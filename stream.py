import queue
import struct
import threading

import pyaudio

from noise_generator import NoiseGenerator
from ring_modulator import RingModulator
from sine_wave_generator import SineWaveGenerator


class Stream:
    def __init__(self,
                 sampling_frequency: int,
                 samples_per_buffer: int,
                 sine_wave_generator: SineWaveGenerator,
                 add_noise: bool,
                 volume: float,
                 multithread_queue: queue.Queue) -> None:
        super().__init__()
        
        # Check arguments.
        if((sampling_frequency is None) or
           (not isinstance(sampling_frequency, int)) or
           (sampling_frequency <= 0) or
           (samples_per_buffer is None) or
           (not isinstance(samples_per_buffer, int)) or
           (samples_per_buffer <= 0) or
           (sine_wave_generator is None) or
           (not isinstance(sine_wave_generator, SineWaveGenerator)) or
           (add_noise is None) or
           (not isinstance(add_noise, bool)) or
           (volume is None) or
           (not isinstance(volume, (int, float))) or
           (volume <= 0) or
           (multithread_queue is None) or
           (not isinstance(multithread_queue, queue.Queue))):
           raise ValueError("ERROR! Invalid arguments!")

        self._pyaudio_object: pyaudio.PyAudio = pyaudio.PyAudio()
        self._format_of_sample = pyaudio.paFloat32
        self._bytes_per_sample: int = pyaudio.get_sample_size(
            self._format_of_sample)
        self._number_of_channels: int = 1
        self._sampling_frequency: int = sampling_frequency
        self._samples_per_buffer: int = samples_per_buffer
        
        self._sine_wave_generator: SineWaveGenerator = sine_wave_generator
        self._add_noise: bool = add_noise
        self._mutex_add_noise: threading.Lock = threading.Lock()
        self._volume: float = volume
        self._mutex_volume: threading.Lock = threading.Lock()

        self._multithread_queue: queue.Queue = multithread_queue

        self._stream: pyaudio.Pyaudio.Stream = self._pyaudio_object.open(
            rate=sampling_frequency,
            channels=self._number_of_channels,
            format=self._format_of_sample,
            input=True,
            output=True,
            frames_per_buffer=samples_per_buffer,
            stream_callback=self._callback)
     
        input_latency_ms: float = self._stream.get_input_latency() * 1000
        output_latency_ms: float = self._stream.get_output_latency() * 1000
        total_latency_ms: float = input_latency_ms + output_latency_ms
        print(f"Input latency = {input_latency_ms} ms")
        print(f"Output latency = {output_latency_ms} ms")
        print(f"Total latency = {total_latency_ms} ms")
    
    def _callback(self,
                  in_data: bytes,
                  frame_count: int,
                  time_info,
                  status_flags):
        # Check arguments.
        if ((status_flags == pyaudio.paInputUnderflow) or
            (status_flags == pyaudio.paInputOverflow) or
            (status_flags == pyaudio.paOutputUnderflow) or
            (status_flags == pyaudio.paOutputOverflow)):
            dummy_bytes: bytes = bytes(frame_count *
                                       self._number_of_channels *
                                       self._bytes_per_sample)
            return (dummy_bytes, pyaudio.paAbort)
        
        i: int = 0
        output_byte_array: bytearray = bytearray()
        while (i + self._bytes_per_sample - 1) <= (len(in_data) - 1):
            # Get input voice point as bytes.
            input_voice_point_bytes: bytes = \
                in_data[i:i + self._bytes_per_sample]
            input_voice_point: float = \
                (struct.unpack("f", input_voice_point_bytes))[0]
          
            # Amplify.
            input_voice_point = input_voice_point * self.volume

            # Get sine wave point.
            sine_wave_point: float = \
                self._sine_wave_generator.get_sine_wave_point()
            
            # Modulate.
            modulated_voice_point: float = RingModulator.modulate(
                input_voice_point=input_voice_point,
                sine_wave_point=sine_wave_point)

            # Add noise optionally.
            if self.add_noise is True:
                noise_point: float = NoiseGenerator.get_noise_point()
                modulated_voice_point = modulated_voice_point + noise_point
   
            # Prevent clipping.
            if modulated_voice_point > 1:
                modulated_voice_point = 1
            elif modulated_voice_point < -1:
                modulated_voice_point = -1

            # Add to output byte array.
            modulated_voice_point_bytes: bytes = \
                struct.pack("f", modulated_voice_point)
            for output_byte in modulated_voice_point_bytes:
                output_byte_array.append(output_byte)

            # Send points to plot.
            points: tuple[float, float, float] = (input_voice_point,
                                                  sine_wave_point,
                                                  modulated_voice_point)
            try:
                self._multithread_queue.put(points, block=False)
            except queue.Full as e:
                pass
            
            # Increment index.
            i = i + self._bytes_per_sample

        output_bytes: bytes = bytes(output_byte_array)
        return (output_bytes, pyaudio.paContinue)
    
    def is_active(self) -> bool:
        return self._stream.is_active()

    def close(self) -> None:
        self._stream.close()
        self._pyaudio_object.terminate()

    @property
    def add_noise(self) -> bool:
        add_noise_copy: bool = True
        with self._mutex_add_noise:
            add_noise_copy = self._add_noise
        return add_noise_copy
    
    @add_noise.setter
    def add_noise(self, new_add_noise: bool) -> None:
        # Check argument.
        if((new_add_noise is None) or
           (not isinstance(new_add_noise, bool))):
            raise ValueError("ERROR! Invalid argument!")

        with self._mutex_add_noise:
            self._add_noise = new_add_noise

    @property
    def volume(self) -> float:
        volume_copy: float = 0
        with self._mutex_volume:
            volume_copy = self._volume
        return volume_copy

    @volume.setter
    def volume(self, new_volume: float) -> None:
        # Check argument.
        if((new_volume is None) or
           (not isinstance(new_volume, (int, float))) or
           (new_volume <= 0)):
            raise ValueError("ERROR! Invalid argument!")

        with self._mutex_volume:
            self._volume = new_volume
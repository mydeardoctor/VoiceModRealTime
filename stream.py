import queue
import struct
import threading
from typing import Any

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
                 volume: int | float,
                 multithread_queue: queue.Queue[tuple[float, float, float]]) \
                    -> None:
        super().__init__()
        """Start pyaudio input/output stream.

        Raises:
            ValueError: invalid arguments.
        """
        # Check arguments.
        if((not isinstance(sampling_frequency, int)) or
           (sampling_frequency <= 0) or
           (not isinstance(samples_per_buffer, int)) or
           (samples_per_buffer <= 0) or
           (not isinstance(sine_wave_generator, SineWaveGenerator)) or
           (not isinstance(add_noise, bool)) or
           (not isinstance(volume, (int, float))) or
           (volume <= 0) or
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

        self._multithread_queue: queue.Queue[tuple[float, float, float]] = \
            multithread_queue

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
                  time_info: Any,
                  status_flags: Any):
        """Pyaudio input/output stream callback.

        Get input voice from a microphone,
        modulate it by a sine wave
        and output modulated voice to a speaker.
        Send input voice, sine wave and modulated voice samples to
        a multithread queue for later plotting.

        Args:
            in_data (bytes): raw bytes of input voice data.
            frame_count (int): number of input voice float samples.
            time_info (Any): time information.
            status_flags (Any): portAutio callback flag.

        Returns:
            _type_: raw bytes of modulated voice data,
            portAudio callback return code.
        """
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
            except queue.Full:
                pass
            
            # Increment index.
            i = i + self._bytes_per_sample

        output_bytes: bytes = bytes(output_byte_array)
        return (output_bytes, pyaudio.paContinue)
    
    def is_active(self) -> bool:
        """Return a flag that specifies whether pyaudio stream is active.

        Returns:
            bool: True - pyaudio input/output stream is active.
            False - pyaudio input/output stream is not active.
        """
        return self._stream.is_active()

    def close(self) -> None:
        """Close pyaudio input/output stream."""
        self._stream.close()
        self._pyaudio_object.terminate()

    @property
    def add_noise(self) -> bool:
        """Return current "add noise" parameter.

        Returns:
            bool: current "add noise" parameter.
        """
        add_noise_copy: bool = True
        with self._mutex_add_noise:
            add_noise_copy = self._add_noise
        return add_noise_copy
    
    @add_noise.setter
    def add_noise(self, new_add_noise: bool) -> None:
        """Check and set new "add noise" parameter.

        Args:
            new_add_noise (bool): new "add noise" parameter.

        Raises:
            ValueError: invalid argument.
        """
        # Check argument.
        if((not isinstance(new_add_noise, bool))):
            raise ValueError("ERROR! Invalid argument!")

        with self._mutex_add_noise:
            self._add_noise = new_add_noise

    @property
    def volume(self) -> float:
        """Return volume.

        Returns:
            float: volume.
        """
        volume_copy: float = 0
        with self._mutex_volume:
            volume_copy = self._volume
        return volume_copy

    @volume.setter
    def volume(self, new_volume: int | float) -> None:
        """Check and set new volume.

        Args:
            new_volume (int | float): new volume.

        Raises:
            ValueError: invalid argument.
        """
        # Check argument.
        if((not isinstance(new_volume, (int, float))) or
           (new_volume <= 0)):
            raise ValueError("ERROR! Invalid argument!")

        with self._mutex_volume:
            self._volume = new_volume
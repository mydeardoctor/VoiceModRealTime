import queue
import struct

import matplotlib
import matplotlib.pyplot as plt
import pyaudio

from noise_generator import NoiseGenerator
from ring_modulator import RingModulator
from sine_wave_generator import SineWaveGenerator


class Stream:
    def __init__(self,
                 pyaudio_object: pyaudio.PyAudio,
                 format_of_sample,
                 number_of_channels: int,
                 samples_per_buffer: int,
                 sampling_frequency: int,
                 sine_wave_generator: SineWaveGenerator,
                 noise_generator: NoiseGenerator,
                 add_noise: bool) -> None:
        super().__init__()

        # Check arguments.
        if ((number_of_channels <= 0) or
            # (samples_per_buffer <= 0) or
            (sampling_frequency <= 0)):
            raise ValueError("Arguments must be > 0.")

        self._pyaudio_object = pyaudio_object
        self._format_of_sample = format_of_sample
        self._bytes_per_sample = pyaudio.get_sample_size(self._format_of_sample)
        self._number_of_channels: int = number_of_channels
        self._samples_per_buffer: int = samples_per_buffer
        self._sampling_frequency: int = sampling_frequency
        self._sine_wave_generator: SineWaveGenerator = sine_wave_generator
        self._noise_generator: NoiseGenerator = noise_generator
        self._add_noise: bool = add_noise
        self._file = open("text.txt", "w") #TODO

        self._stream: pyaudio.PyAudio.Stream = self._pyaudio_object.open(
            input=True,
            output=True,
            rate=sampling_frequency,
            format=format_of_sample,
            channels=number_of_channels,
            frames_per_buffer=samples_per_buffer,
            stream_callback=self._callback)
        # TODO
        print(f"input latency = {self._stream.get_input_latency()}")
        print(f"output latency = {self._stream.get_output_latency()}")
    
    def _callback(self,
                  in_data: bytes,
                  frame_count: int,
                  time_info,
                  status):
        # Check arguments.
        if ((status == pyaudio.paInputUnderflow) or
            (status == pyaudio.paInputOverflow) or
            (status == pyaudio.paOutputUnderflow) or
            (status == pyaudio.paOutputOverflow)):
            dummy_bytes: bytes = bytes(frame_count *
                                       self._number_of_channels *
                                       self._bytes_per_sample)
            return (dummy_bytes, pyaudio.paAbort)
        
        i = 0
        output_byte_array: bytearray = bytearray()
        while (i + self._bytes_per_sample - 1) <= (len(in_data) - 1):
            # Get sample.
            input_bytes: bytes = in_data[i:i + self._bytes_per_sample]
            input_float: float = (struct.unpack("f", input_bytes))[0] * 5 #TODO
          
            self._file.write(f"{input_float}\n") #TODO

            # Get sine wave point.
            sine_wave_point: float = \
                self._sine_wave_generator.get_sine_wave_point()
            
            self._file.write(f"{sine_wave_point}\n") #TODO

            # Modulate.
            modulated_output: float = RingModulator.modulate(
                input_signal_point=input_float,
                sine_wave_point=sine_wave_point) #TODO

            self._file.write(f"{modulated_output}\n") #TODO

            # Add noise.
            modulated_output_with_noise: float = 0.0
            if self._add_noise is True:
                noise_point: float = self._noise_generator.get_noise_point()
                modulated_output_with_noise = modulated_output + noise_point
            else:
                modulated_output_with_noise = modulated_output

            # Add to output.
            output_bytes: bytes = struct.pack("f", modulated_output_with_noise)
            for output_byte in output_bytes:
                output_byte_array.append(output_byte)

            # Increment index.
            i = i + self._bytes_per_sample

        total_output_bytes: bytes = bytes(output_byte_array)
        return (total_output_bytes, pyaudio.paContinue)
    
    # TODO is_active
    def is_active(self) -> bool:
        return self._stream.is_active()

    def close(self) -> None:
        self._stream.close()
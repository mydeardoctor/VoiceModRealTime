import argparse
import collections
import queue
import struct
import time

import matplotlib
import matplotlib.pyplot as plt
import pyaudio

from noise_generator import NoiseGenerator
from ring_modulator import RingModulator
from sine_wave_generator import SineWaveGenerator
from stream import Stream


# TODO
# Громкость выше
# чеклист написания программы любой
# автодокументация в питоне. докстринги.
# тесты в питоне. юнит тесты.
# проверка статической типизации в питоне

# TODO chek arguments for None
# TODO громкость!!!!!!

# TODO размер буфера
# TODO get latency
# TODO run as root
# TODO https://www.portaudio.com/docs/latency.html
# TODO написать portaudio на C++

# TODO рефакторинг
# TODO убрать matplotlib
# TODO exceptions при принятии аргументов
# TODO limit amplitude to 1
# TODO sine wave amplitude!!!!!!!!! Чем больше амплитуда синусоиды, тем сильнее модуляция? но я не могу увеличить синусоиду, зато могу увеличить сигнал? Нормалайз сигнал по громкости. Moving average.
# TODO float output range? -1 1? PCM float.
# TODO другая частота модуляции
# TODO requirements.txt
# TODO git

# TODO run at startup
# TODO power saving raspi
# TODO подключиться к распберри по телефону
# TODO cli interface. громкость, частота модуляции

# TODO main thread ждёт частоту, громкость. мьютексы

# TODO float range
# TODO может ли другой телефон выходить в инет при точке доступа
# TODO docstring. document exceptions raised
def main():
    # TODO parser
    parser = argparse.ArgumentParser(prog="PROGRAM_NAME",
                                     description="DESCRIPTION",
                                     epilog="EPILOG")
    parser.add_argument("-f", "--frequency", action="store", metavar="FREQ", default=48000, help="HELP FREQ", required=False)
    parser.add_argument("-n", "--noise", action="store_false", default=True, help="NOISE OFF", required=False)
    namespace: argparse.Namespace = parser.parse_args() #Exception
    print(namespace)

    SAMPLING_FREQUENCY: int = 48000
    SINE_WAVE_FREQUENCY: int = 220#TODO 230 240 
    FORMAT_OF_SAMPLE = pyaudio.paFloat32
    NUMBER_OF_CHANNELS: int = 1
    SAMPLES_PER_BUFFER: int = 1024 #TODO set to zero
    ADD_NOISE: bool = True
    NOISE_DIVIDER: int = 100000

    sine_wave_generator: SineWaveGenerator = SineWaveGenerator(
        sampling_frequency=SAMPLING_FREQUENCY,
        sine_wave_frequency=SINE_WAVE_FREQUENCY)
    # sine_wave_generator.plot_sine_wave(time_s=1/SINE_WAVE_FREQUENCY)

    noise_generator: NoiseGenerator = NoiseGenerator(divider=NOISE_DIVIDER)

    multithread_queue: queue.Queue = queue.Queue(maxsize=SAMPLES_PER_BUFFER*4*10) #TODO

    pyaudio_object: pyaudio.PyAudio = pyaudio.PyAudio()
    stream: Stream = Stream(
        pyaudio_object=pyaudio_object,
        format_of_sample = FORMAT_OF_SAMPLE,
        number_of_channels = NUMBER_OF_CHANNELS,
        samples_per_buffer=SAMPLES_PER_BUFFER,
        sampling_frequency = SAMPLING_FREQUENCY,
        sine_wave_generator=sine_wave_generator,
        noise_generator=noise_generator,
        add_noise=ADD_NOISE)
 
    # Main thread.
    #TODO
    state = 0
    try:
        while stream.is_active() is True:
            match state:
                case 0:
                    print("To change volume enter 1.")
                    print("To change sine wave frequency enter 2.")
                    print("Enter: ")
                    line: str = input()
                    line_int: int = int(line)
                    if line_int == 1:
                        state = 1
                    elif line_int == 2:
                        state = 2
                    else:
                        print("INVALID NUMBER.")
                        state = 0
                case 1:
                    print("Enter new volume.")
                    print("Enter 0 to return.")
                    print("Enter: ")
                    line: str = input()
                    line_int: int = int(line)
                    if line_int != 0:
                        print("accepted")
                        state = 0
                    else:
                        state = 0
                case 2:
                    print("Enter new sine wave frequency.")
                    print("Enter 0 to return.")
                    print("Enter: ")
                    line: str = input()
                    line_int: int = int(line)
                    if line_int != 0:
                        sine_wave_generator.set_sine_wave_frequency(line_int) #TODO MUTEX
                        print("accepted")
                        state = 0
                    else:
                        state = 0

            time.sleep(0.1)

    except BaseException as e:
        print(type(e))
        print(e)
        print("Stopping main thread!")

    finally:
        stream.close()
        pyaudio_object.terminate() # TODO перенести в stream


if __name__ == "__main__":
    main()
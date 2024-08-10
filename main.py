import argparse
import collections
import json
import queue
import struct
import time
import threading

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
# from networkx import volume
import numpy as np
import pyaudio

from noise_generator import NoiseGenerator
from ring_modulator import RingModulator
from sine_wave_generator import SineWaveGenerator
from stream import Stream
from parameters import Parameters
from plot import Plot


# TODO
# Нарисовать графики.

# Check arguments for None. Exceptions.
# Limit amplitude to 1.
# Размер буфера, latency. https://www.portaudio.com/docs/latency.html
# убрать matplotlib для raspberry
# requirements.txt

# cli interface. громкость, частота модуляции
# main thread ждёт частоту, громкость. мьютексы
# Громкость выше.

# raspberry не вывозит, убрать всё лишнее, квантизировать. не считать синусоиду. pyaudio через callbacks
# Рефакторинг.
# Docstrings for modules, classes, functions. PEP257. Document exceptions raised

# Подобрать частоту модуляции.
# подключиться к распберри по телефону

# README.md


# ГРОМКОСТЬ:
# Без модуляции звук такой же громкости, как и виндоусовский диктофон. Но в каком диапазоне аудио? Построить в матплотлибе, чтобы узнать диапазон.ГРОМКОСТЬ
# Почему модуляция тише? Построить матплотлибе. Потому что модулирующая синусоида часто равна нулю


# Implement volume change menu
# Подписать графики
# подобрать частоту синусоиды
# добавить в меню add_noise


index = 0

def main():
    parameters: Parameters = Parameters()
    
    sine_wave_generator: SineWaveGenerator = SineWaveGenerator(
        sampling_frequency=parameters.sampling_frequency,
        sine_wave_frequency=parameters.sine_wave_frequency)

    multithread_queue_samples: int = parameters.samples_per_buffer * 4
    multithread_queue: queue.Queue = queue.Queue(
        maxsize=multithread_queue_samples)

    stream: Stream = Stream(
        samples_per_buffer=parameters.samples_per_buffer,
        sampling_frequency = parameters.sampling_frequency,
        sine_wave_generator=sine_wave_generator,
        add_noise=parameters.add_noise,
        multithread_queue = multithread_queue,
        volume=parameters.volume)
    
    plot: Plot = Plot(sampling_frequency=parameters.sampling_frequency,
                      samples_per_buffer=parameters.samples_per_buffer,
                      multithread_queue=multithread_queue)

    # Main thread.
       
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
                    #TODO сделать тут обработку эксепшнов когда я ввожу строку или говно. и в остальных местах в меню
                    line_float: float = float(line)
                    if line_float != 0:
                        stream.set_volume(new_volume=line_float)
                        print("accepted")
                        state = 0

                        # TODO ОГРАНИЧЕНИЯ
                        parameters["volume"] = line_float
                        with open("config.json", "w") as config_file:
                            json.dump(parameters, config_file, indent=4)
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

                        # TODO ОГРАНИЧЕНИЯ
                        parameters["frequency"] = line_int
                        with open("config.json", "w") as config_file:
                            json.dump(parameters, config_file, indent=4)
                    else:
                        state = 0

            time.sleep(0.1)

    except BaseException as e:
        print(type(e))
        print(e)
        print("Stopping main thread!")

    finally:
        stream.close()
        plot.close()


if __name__ == "__main__":
    main()
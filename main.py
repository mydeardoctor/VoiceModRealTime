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

    # TODO
    SAMPLING_FREQUENCY: int = 48000
    SAMPLES_PER_BUFFER: int = 1024 #20ms
    UPDATE_INTERVAL_SAMPLES: int = SAMPLES_PER_BUFFER * 2
    UPDATE_INTERVAL_TIME_S = 1/SAMPLING_FREQUENCY * UPDATE_INTERVAL_SAMPLES
    UPDATE_INTERVAL_TIME_MS = UPDATE_INTERVAL_TIME_S * 1000
    PLOT_TIME_WINDOW_SAMPLES = UPDATE_INTERVAL_SAMPLES * 1
    MULTITHREAD_QUEUE_SAMPLES: int = PLOT_TIME_WINDOW_SAMPLES * 2


    sine_wave_generator: SineWaveGenerator = SineWaveGenerator(
        sampling_frequency=SAMPLING_FREQUENCY,
        sine_wave_frequency=parameters.frequency)


    # multithread_queue: queue.Queue = queue.Queue(maxsize=SAMPLES_PER_BUFFER*4*40) #TODO
    multithread_queue1: queue.Queue = queue.Queue(maxsize=MULTITHREAD_QUEUE_SAMPLES)
    multithread_queue2: queue.Queue = queue.Queue(maxsize=MULTITHREAD_QUEUE_SAMPLES)
    multithread_queue3: queue.Queue = queue.Queue(maxsize=MULTITHREAD_QUEUE_SAMPLES)

    stream: Stream = Stream(
        samples_per_buffer=SAMPLES_PER_BUFFER,
        sampling_frequency = SAMPLING_FREQUENCY,
        sine_wave_generator=sine_wave_generator,
        add_noise=parameters.add_noise,
        multithread_queue1=multithread_queue1,
        multithread_queue2=multithread_queue2,
        multithread_queue3=multithread_queue3,
        volume=parameters.volume)
    

    # matplotlib
    # Create the figure and axes for plotting
    fig, ax = plt.subplots()
    x = np.arange(0, PLOT_TIME_WINDOW_SAMPLES)
    line1, = ax.plot(x, [0]*PLOT_TIME_WINDOW_SAMPLES)
    line2, = ax.plot(x, [0]*PLOT_TIME_WINDOW_SAMPLES)
    line3, = ax.plot(x, [0]*PLOT_TIME_WINDOW_SAMPLES)
    ax.set_ylim(-1, 1)  # Set y-axis limits to fit float32 audio data
    # ax[1].set_ylim(-1, 1)  # Set y-axis limits to fit float32 audio data
    # ax[2].set_ylim(-1, 1)  # Set y-axis limits to fit float32 audio data
    # Create animation
    input_circular_buffer = collections.deque([0]*PLOT_TIME_WINDOW_SAMPLES, maxlen=PLOT_TIME_WINDOW_SAMPLES)
    sine_circular_buffer = collections.deque([0]*PLOT_TIME_WINDOW_SAMPLES, maxlen=PLOT_TIME_WINDOW_SAMPLES)
    output_circular_buffer = collections.deque([0]*PLOT_TIME_WINDOW_SAMPLES, maxlen=PLOT_TIME_WINDOW_SAMPLES)


    def update_plot(frame):
        for _ in range(0, UPDATE_INTERVAL_SAMPLES, 1):
            try:
                input_point = multithread_queue1.get(block=True)
            except BaseException as e:
                input_point = 0
            try:
                sine_point = multithread_queue2.get(block=True)
            except BaseException as e:
                sine_point = 0
            try:
                output_point = multithread_queue3.get(block=True)
            except BaseException as e:
                output_point = 0

            input_circular_buffer.popleft()
            sine_circular_buffer.popleft()
            output_circular_buffer.popleft()

            input_circular_buffer.append(input_point)
            sine_circular_buffer.append(sine_point)
            output_circular_buffer.append(output_point)

        line1.set_ydata(input_circular_buffer)
        line2.set_ydata(sine_circular_buffer)
        line3.set_ydata(output_circular_buffer)
        return line1, line2, line3
    
    ani = animation.FuncAnimation(fig, update_plot, blit=True, interval=UPDATE_INTERVAL_TIME_MS)
    plt.show(block=False)

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


if __name__ == "__main__":
    main()
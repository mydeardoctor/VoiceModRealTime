import argparse
import collections
import queue
import struct
import time
import threading

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import pyaudio

from noise_generator import NoiseGenerator
from ring_modulator import RingModulator
from sine_wave_generator import SineWaveGenerator
from stream import Stream


# TODO
# Нарисовать графики.

# Check arguments for None. Exceptions.
# Limit amplitude to 1.
# Размер буфера, latency. https://www.portaudio.com/docs/latency.html
# убрать matplotlib
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
# Почему модуляция тише? Построить матплотлибе.


# Implement volume change menu




def main():
    # TODO parser
    # parser = argparse.ArgumentParser(prog="PROGRAM_NAME",
    #                                  description="DESCRIPTION",
    #                                  epilog="EPILOG")
    # parser.add_argument("-f", "--frequency", action="store", metavar="FREQ", default=48000, help="HELP FREQ", required=False)
    # parser.add_argument("-n", "--noise", action="store_false", default=True, help="NOISE OFF", required=False)
    # namespace: argparse.Namespace = parser.parse_args() #Exception
    # print(namespace)



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

    multithread_queue: queue.Queue = queue.Queue(maxsize=SAMPLES_PER_BUFFER*4*40) #TODO
    multithread_queue1: queue.Queue = queue.Queue(maxsize=SAMPLES_PER_BUFFER*4*40)
    multithread_queue2: queue.Queue = queue.Queue(maxsize=SAMPLES_PER_BUFFER*4*40)
    multithread_queue3: queue.Queue = queue.Queue(maxsize=SAMPLES_PER_BUFFER*4*40)

    pyaudio_object: pyaudio.PyAudio = pyaudio.PyAudio()
    stream: Stream = Stream(
        pyaudio_object=pyaudio_object,
        format_of_sample = FORMAT_OF_SAMPLE,
        number_of_channels = NUMBER_OF_CHANNELS,
        samples_per_buffer=SAMPLES_PER_BUFFER,
        sampling_frequency = SAMPLING_FREQUENCY,
        sine_wave_generator=sine_wave_generator,
        noise_generator=noise_generator,
        add_noise=ADD_NOISE,
        multithread_queue1=multithread_queue1,
        multithread_queue2=multithread_queue2,
        multithread_queue3=multithread_queue3)
    

    # matplotlib
    # Create the figure and axes for plotting
    fig, ax = plt.subplots()
    x = np.arange(0, SAMPLES_PER_BUFFER*4)
    line1, = ax.plot(x, np.random.rand(SAMPLES_PER_BUFFER*4))
    line2, = ax.plot(x, np.random.rand(SAMPLES_PER_BUFFER*4))
    line3, = ax.plot(x, np.random.rand(SAMPLES_PER_BUFFER*4))
    ax.set_ylim(-1, 1)  # Set y-axis limits to fit float32 audio data
    # ax[1].set_ylim(-1, 1)  # Set y-axis limits to fit float32 audio data
    # ax[2].set_ylim(-1, 1)  # Set y-axis limits to fit float32 audio data
    # Create animation
    def update_plot(frame):
        data_input = []
        data_sine = []
        data_modulated = []
        for i in range(0, SAMPLES_PER_BUFFER*4, 1):
            try:
                data_input_point = multithread_queue1.get(block=True)
            except BaseException as e:
                data_input_point = 0
            finally:
                data_input.append(data_input_point)
            try:
                data_sine_point = multithread_queue2.get(block=True)
            except BaseException as e:
                data_sine_point = 0
            finally:
                data_sine.append(data_sine_point)
            try:
                data_modulated_point = multithread_queue3.get(block=True)
            except BaseException as e:
                data_modulated_point = 0
            finally:
                data_modulated.append(data_modulated_point)

        line1.set_ydata(data_input)
        line2.set_ydata(data_sine)
        line3.set_ydata(data_modulated)
        return line1, line2, line3
    ani = animation.FuncAnimation(fig, update_plot, blit=True, interval=(1/SAMPLING_FREQUENCY)*SAMPLES_PER_BUFFER*4)
    plt.show(block=False)

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
                    #TODO сделать тут обработку эксепшнов когда я ввожу строку или говно. и в остальных местах в меню
                    line_float: float = float(line)
                    if line_float != 0:
                        stream.set_volume(new_volume=line_float)
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
        pyaudio_object.terminate() # TODO перенести в stream. см KWS


if __name__ == "__main__":
    main()
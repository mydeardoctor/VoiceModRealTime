import queue

from menu_state import MenuState
from parameters import Parameters
from plot import Plot
from sine_wave_generator import SineWaveGenerator
from stream import Stream


# TODO
# TODOs
# Problems

# pylance
# Docstrings for modules, classes, functions. PEP257. Document exceptions raised

# Размер буфера, latency. https://www.portaudio.com/docs/latency.html. На распберри запускать от root, чтобы latency была меньше. You must also set PA_MIN_LATENCY_MSEC using the appropriate command for your shell.
# https://github.com/PortAudio/portaudio/wiki/Platforms_RaspberryPi
# raspberry убрать matplotlib
# подключиться к распберри по телефону

# подобрать частоту синусоиды

# README.md
# requirements.txt
# gitignore


def main():
    parameters: Parameters = Parameters()
    
    sine_wave_generator: SineWaveGenerator = SineWaveGenerator(
        sampling_frequency=parameters.sampling_frequency,
        sine_wave_frequency=parameters.sine_wave_frequency)

    multithread_queue_samples: int = parameters.samples_per_buffer * 4
    multithread_queue: queue.Queue = queue.Queue(
        maxsize=multithread_queue_samples)

    plot: Plot = Plot(sampling_frequency=parameters.sampling_frequency,
                      samples_per_buffer=parameters.samples_per_buffer,
                      multithread_queue=multithread_queue)

    stream: Stream = Stream(sampling_frequency=parameters.sampling_frequency,
                            samples_per_buffer=parameters.samples_per_buffer,
                            sine_wave_generator=sine_wave_generator,
                            add_noise=parameters.add_noise,
                            volume=parameters.volume,
                            multithread_queue=multithread_queue)
    
    # Main thread.
    menu_state: MenuState = MenuState.MAIN
    try:
        while stream.is_active() is True:          
            match menu_state:
                case MenuState.MAIN:
                    print("Enter 1 to change sine wave frequency.")
                    print("Enter 2 to add or remove noise.")
                    print("Enter 3 to change volume.")
                    print("Enter 4 to exit. ")
                    line: str = input()

                    number: int = 0
                    try:
                        number = int(line)
                    except ValueError as e:
                        number = 0

                    match number:
                        case 1:
                            menu_state = MenuState.CHANGING_SINE_WAVE_FREQUENCY
                        case 2:
                            menu_state = MenuState.CHANGING_NOISE
                        case 3:
                            menu_state = MenuState.CHANGING_VOLUME
                        case 4:
                            break
                        case _:
                            print("ERROR! Invalid number!")
                            menu_state = MenuState.MAIN

                case MenuState.CHANGING_SINE_WAVE_FREQUENCY:
                    print("Enter new sine wave frequency: ", end="")
                    line: str = input()
                    
                    new_sine_wave_frequency: int = 0
                    try:
                        new_sine_wave_frequency = int(line)
                    except ValueError as e:
                        new_sine_wave_frequency = 0

                    parameters.sine_wave_frequency = new_sine_wave_frequency
                    sine_wave_generator.sine_wave_frequency = \
                        parameters.sine_wave_frequency
                    
                    menu_state = MenuState.MAIN

                case MenuState.CHANGING_NOISE:
                    print("Enter \"true\" to add noise. "
                          "Enter \"false\" to remove noise: ", end="")
                    line: str = input()

                    new_add_noise = None
                    if ((line == "true") or (line == "True")):
                        new_add_noise = True
                    elif ((line == "false") or (line == "False")):
                        new_add_noise = False

                    parameters.add_noise = new_add_noise
                    stream.add_noise = parameters.add_noise

                    menu_state = MenuState.MAIN

                case MenuState.CHANGING_VOLUME:
                    print("Enter new volume: ", end="")
                    line: str = input()
                    
                    new_volume: float = 0
                    try:
                        new_volume = float(line)
                    except ValueError as e:
                        new_volume = 0
                    
                    parameters.volume = new_volume
                    stream.volume = parameters.volume

                    menu_state = MenuState.MAIN

                case _:
                    menu_state = MenuState.MAIN

    except BaseException as e:
        print(type(e))
        print(e)
        print("Stopping main thread.")

    finally:
        plot.close()
        stream.close()
        

if __name__ == "__main__":
    main()
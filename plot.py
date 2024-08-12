import collections
from concurrent.futures import thread
import queue
import threading

import matplotlib
import matplotlib.animation
import matplotlib.pyplot as plt


# pause with lock


class Plot:
    def __init__(self,
                 sampling_frequency: int,
                 samples_per_buffer: int,
                 multithread_queue: queue.Queue) -> None:
        super().__init__()
        
        # TODO Check parameters
        self._samples_per_update_interval: int = samples_per_buffer
        sample_time_s: float = 1 / sampling_frequency
        update_interval_time_ms: int = (sample_time_s * self._samples_per_update_interval * 1000)

        self._multithread_queue: queue.Queue = multithread_queue

        # TODO подписи
        self._figure: matplotlib.figure.Figure = plt.figure()
        self._axes: matplotlib.axes.Axes = self._figure.add_subplot()
        self._axes.set_xlim(left=0, right=self._samples_per_update_interval - 1)
        self._axes.set_ylim(bottom=-1, top=1)
        self._axes.set_title(label="Audio signals")
        self._axes.set_xlabel(xlabel="Points")
        self._axes.set_ylabel(ylabel="Float value")    

        x = [i for i in range(0, self._samples_per_update_interval, 1)]
        y = [0] * self._samples_per_update_interval

        self._input_voice_line: matplotlib.lines.Line2D
        self._sine_wave_line: matplotlib.lines.Line2D
        self._modulated_voice_line: matplotlib.lines.Line2D

        self._input_voice_line, *other_lines = self._axes.plot([], [], label="Input voice")
        self._sine_wave_line, *other_lines = self._axes.plot([], [], label="Sine wave")
        self._modulated_voice_line, *other_lines = self._axes.plot([], [], label="Modulated voice")
        self._axes.legend(loc="lower left")

        self._mutex_running: threading.Lock = threading.Lock()
        self._running: bool = True

        self._anim: matplotlib.animation.FuncAnimation = matplotlib.animation.FuncAnimation(
            fig=self._figure,
            func=self._update,
            frames=self._get_frame,
            init_func=self._init_animation,
            interval=update_interval_time_ms,
            repeat=False,
            cache_frame_data=False)
        plt.show(block=False)

    # TODO how to stop animation and this infinite generator
    def _init_animation(self):
        x = [i for i in range(0, self._samples_per_update_interval, 1)]
        y = [0] * self._samples_per_update_interval

        self._input_voice_line.set_data(x, y)
        self._sine_wave_line.set_data(x, y)
        self._modulated_voice_line.set_data(x, y)

        return [self._input_voice_line,
                self._sine_wave_line,
                self._modulated_voice_line]

    def _get_frame(self):
        in1_buf: list[float] = []
        in2_buf: list[float] = []
        in3_buf: list[float] = []


        while True:
            running_copy: bool = self.running
            
            if running_copy is True:
                in1_buf.clear()
                in2_buf.clear()
                in3_buf.clear()
                for _ in range(0, self._samples_per_update_interval, 1):
                    in1: float = 0
                    in2: float = 0
                    in3: float = 0
                    # try
                    in1, in2, in3 = self._multithread_queue.get(block=True)
                    # base exception
                    in1_buf.append(in1)
                    in2_buf.append(in2)
                    in3_buf.append(in3)
                in1_buf_copy: list[float] = in1_buf.copy()
                in2_buf_copy: list[float] = in2_buf.copy()
                in3_buf_copy: list[float] = in3_buf.copy()
                yield (in1_buf_copy, in2_buf_copy, in3_buf_copy)
                
            else:
                break

    def _update(self,
                frame,
                *fargs):
        input_voice_buffer: list[float] = []
        sine_wave_buffer: list[float] = []
        modulated_voice_buffer: list[float] = []

        input_voice_buffer, sine_wave_buffer, modulated_voice_buffer = frame
        
        self._input_voice_line.set_ydata(input_voice_buffer)
        self._sine_wave_line.set_ydata(sine_wave_buffer)
        self._modulated_voice_line.set_ydata(modulated_voice_buffer)

        return self._input_voice_line, self._sine_wave_line, self._modulated_voice_line

    @property
    def running(self) -> bool:
        running_copy: bool = True
        with self._mutex_running:
            running_copy = self._running
        return running_copy

    @running.setter
    def running(self, new_running: bool) -> None:
        with self._mutex_running:
            self._running = new_running
    
    def close(self) -> None:
        self.running = False
        self._anim.pause()
        plt.close(fig=self._figure)
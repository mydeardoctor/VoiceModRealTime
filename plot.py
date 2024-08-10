import collections
import queue

import matplotlib
import matplotlib.pyplot as plt


class Plot:
    def __init__(self,
                 sampling_frequency: int,
                 samples_per_buffer: int,
                 multithread_queue: queue.Queue) -> None:
        super().__init__()
        
        # TODO Check parameters
        sample_time_s: float = 1 / sampling_frequency
        self._samples_per_update_interval: int = samples_per_buffer * 2
        update_interval_time_s: float = (sample_time_s
                                        * self._samples_per_update_interval)
        update_interval_time_ms: int = int(update_interval_time_s * 1000)

        self._multithread_queue: queue.Queue = multithread_queue

        # TODO подписи
        self._figure: matplotlib.figure.Figure = plt.figure()
        self._axes: matplotlib.axes.Axes = self._figure.add_subplot()
        self._axes.set_ylim(bottom=-1, top=1)

        x = range(0, self._samples_per_update_interval, 1)
        y = [0] * self._samples_per_update_interval

        self._input_voice_line: matplotlib.lines.Line2D
        self._sine_wave_line: matplotlib.lines.Line2D
        self._modulated_voice_line: matplotlib.lines.Line2D

        # TODO?
        self._input_voice_line, *other_lines = self._axes.plot(x, y)
        self._sine_wave_line, *other_lines = self._axes.plot(x, y)
        self._modulated_voice_line, *other_lines = self._axes.plot(x, y)
        
        self._anim: matplotlib.animation.FuncAnimation = matplotlib.animation.FuncAnimation(
            fig=self._figure,
            func=self._update,
            frames=self._get_frame,
            interval=update_interval_time_ms)
        plt.show(block=False)

    # TODO init
    # TODO how to stop animation and this infinite generator
    def _get_frame(self):
        in1_buf: list[float] = []
        in2_buf: list[float] = []
        in3_buf: list[float] = []
        while True:
            in1_buf.clear()
            in2_buf.clear()
            in3_buf.clear()
            for _ in range(0, 2048, 1):
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

    def close(self) -> None:
        plt.close(fig=self._figure)
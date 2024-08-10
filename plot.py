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

        self._input_voice_line, *other_lines = self._axes.plot(x, y)
        self._sine_wave_line, *other_lines = self._axes.plot(x, y)
        self._modulated_voice_line, *other_lines = self._axes.plot(x, y)
        
        self._anim: matplotlib.animation.FuncAnimation = matplotlib.animation.FuncAnimation(
            fig=self._figure,
            func=self._update,
            interval=update_interval_time_ms)
        plt.show(block=False)

    # TODO whats the point of arguments?
    def _update(self,
                frame,
                *fargs):
        input_buffer = []
        sine_buffer = []
        output_buffer = []

        for _ in range(0, self._samples_per_update_interval, 1):
            try:
                t = self._multithread_queue.get(block=True) #TODO?
                input_point, sine_point, output_point = t
            except BaseException as e:
                input_point = 0
                sine_point = 0
                output_point = 0
            input_buffer.append(input_point)
            sine_buffer.append(sine_point)
            output_buffer.append(output_point)
                 
        self._input_voice_line.set_ydata(input_buffer)
        self._sine_wave_line.set_ydata(sine_buffer)
        self._modulated_voice_line.set_ydata(output_buffer)
        return self._input_voice_line, self._sine_wave_line, self._modulated_voice_line
    


    def close(self) -> None:
        plt.close(fig=self._figure)
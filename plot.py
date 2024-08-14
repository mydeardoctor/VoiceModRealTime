import queue
import threading
from typing import Any

import matplotlib.animation
import matplotlib.axes
import matplotlib.figure
import matplotlib.lines
import matplotlib.pyplot as plt


class Plot:
    def __init__(self,
                 sampling_frequency: int,
                 samples_per_buffer: int,
                 multithread_queue: queue.Queue[tuple[float, float, float]]) \
                    -> None:
        """Start plotting input voice, sine wave and modulated voice.

        Raises:
            ValueError: invalid arguments.
        """
        super().__init__()
        
        # Check arguments.
        if((not isinstance(sampling_frequency, int)) or
           (sampling_frequency <= 0) or
           (not isinstance(samples_per_buffer, int)) or
           (samples_per_buffer <= 0) or
           (not isinstance(multithread_queue, queue.Queue))):
            raise ValueError("ERROR! Invalid arguments!")

        self._samples_per_update_interval: int = samples_per_buffer
        sample_time_ms: float = 1 / sampling_frequency * 1000
        self._update_interval_ms: int = int(sample_time_ms
                                            * self._samples_per_update_interval)

        self._multithread_queue: queue.Queue[tuple[float, float, float]] = \
            multithread_queue

        self._figure: matplotlib.figure.Figure = plt.figure()
        self._axes: matplotlib.axes.Axes = self._figure.add_subplot()

        self._input_voice_line: matplotlib.lines.Line2D
        self._sine_wave_line: matplotlib.lines.Line2D
        self._modulated_voice_line: matplotlib.lines.Line2D
        self._input_voice_line, *other_lines = self._axes.plot(
            [], [], label="Input voice")
        self._sine_wave_line, *other_lines = self._axes.plot(
            [], [], label="Sine wave")
        self._modulated_voice_line, *other_lines = self._axes.plot(
            [], [], label="Modulated voice")
        
        self._axes.set_xlim(left=0, right=self._samples_per_update_interval - 1)
        self._axes.set_ylim(bottom=-1, top=1)
        self._axes.set_title(label="Audio signals")
        self._axes.set_xlabel(xlabel="Points")
        self._axes.set_ylabel(ylabel="Float value")  
        self._axes.legend(loc="lower left")

        self._running: bool = True
        self._mutex_running: threading.Lock = threading.Lock()

        self._animation: matplotlib.animation.FuncAnimation = \
            matplotlib.animation.FuncAnimation(
                fig=self._figure,
                func=self._update_animation,
                frames=self._get_frame_for_animation,
                init_func=self._init_animation,
                interval=self._update_interval_ms,
                repeat=False,
                cache_frame_data=False)
        plt.show(block=False)

    def _init_animation(self):
        """Initialize a clear frame.

        Returns:
            _type_: line to draw input voice,
            line to draw sine wave,
            line to draw modulated voice.
        """
        x = [i for i in range(0, self._samples_per_update_interval, 1)]
        y = [0.0] * self._samples_per_update_interval

        self._input_voice_line.set_data(x, y)
        self._sine_wave_line.set_data(x, y)
        self._modulated_voice_line.set_data(x, y)

        return (self._input_voice_line,
                self._sine_wave_line,
                self._modulated_voice_line)

    def _get_frame_for_animation(self):
        """Return data for next animation frame.

        Receive and return input voice, sine wave and modulated voice samples
        from a multithread queue for plotting.

        Yields:
            _type_: buffer with input voice samples,
            buffer with sine wave samples,
            buffer with modulated voice samples.
        """
        input_voice_buffer: list[float] = []
        sine_wave_buffer: list[float] = []
        modulated_voice_buffer: list[float] = []

        while self.running is True:
            input_voice_buffer.clear()
            sine_wave_buffer.clear()
            modulated_voice_buffer.clear()

            for _ in range(0, self._samples_per_update_interval, 1):
                input_voice_point: float = 0
                sine_wave_point: float = 0
                modulated_voice_point: float = 0

                input_voice_point, sine_wave_point, modulated_voice_point = \
                    self._multithread_queue.get(block=True)
                
                input_voice_buffer.append(input_voice_point)
                sine_wave_buffer.append(sine_wave_point)
                modulated_voice_buffer.append(modulated_voice_point)

            input_voice_buffer_copy: list[float] = \
                input_voice_buffer.copy()
            sine_wave_buffer_copy: list[float] = \
                sine_wave_buffer.copy()
            modulated_voice_buffer_copy: list[float] = \
                modulated_voice_buffer.copy()
            
            yield (input_voice_buffer_copy,
                   sine_wave_buffer_copy,
                   modulated_voice_buffer_copy)
                
    def _update_animation(self, frame: Any, *fargs: Any):
        """Draw animation frame.

        Args:
            frame (Any): data to draw.

        Returns:
            _type_: line to draw input voice,
            line to draw sine wave,
            line to draw modulated voice.
        """
        input_voice_buffer: list[float] = []
        sine_wave_buffer: list[float] = []
        modulated_voice_buffer: list[float] = []

        input_voice_buffer, sine_wave_buffer, modulated_voice_buffer = frame
        
        self._input_voice_line.set_ydata(input_voice_buffer)
        self._sine_wave_line.set_ydata(sine_wave_buffer)
        self._modulated_voice_line.set_ydata(modulated_voice_buffer)

        return (self._input_voice_line,
                self._sine_wave_line,
                self._modulated_voice_line)
    
    def close(self) -> None:
        """Stop animation and close plot."""
        self.running = False
        try:
            self._animation.pause()
        except AttributeError:
            pass
        plt.close(fig=self._figure)

    @property
    def running(self) -> bool:
        """Return a flag that specifies whether plot is running.

        Returns:
            bool: True - plot is running.
            False - plot is not running.
        """
        running_copy: bool = True
        with self._mutex_running:
            running_copy = self._running
        return running_copy

    @running.setter
    def running(self, new_running: bool) -> None:
        """Check and set new "running" flag.

        Args:
            new_running (bool): new "running" flag.

        Raises:
            ValueError: invalid argument.
        """
        # Check argument.
        if((not isinstance(new_running, bool))):
            raise ValueError("ERROR! Invalid argument!")

        with self._mutex_running:
            self._running = new_running
import math
import threading


class SineWaveGenerator:
    def __init__(self,
                 sampling_frequency: int,
                 sine_wave_frequency: int) -> None:
        """Initialize a sine wave with a specified frequency.

        Args:
            sampling_frequency (int): sampling frequency, Hz.
            sine_wave_frequency (int): sine wave frequency. Hz.

        Raises:
            ValueError: invalid arguments.
        """
        super().__init__()

        # Check arguments.
        if((not isinstance(sampling_frequency, int)) or
           (sampling_frequency <= 0) or
           (not isinstance(sine_wave_frequency, int)) or
           (sine_wave_frequency <= 0) or
           (sine_wave_frequency >= sampling_frequency/2)):
            raise ValueError("ERROR! Invalid arguments!")
        
        self._mutex_sine_wave_generator: threading.Lock = threading.Lock()

        self._sampling_frequency: int = sampling_frequency
        self._sine_wave_frequency: int = sine_wave_frequency

        self._number_of_samples_in_sine_wave_period: int \
            = self._sampling_frequency // self._sine_wave_frequency
        self._current_sample_index: int = 0

        self._sine_wave: list[float] = []
        self._generate_sine_wave()

    def _generate_sine_wave(self) -> None:
        """Generate a buffer that contains one sine wave period."""
        with self._mutex_sine_wave_generator:
            self._sine_wave.clear()
            for i in range(0, self._number_of_samples_in_sine_wave_period, 1):
                current_time: float = i * 1 / self._sampling_frequency
                sine_wave_point: float = math.sin(
                    2 * math.pi * self._sine_wave_frequency * current_time)
                self._sine_wave.append(sine_wave_point)
    
    def get_sine_wave_point(self) -> float:
        """Return next sine wave point.

        Returns:
            float: next sine wave point.
        """
        sine_wave_point: float = 0

        with self._mutex_sine_wave_generator:
            sine_wave_point = self._sine_wave[self._current_sample_index]
            
            self._current_sample_index = self._current_sample_index + 1
            if (self._current_sample_index
                >= self._number_of_samples_in_sine_wave_period):
                self._current_sample_index = 0

        return sine_wave_point
    
    @property
    def sine_wave_frequency(self) -> int:
        """Return sine wave frequency.

        Returns:
            int: sine wave frequency, Hz.
        """
        sine_wave_frequency_copy: int = 0
        with self._mutex_sine_wave_generator:
            sine_wave_frequency_copy = self._sine_wave_frequency
        return sine_wave_frequency_copy

    @sine_wave_frequency.setter
    def sine_wave_frequency(self, new_sine_wave_frequency: int) -> None:
        """Check and set new sine wave frequency.

        Check and set new sine wave frequency.
        Regenerate a buffer that contains one sine wave period.

        Args:
            new_sine_wave_frequency (int): new sine wave frequency, Hz.

        Raises:
            ValueError: invalid argument.
        """
        # Check argument.
        if((not isinstance(new_sine_wave_frequency, int)) or
           (new_sine_wave_frequency <= 0) or
           (new_sine_wave_frequency >= self._sampling_frequency/2)):
            raise ValueError("ERROR! Invalid argument!")
        
        with self._mutex_sine_wave_generator:
            self._sine_wave_frequency = new_sine_wave_frequency
        
            self._number_of_samples_in_sine_wave_period \
                = self._sampling_frequency // self._sine_wave_frequency
            self._current_sample_index = 0

        self._generate_sine_wave()
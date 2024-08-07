import math


class SineWaveGenerator:
    # TODO min max default
    def __init__(self,
                 sampling_frequency: int,
                 sine_wave_frequency: int) -> None:
        super().__init__()

        # Check arguments.
        if (sampling_frequency <= 0) or (sine_wave_frequency <= 0):
            raise ValueError("Arguments must be > 0.")
        
        if sine_wave_frequency >= sampling_frequency/2:
            raise ValueError(
                "sine_wave_frequency must be < sampling_frequency/2.")
        
        self._sampling_frequency: int = sampling_frequency
        self._sine_wave_frequency: int = sine_wave_frequency
        self._number_of_samples_in_sine_wave_period: int \
            = self._sampling_frequency // self._sine_wave_frequency
        self._current_sample_index: int = 0

        self._sine_wave: list[float] = self._generate_sine_wave()

    def _generate_sine_wave(self) -> list[float]:
        sine_wave: list[float] = []
        for i in range(0, self._number_of_samples_in_sine_wave_period, 1):
            current_time: float = i * 1 / self._sampling_frequency
            sine_wave_point: float = math.sin(
                2 * math.pi * self._sine_wave_frequency * current_time)
            sine_wave.append(sine_wave_point)
        return sine_wave
    
    def get_sine_wave_point(self) -> float:
        sine_wave_point: float = self._sine_wave[self._current_sample_index]
        
        self._current_sample_index = self._current_sample_index + 1
        if (self._current_sample_index
            >= self._number_of_samples_in_sine_wave_period):
            self._current_sample_index = 0

        return sine_wave_point
    # TODO mutex, проверка как в параметрах
    def set_sine_wave_frequency(self,
                                sine_wave_frequency: int) -> None:
        # Check arguments.
        if sine_wave_frequency <= 0:
            raise ValueError("sine_wave_frequency must be > 0.")
        
        if sine_wave_frequency >= self._sampling_frequency/2:
            raise ValueError(
                "sine_wave_frequency must be < self._sampling_frequency/2.")
        
        self._sine_wave_frequency = sine_wave_frequency
        self._number_of_samples_in_sine_wave_period \
            = self._sampling_frequency // self._sine_wave_frequency
        self._current_sample_index = 0

        self._sine_wave = self._generate_sine_wave()
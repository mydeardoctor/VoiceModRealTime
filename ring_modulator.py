class RingModulator:
    @staticmethod
    def modulate(input_signal_point: float,
                 sine_wave_point: float) -> float:
        modulated_signal_point: float = input_signal_point * sine_wave_point
        return modulated_signal_point
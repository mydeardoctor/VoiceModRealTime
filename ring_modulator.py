class RingModulator:
    @staticmethod
    def modulate(input_voice_point: float,
                 sine_wave_point: float) -> float:
        # Check arguments.
        if ((input_voice_point is None) or
            (not isinstance(input_voice_point, (int, float))) or
            (sine_wave_point is None) or
            (not isinstance(sine_wave_point, (int, float)))):
            raise ValueError("ERROR! Invalid arguments!")

        modulated_voice_point: float = input_voice_point * sine_wave_point
        return modulated_voice_point
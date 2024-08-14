class RingModulator:
    @staticmethod
    def modulate(input_voice_point: int | float,
                 sine_wave_point: int | float) -> float:
        """Modulate input voice by a sine wave and return modulated voice.

        Args:
            input_voice_point (int | float): input voice point.
            sine_wave_point (int | float): sine wave point.

        Raises:
            ValueError: invalid arguments.

        Returns:
            float: modulated voice point.
        """
        # Check arguments.
        if ((not isinstance(input_voice_point, (int, float))) or
            (not isinstance(sine_wave_point, (int, float)))):
            raise ValueError("ERROR! Invalid arguments!")

        modulated_voice_point: float = input_voice_point * sine_wave_point
        return modulated_voice_point
import random


class NoiseGenerator:
    @staticmethod    
    def get_noise_point() -> float:
        NOISE_DIVIDER: int = 10000
        noise_point: float = random.gauss(mu=0.0, sigma=1.0) / NOISE_DIVIDER
        return noise_point
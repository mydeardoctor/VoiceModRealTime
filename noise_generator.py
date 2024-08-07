import random


class NoiseGenerator:
    @staticmethod    
    def get_noise_point() -> float:
        noise_point: float = random.gauss(mu=0.0, sigma=1.0) / 10000
        return noise_point
import random

class NoiseGenerator:
    def __init__(self,
                 divider: int) -> None:
        super().__init__()

        # Check arguments.
        if divider <= 0:
            raise ValueError("Divider must be > 0.")
        
        self._divider: int = divider
    
    def get_noise_point(self) -> float:
        noise_point: float = random.gauss(mu=0.0, sigma=1.0)
        noise_point = noise_point / self._divider
        return noise_point
import json


class Parameters:
    def __init__(self) -> None:
        super().__init__()

        self._MIN_VOLUME: float = 1.0
        self._MIN_FREQUENCY: int = 1
        
        self._MAX_VOLUME: float = 20.0
        self._MAX_FREQUENCY: int = 500

        self._DEFAULT_VOLUME: float = self._MIN_VOLUME
        self._DEFAULT_FREQUENCY: int = 220
        self._DEFAULT_ADD_NOISE: bool = True

        self._volume: float = self._DEFAULT_VOLUME
        self._frequency: int = self._DEFAULT_FREQUENCY
        self._add_noise: bool = self._DEFAULT_ADD_NOISE

        self._CONFIG_FILE_NAME: str = "config.json"

        load_status: bool = self._load()
        if load_status is False:
            self._save()

    def _load(self) -> bool:
        load_status: bool = True

        try:
            with open(self._CONFIG_FILE_NAME, "r") as config_file:
                parameters_from_config_file = json.load(config_file)
                volume_from_config_file: float = \
                    parameters_from_config_file["volume"]
                frequency_from_config_file: int = \
                    parameters_from_config_file["frequency"]
                add_noise_from_config_file = \
                    parameters_from_config_file["add_noise"]
                print("Parameters are loaded from config file successfully.")
                
                # Check parameters.
                result: bool = self._check_volume(volume_from_config_file)
                if result is True:
                    self._volume = volume_from_config_file
                else:
                    print("ERROR! Using default \"volume\"!")
                    self._volume = self._DEFAULT_VOLUME
                    load_status = False

                result = self._check_frequency(frequency_from_config_file)
                if result is True:
                    self._frequency = frequency_from_config_file
                else:
                    print("ERROR! Using default \"frequency\"!")
                    self._frequency = self._DEFAULT_FREQUENCY
                    load_status = False
                
                result = self._check_add_noise(add_noise_from_config_file)
                if result is True:
                    self._add_noise = add_noise_from_config_file
                else:
                    print("ERROR! Using default \"add noise\"!")
                    self._add_noise = self._DEFAULT_ADD_NOISE
                    load_status = False

        except BaseException as e:
            print(type(e))
            print(e)
            print("ERROR! Could not load parameters from config file!")
            print("ERROR! Using default parameters!")
            self._volume = self._DEFAULT_VOLUME
            self._frequency = self._DEFAULT_FREQUENCY
            self._add_noise = self._DEFAULT_ADD_NOISE
            load_status = False
    
        return load_status

    def _save(self) -> None:
        parameters_to_config_file = {
            "volume":self._volume,
            "frequency":self._frequency,
            "add_noise":self._add_noise
        }

        try:
            with open(self._CONFIG_FILE_NAME, "w") as config_file:
                json.dump(parameters_to_config_file, config_file, indent=4)
                print("Parameters are saved to config file successfully.")

        except BaseException as e:
            print(type(e))
            print(e)
            print("ERROR! Could not save parameters to config file!")

    def _check_volume(self, volume) -> bool:
        if ((volume is not None) and
            (isinstance(volume, (int, float))) and
            (volume >= self._MIN_VOLUME) and
            (volume <= self._MAX_VOLUME)):
            print("\"Volume\" is valid.")
            return True
        else:
            print("ERROR! \"Volume\" is invalid! "
                  "\"Volume\" must be int or float! "
                  "\"Volume\" must be between "
                  f"{self._MIN_VOLUME} and {self._MAX_VOLUME}!")
            return False

    def _check_frequency(self, frequency) -> bool:
        if ((frequency is not None) and
            (isinstance(frequency, int)) and
            (frequency >= self._MIN_FREQUENCY) and
            (frequency <= self._MAX_FREQUENCY)):
            print("\"Frequency\" is valid.")
            return True
        else:
            print("ERROR! \"Frequency\" is invalid! "
                  "\"Frequency\" must be int! "
                  "\"Frequency\" must be between "
                  f"{self._MIN_FREQUENCY} and {self._MAX_FREQUENCY}!")
            return False

    def _check_add_noise(self, add_noise) -> bool:
        if ((add_noise is not None) and
            (isinstance(add_noise, bool))):
            print("\"Add noise\" is valid.")
            return True
        else:
            print("ERROR! \"Add noise\" is invalid! "
                  "\"Add noise\" must be bool!")
            return False
    
    @property
    def volume(self) -> float:
        return self._volume
    
    @volume.setter
    def volume(self, new_volume: float) -> None:
        result: bool = self._check_volume(new_volume)
        if result is True:
            self._volume = new_volume
        else:
            print("ERROR! Using default \"volume\"!")
            self._volume = self._DEFAULT_VOLUME
        self._save()
 
    @property
    def frequency(self) -> int:
        return self._frequency
    
    @frequency.setter
    def frequency(self, new_frequency: int) -> None:
        result: bool = self._check_frequency(new_frequency)
        if result is True:
            self._frequency = new_frequency
        else:
            print("ERROR! Using default \"frequency\"!")
            self._frequency = self._DEFAULT_FREQUENCY
        self._save()
    
    @property
    def add_noise(self) -> bool:
        return self._add_noise
    
    @add_noise.setter
    def add_noise(self, new_add_noise) -> None:
        result: bool = self._check_add_noise(new_add_noise)
        if result is True:
            self._add_noise = new_add_noise
        else:
            print("ERROR! Using default \"add noise\"!")
            self._add_noise = self._DEFAULT_ADD_NOISE
        self._save()
from enum import Enum

# Supported Platforms
class SupportedPlatforms(Enum):
    SWITCH = 'switch'

    @classmethod
    def platform_list(cls):
        return [value.value for value in cls.__members__.values()]
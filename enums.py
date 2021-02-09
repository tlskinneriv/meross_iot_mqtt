from enum import Enum

# Supported Platforms
class SupportedPlatforms(Enum):
    SWITCH = 'switch'
    COVER = 'cover'

    @classmethod
    def platform_list(cls):
        return [value.value for value in cls.__members__.values()]
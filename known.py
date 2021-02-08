# List of known configurations for devices

from .const import CONF_PLATFORM, CONF_NUMCHANNELS
from .enums import SupportedPlatforms

KNOWN_DEVICES = {
    'mss510x': {
        CONF_PLATFORM: SupportedPlatforms.SWITCH.value,
        CONF_NUMCHANNELS: 1
    },
    'mss550x': {
        CONF_PLATFORM: SupportedPlatforms.SWITCH.value,
        CONF_NUMCHANNELS: 1
    },
    'mss120b': {
        CONF_PLATFORM: SupportedPlatforms.SWITCH.value,
        CONF_NUMCHANNELS: 2
    }
}
"""The Meross IoT MQTT integration."""
import asyncio

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from homeassistant.components import mqtt
from homeassistant.helpers import entity_registry as er

from .const import DOMAIN, CONF_PLATFORM, CONF_UUID
from .enums import SupportedPlatforms

# TODO List the platforms that you want to support.
# For your initial PR, limit it to 1 platform.
PLATFORMS = SupportedPlatforms.platform_list()

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Meross IoT MQTT from a config entry."""
    # TODO Store an API object for your platforms to access
    # hass.data[DOMAIN][entry.entry_id] = MyApi(...)

    platform = entry.data[CONF_PLATFORM]
    uuid = entry.data[CONF_UUID]

    if platform not in PLATFORMS:
        _LOGGER.warning('Config entry for {} with platform {} cannot be setup because platform {} is not supported.'.format(uuid, platform, platform))
    else:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )
    #if unload_ok:
    #    hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

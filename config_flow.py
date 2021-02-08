"""Config flow to configure Tuya integration"""

import logging

from typing import Dict, Any

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from voluptuous import All, Range
from homeassistant import config_entries, data_entry_flow
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME

from .const import DOMAIN, CONF_MAC, CONF_MODEL, CONF_UUID, CONF_NUMCHANNELS, CONF_PLATFORM
from .meross.device import MerossBaseDevice

from . import PLATFORMS
from .known import KNOWN_DEVICES

_LOGGER = logging.getLogger(__name__)


class MerossMQTTConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Meross MQTT integration config flow."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    def __init__(self):
        """Initialize flow"""
        self._uuid = vol.UNDEFINED
        self._model = vol.UNDEFINED
        self._mac = vol.UNDEFINED
        self._num_channels = vol.UNDEFINED
        self._platform = vol.UNDEFINED

    @property
    def name(self):
        return '{} - {}'.format(self._model, self._mac)

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        errors = {}

        if user_input is not None:
            self._uuid = user_input[CONF_UUID]
            self._model = user_input[CONF_MODEL]
            self._mac = user_input[CONF_MAC]
            self._num_channels = user_input[CONF_NUMCHANNELS]
            self._platform = user_input[CONF_PLATFORM]

            await self.async_set_unique_id(self._uuid)
            self._abort_if_unique_id_configured(
                updates={CONF_UUID: self._uuid}
            )

            return self.async_create_entry(
                title=self.name,
                data={
                    CONF_UUID: self._uuid,
                    CONF_MODEL: self._model,
                    CONF_MAC: self._mac,
                    CONF_NUMCHANNELS: self._num_channels,
                    CONF_PLATFORM: self._platform,
                },
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_UUID): str,
                    vol.Required(CONF_MODEL): str,
                    vol.Required(CONF_MAC): str,
                    vol.Required(CONF_NUMCHANNELS, default=1): All(int, Range(min=1)),
                    vol.Required(CONF_PLATFORM): vol.In(PLATFORMS),
                }
            ),
            errors=errors,
        )

    async def async_step_import(self, user_input):
        """Import a config flow from configuration."""

        #if self._async_current_entries():
        #    return self.async_abort(reason="already_configured")

        self._uuid = user_input[CONF_UUID]
        self._model = user_input[CONF_MODEL]
        self._mac = user_input[CONF_MAC]
        self._num_channels = user_input[CONF_NUMCHANNELS]
        self._platform = user_input[CONF_PLATFORM]

        await self.async_set_unique_id(self._uuid)
        self._abort_if_unique_id_configured(
            updates={CONF_UUID: self._uuid}
        )

        return self.async_create_entry(
            title=self.name,
            data={
                CONF_UUID: self._uuid,
                CONF_MODEL: self._model,
                CONF_MAC: self._mac,
                CONF_NUMCHANNELS: self._num_channels,
                CONF_PLATFORM: self._platform,
            },
        )

    async def async_step_mqtt(self, discovery_info: Dict[str, Any]):
        device_info = MerossBaseDevice.get_auto_config_info(discovery_info.payload)
        if device_info:
            uuid = device_info[CONF_UUID]
            
            self._uuid = uuid
            self._mac = device_info[CONF_MAC]
            self._model = device_info[CONF_MODEL]

            await self.async_set_unique_id(uuid)
            self._abort_if_unique_id_configured(
                updates={CONF_UUID: uuid}
            )

            # check to see if we know info for the model
            known_device = KNOWN_DEVICES.get(self._model)
            if (known_device):
                # if we do, completely setup the device
                self._num_channels = known_device[CONF_NUMCHANNELS]
                self._platform = known_device[CONF_PLATFORM]
                return self.async_create_entry(
                    title=self.name,
                    data={
                        CONF_UUID: self._uuid,
                        CONF_MODEL: self._model,
                        CONF_MAC: self._mac,
                        CONF_NUMCHANNELS: self._num_channels,
                        CONF_PLATFORM: self._platform,
                    },
                )
            return await self.async_step_discovery_confirm()
        raise data_entry_flow.AbortFlow("non_bind_discovery")

    async def async_step_discovery_confirm(self, user_input=None):
        """Handle user-confirmation of discovered node."""
        errors = {}

        if user_input is not None:
            self._num_channels = user_input[CONF_NUMCHANNELS]
            self._platform = user_input[CONF_PLATFORM]

            return self.async_create_entry(
                title=self.name,
                data={
                    CONF_UUID: self._uuid,
                    CONF_MODEL: self._model,
                    CONF_MAC: self._mac,
                    CONF_NUMCHANNELS: self._num_channels,
                    CONF_PLATFORM: self._platform,
                },
            )

        return self.async_show_form(
            step_id="discovery_confirm",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NUMCHANNELS, default=1): All(int, Range(min=1)),
                    vol.Required(CONF_PLATFORM): vol.In(PLATFORMS),
                }
            ),
            errors=errors,
        )
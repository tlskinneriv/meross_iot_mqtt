"""Platform for switch integration."""
import logging

import voluptuous as vol
from voluptuous import All, Range
import asyncio
from datetime import timedelta

import homeassistant.helpers.config_validation as cv

from homeassistant.components.switch import (PLATFORM_SCHEMA, SwitchEntity)
from homeassistant.const import (STATE_ON, STATE_OFF, STATE_UNKNOWN, STATE_UNAVAILABLE)
from homeassistant.core import callback

from .const import (CONF_MODEL, CONF_UUID, CONF_MAC, DOMAIN, CONF_NUMCHANNELS)

from .meross.device import MerossSwitchDevice

_LOGGER = logging.getLogger(__name__)

# Validate user's config
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_UUID): cv.string,
    vol.Required(CONF_MODEL): cv.string,
    vol.Required(CONF_MAC): cv.string,
    vol.Optional(CONF_NUMCHANNELS, default=1): All(int, Range(min=1))
})

async def async_setup_platform(hass, config, async_add_devices, discovery_info=None):
    """ Set up the Meross Switch """
    uuid = config[CONF_UUID]
    model = config[CONF_MODEL]
    mac = config[CONF_MAC]
    num_channels = config[CONF_NUMCHANNELS]

    # Create entities and add them
    devices = [MerossSwitchEntity(uuid, model, mac, channel) for channel in range(num_channels)]
    async_add_devices(devices)

async def async_setup_entry(hass, config_entry, async_add_devices):
    """ Set up the Meross Switch """
    uuid = config_entry.data[CONF_UUID]
    model = config_entry.data[CONF_MODEL]
    mac = config_entry.data[CONF_MAC]
    num_channels = config_entry.data[CONF_NUMCHANNELS]

    # Create device & add it
    devices = [MerossSwitchEntity(uuid, model, mac, channel) for channel in range(num_channels)]
    async_add_devices(devices)

class MerossSwitchEntity(SwitchEntity):
    
    def __init__(self, uuid, model, mac, channel=0):
        self.entity_id = 'switch.meross_iot_mqtt_{}_{}'.format(uuid, channel)
        self._device = MerossSwitchDevice(uuid=uuid, mac=mac, channel=channel)
        self._mqtt_topic = '/appliance/{}/subscribe'.format(uuid)
        self._model = model
        
    @property
    def should_poll(self):
        return True
    
    @property
    def is_on(self):
        return True if self.state == STATE_ON else False

    @property
    def state(self):
        return self._device.state

    @property
    def name(self):
        """ Default name for a new switch """
        return 'Meross {} Switch {}'.format(self._model, self._device.channel)

    @property
    def unique_id(self):
        return '{}_{}'.format(self._device.uuid, self._device.channel)

    @property
    def device_info(self):
        """Information about this entity/device."""
        return {
            "identifiers": {(DOMAIN, self._device.uuid)},
            "name": "Meross {} Switch".format(self._model),
            "manufacturer": 'Meross',
            "model": self._model
        }

    def initialize(self):
        self._send_mqtt_payload(self._device.init_led())
        self._send_mqtt_payload(self._device.request_update())

    async def async_added_to_hass(self):
        # Subscribe to MQTT updates
        @callback
        def message_received(msg):
            payload = msg.payload
            self._process_mqtt_payload(payload)

        topic = '/appliance/{}/publish'.format(self._device.uuid)
        await self.hass.components.mqtt.async_subscribe(topic, message_received)

        # Initialize the device
        self.initialize()
    
    def turn_on(self):
        self._send_mqtt_payload(self._device.turn_on())

    def turn_off(self):
        self._send_mqtt_payload(self._device.turn_off())

    def update(self):
        if self._device.state == STATE_UNKNOWN or self._device.state == STATE_UNAVAILABLE:
            self._send_mqtt_payload(self._device.request_update())

    def _send_mqtt_payload(self, mqtt_payload):
        self.hass.components.mqtt.publish(self._mqtt_topic, mqtt_payload)
    
    def _process_mqtt_payload(self, mqtt_payload):
        self._device.update(mqtt_payload)
        self.schedule_update_ha_state()
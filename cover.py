"""Platform for switch integration."""
import logging

import voluptuous as vol
from voluptuous import All, Range
import asyncio
from datetime import timedelta

import homeassistant.helpers.config_validation as cv

from homeassistant.components.cover import (PLATFORM_SCHEMA, CoverEntity, DEVICE_CLASS_GARAGE, SUPPORT_CLOSE, SUPPORT_OPEN)
from homeassistant.const import (STATE_OPEN, STATE_CLOSED, STATE_UNKNOWN, STATE_OPENING, STATE_CLOSING)
from homeassistant.core import callback

from .const import (CONF_MODEL, CONF_UUID, CONF_MAC, DOMAIN, CONF_NUMCHANNELS)

from .meross.device import MerossGarageDoorDevice

_LOGGER = logging.getLogger(__name__)

# Validate user's config
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_UUID): cv.string,
    vol.Required(CONF_MODEL): cv.string,
    vol.Required(CONF_MAC): cv.string,
    vol.Optional(CONF_NUMCHANNELS, default=1): All(int, Range(min=1))
})

# Default scan interval time
#SCAN_INTERVAL = timedelta(minutes=2)

async def async_setup_platform(hass, config, async_add_devices, discovery_info=None):
    """ Set up the Meross Cover """
    uuid = config[CONF_UUID]
    model = config[CONF_MODEL]
    mac = config[CONF_MAC]
    num_channels = config[CONF_NUMCHANNELS]

    # Create entities and add them
    devices = [MerossCoverEntity(uuid, model, mac, channel) for channel in range(num_channels)]
    async_add_devices(devices)

async def async_setup_entry(hass, config_entry, async_add_devices):
    """ Set up the Meross Cover """
    uuid = config_entry.data[CONF_UUID]
    model = config_entry.data[CONF_MODEL]
    mac = config_entry.data[CONF_MAC]
    num_channels = config_entry.data[CONF_NUMCHANNELS]

    # Create device & add it
    devices = [MerossCoverEntity(uuid, model, mac, channel) for channel in range(num_channels)]
    async_add_devices(devices)

class MerossCoverEntity(CoverEntity):
    
    def __init__(self, uuid, model, mac, channel=0):
        self.entity_id = 'switch.meross_iot_mqtt_{}_{}'.format(uuid, channel)
        self._device = MerossGarageDoorDevice(uuid=uuid, mac=mac, channel=channel)
        self._mqtt_topic = '/appliance/{}/subscribe'.format(uuid)
        self._model = model
        
    should_poll = False

    @property
    def device_class(self):
        """Return the class of this device, from component DEVICE_CLASSES."""
        return DEVICE_CLASS_GARAGE

    @property
    def supported_features(self):
        """Flag supported features."""
        return SUPPORT_OPEN | SUPPORT_CLOSE
    
    @property
    def is_closed(self):
        return True if self.state == STATE_CLOSED else False

    @property
    def is_opening(self):
        return True if self.state == STATE_OPENING else False

    @property
    def is_closing(self):
        return True if self.state == STATE_CLOSING else False
    
    @property
    def state(self):
        return self._device.state

    @property
    def name(self):
        """ Default name for a new switch """
        return 'Meross {} Garage Door Opener {}'.format(self._model, self._device.channel)

    @property
    def unique_id(self):
        return '{}_{}'.format(self._device.uuid, self._device.channel)

    @property
    def device_info(self):
        """Information about this entity/device."""
        return {
            "identifiers": {(DOMAIN, self._device.uuid)},
            "name": "Meross {} Garage Door Opener".format(self._model),
            "manufacturer": 'Meross',
            "model": self._model
        }

    def initialize(self):
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
    
    def open_cover(self):
        self._send_mqtt_payload(self._device.open())
        self._device.state = STATE_OPENING
        self.schedule_update_ha_state()

    def close_cover(self):
        self._send_mqtt_payload(self._device.close())
        self._device.state = STATE_CLOSING
        self.schedule_update_ha_state()

    def update(self):
        self._send_mqtt_payload(self._device.request_update())

    def _send_mqtt_payload(self, mqtt_payload):
        self.hass.components.mqtt.publish(self._mqtt_topic, mqtt_payload)
    
    def _process_mqtt_payload(self, mqtt_payload):
        self._device.update(mqtt_payload)
        self.schedule_update_ha_state()
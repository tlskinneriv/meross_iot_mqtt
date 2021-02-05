"""Platform for switch integration."""
import logging

import voluptuous as vol

import homeassistant.helpers.config_validation as cv

from homeassistant.components.switch import (PLATFORM_SCHEMA, SwitchEntity)
from homeassistant.const import (STATE_ON, STATE_OFF, STATE_UNKNOWN)
from homeassistant.core import callback

from .const import (CONF_MAC, CONF_UUID, CONF_DEVICENAME, DOMAIN)

from .meross.device import MerossSwitchDevice

_LOGGER = logging.getLogger(__name__)

# Validate user's config
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_UUID): cv.string,
    vol.Required(CONF_MAC): cv.string,
    vol.Required(CONF_DEVICENAME): cv.string,
})

def setup_platform(hass, config, add_devices, discovery_info=None):
    """ Set up the Meross Switch """
    uuid = config[CONF_UUID]
    mac = config[CONF_MAC]
    device_name = config[CONF_DEVICENAME]

    # Create device & add it
    device = MerossSwitchEntity(uuid, mac, device_name)
    add_devices([device])

    # Subscribe to MQTT updates
    @callback
    def message_received(topic, payload, qos):
        device._process_mqtt_payload(payload)

    topic = '/appliance/{}/publish'.format(uuid)
    hass.components.mqtt.subscribe(topic, message_received)

    # Initialize the device
    device.initialize()

class MerossSwitchEntity(SwitchEntity):
    
    def __init__(self, uuid, mac, device_name):
        self.entity_id = 'switch.meross_iot_mqtt_{}'.format(uuid)
        self._device = MerossSwitchDevice(uuid=uuid, mac=mac, device_name=device_name)
        self._mqtt_topic = '/appliance/{}/subscribe'.format(uuid)
        
    should_poll = False
    
    @property
    def is_on(self):
        True if self.state == STATE_ON else False

    @property
    def state(self):
        return self._device.state

    @property
    def name(self):
        """ Default name for a new switch """
        return 'Meross Smart Switch'

    @property
    def unique_id(self):
        return self._device._uuid

    @property
    def device_info(self):
        """Information about this entity/device."""
        return {
            "identifiers": {(DOMAIN, self._device._uuid)},
            # If desired, the name for the device could be different to the entity
            "name": self.name,
            "manufacturer": 'Meross',
        }

    def initialize(self):
        self._send_mqtt_payload(self._device.init_led())
        self._send_mqtt_payload(self._device.request_update())
    
    def turn_on(self):
        self._send_mqtt_payload(self._device.turn_on())

    def turn_off(self):
        self._send_mqtt_payload(self._device.turn_off())

    def _send_mqtt_payload(self, mqtt_payload):
        self.hass.components.mqtt.publish(self._mqtt_topic, mqtt_payload)
    
    def _process_mqtt_payload(self, mqtt_payload):
        self._device.update(mqtt_payload)
        self.schedule_update_ha_state()
import json
import random
import string

from time import time
from hashlib import md5

from .mixins import ToggleXMixin, LEDModeMixin
from .enums import Namespace, Method, LEDMode
from .utils import mangle, valid_header
from .const import (METH_PUSH, METH_GETACK)

from homeassistant.components import mqtt
from homeassistant.const import (STATE_ON, STATE_OFF, STATE_UNKNOWN)

import logging

_LOGGER = logging.getLogger(__name__)

class MerossBaseDevice(object):
    def __init__(self, uuid, mac, device_name):
        self._uuid = uuid
        self._mac = mac
        self._device_name = device_name
        self.state = STATE_UNKNOWN

    def _get_message_header(self, method: Method, namespace: Namespace):
        messageId = md5(''.join(random.choice(string.ascii_lowercase) for i in range(16)).encode()).hexdigest()
        timestamp = int(time())
        key = mangle(self._device_name)

        sign = md5('{}{}{}'.format(messageId, key, timestamp).encode()).hexdigest()

        header = {
            'from': '/appliance/{}/publish'.format(self._uuid),
            'messageId': messageId,
            'method': method.value,
            'namespace': namespace.value,
            'payloadVersion': 1,
            'sign': sign,
            'timestamp': timestamp,
        }
        return header

    def _get_mqtt_payload(self, method: Method, namespace: Namespace, payload_options: dict):
        payload = {
            'header': self._get_message_header(method, namespace),
            'payload': payload_options
        }
        json_payload = json.dumps(payload, indent=4)
        return json_payload

    def request_update(self):
        return self._get_mqtt_payload(Method.GET, Namespace.SYSTEM_ALL, {})

    def update(self, payload_json):
        """ This needs to be overriden by the device """
        return None

class MerossSwitchDevice(ToggleXMixin, LEDModeMixin, MerossBaseDevice):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def turn_on(self):
        return self.togglex_turn_on(0)

    def turn_off(self):
        return self.togglex_turn_off(0)

    def init_led(self):
        return self.set_led_mode(LEDMode.ON_WHEN_LIGHT_ON)

    def update(self, payload_json):
        """ return a hass supported state response """
        payload = json.loads(payload_json)
        header = payload['header']
        payload = payload['payload']
        if valid_header(header, [METH_GETACK, METH_PUSH]):
            self.state = self.togglex_get_state(payload)
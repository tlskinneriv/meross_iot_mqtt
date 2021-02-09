from .enums import Namespace, Method, LEDMode

from homeassistant.const import STATE_ON, STATE_OFF, STATE_UNAVAILABLE

class ToggleXMixin(object):
    def togglex_turn_on(self, channel: int):
        payload_options = {
            'togglex': {
                'channel': channel,
                'onoff': 1
            }
        }
        return self._get_mqtt_payload(Method.SET, Namespace.CONTROL_TOGGLEX, payload_options)

    def togglex_turn_off(self, channel: int):
        payload_options = {
            'togglex': {
                'channel': channel,
                'onoff': 0
            }
        }
        return self._get_mqtt_payload(Method.SET, Namespace.CONTROL_TOGGLEX, payload_options)

    def togglex_get_state(self, payload):
        if payload.get('all'):
            """ deal with digest payload """
            togglex = payload.get('all').get('digest').get('togglex', list())
            # check to make sure we're outside the range of the list
        else:
            togglex = payload.get('togglex', list())
        togglex = [x for x in list(togglex) if x['channel'] == self.channel]
        if not togglex:
            return None
        togglex = togglex[0]
        return 1 if togglex['onoff'] == 1 else 0

class LEDModeMixin(object):
    def set_led_mode(self, led_mode):
        payload_options = {
            'LedMode': {
                'mode': led_mode.value
            }
        }
        return self._get_mqtt_payload(Method.SET, Namespace.SYSTEM_LEDMODE, payload_options)

class GarageOpenerMixin(object):
    def garage_open(self, channel: int):
        payload_options = {
            'state': {
                'channel': channel,
                'open': 1
            }
        }
        return self._get_mqtt_payload(Method.SET, Namespace.GARAGE_DOOR_STATE, payload_options)

    def garage_close(self, channel: int):
        payload_options = {
            'state': {
                'channel': channel,
                'open': 0
            }
        }
        return self._get_mqtt_payload(Method.SET, Namespace.GARAGE_DOOR_STATE, payload_options)

    def garage_get_state(self, payload):
        if payload.get('all'):
            """ deal with digest payload """
            garageDoor = payload.get('all').get('digest').get('garageDoor', list())
            # check to make sure we're outside the range of the list
        else:
            # garage door state is actually in the 'state' key
            garageDoor = payload.get('state', list())
        garageDoor = [x for x in list(garageDoor) if x['channel'] == self.channel]
        if not garageDoor:
            return None
        garageDoor = garageDoor[0]
        return 1 if garageDoor['open'] == 1 else 0
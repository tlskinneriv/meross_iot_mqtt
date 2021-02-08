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
            return STATE_UNAVAILABLE
        togglex = togglex[0]
        return STATE_ON if togglex['onoff'] == 1 else STATE_OFF

class LEDModeMixin(object):
    def set_led_mode(self, led_mode):
        payload_options = {
            'LedMode': {
                'mode': led_mode.value
            }
        }
        return self._get_mqtt_payload(Method.SET, Namespace.SYSTEM_LEDMODE, payload_options)
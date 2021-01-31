from .enums import Namespace, Method

from homeassistant.const import STATE_ON, STATE_OFF

class ToggleXMixin(object):
    def togglex_turn_on(self):
        payload_options = {
            'togglex': {
                'channel': 0,
                'onoff': 1
            }
        }
        return self._get_mqtt_payload(Method.SET, Namespace.CONTROL_TOGGLEX, payload_options)

    def togglex_turn_off(self):
        payload_options = {
            'togglex': {
                'channel': 0,
                'onoff': 0
            }
        }
        return self._get_mqtt_payload(Method.SET, Namespace.CONTROL_TOGGLEX, payload_options)

    def togglex_get_state(self, payload):
        if payload.get('all'):
            """ deal with digest payload """
            togglex = payload.get('all').get('digest').get('togglex')
        else:
            togglex = payload.get('togglex')
        return STATE_ON if togglex[0]['onoff'] == 1 else STATE_OFF
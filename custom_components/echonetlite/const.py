"""Constants for the echonetlite integration."""
from homeassistant.const import CONF_ICON, CONF_NAME, CONF_TYPE
from pychonet.HomeAirConditioner import FAN_SPEED, AIRFLOW_VERT, AIRFLOW_HORIZ, AUTO_DIRECTION, SWING_MODE

DOMAIN = "echonetlite"

SENSOR_TYPE_TEMPERATURE = "temperature"

HVAC_OP_FAN = "Air flow rate setting"
HVAC_OP_AUTO = "Automatic control of air flow direction setting"
HVAC_OP_SWING = "Automatic swing of air flow setting"
HVAC_OP_HORIZ = "Air flow direction (horizontal) setting"
HVAC_OP_VERT = "Air flow direction (vertical) setting"


HVAC_SELECT_OP_CODES = {
        0xA0: {"name": HVAC_OP_FAN, "options": FAN_SPEED},
        0xA1: {"name": HVAC_OP_AUTO, "options": AUTO_DIRECTION},
        0xA3: {"name": HVAC_OP_SWING, "options": SWING_MODE},
        0xA5: {"name": HVAC_OP_HORIZ, "options": AIRFLOW_HORIZ},
        0xA4: {"name": HVAC_OP_VERT, "options": AIRFLOW_VERT}
    }

ENL_SENSOR_OP_CODES = {
        0x00: {
            0x11 : {
                0xE0: {CONF_ICON: "mdi:thermometer", CONF_TYPE: SENSOR_TYPE_TEMPERATURE},
            }
        },
        0x01: {
            0x30: {
                0xBE: {CONF_ICON: "mdi:thermometer", CONF_TYPE: SENSOR_TYPE_TEMPERATURE},
                0xBB: {CONF_ICON: "mdi:thermometer", CONF_TYPE: SENSOR_TYPE_TEMPERATURE}
            }
        },
        'default':  {CONF_ICON: None, CONF_TYPE: None},
    }  

ATTR_STATE_ON = "on"
ATTR_STATE_OFF = "off"

HVAC_AUTO_SWING_VERT = "auto-vert"
HVAC_AUTO_SWING_BOTH = "auto"
HVAC_AUTO_SWING_HORIZ = "auto-horiz"
HVAC_AUTO_SWING_OFF = "non-auto"

HVAC_SWING_BOTH = "vert-horiz"
HVAC_SWING_VERT = "vert"
HVAC_SWING_HORIZ = "horiz"
HVAC_SWING_OFF = "not-used"
HVAC_SWING_SPLIT = "left-right"


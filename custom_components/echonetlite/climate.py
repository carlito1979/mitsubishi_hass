import logging

_LOGGER = logging.getLogger(__name__)

from pychonet.HomeAirConditioner import (
    ENL_STATUS,
    ENL_FANSPEED,
    ENL_AUTO_DIRECTION,
    ENL_SWING_MODE,
    ENL_AIR_VERT,
    ENL_AIR_HORZ,
    ENL_HVAC_MODE,
    ENL_HVAC_SET_TEMP,
    ENL_HVAC_ROOM_TEMP,
    ENL_HVAC_OUT_TEMP
)

from pychonet.EchonetInstance import ENL_SETMAP
from pychonet.lib.eojx import EOJX_CLASS

from homeassistant.components.climate import ClimateEntity
from homeassistant.util.unit_system import UnitSystem
from homeassistant.components.climate.const import (
    ATTR_TARGET_TEMP_HIGH,
    ATTR_TARGET_TEMP_LOW,
    SUPPORT_TARGET_TEMPERATURE,
    SUPPORT_FAN_MODE,
    SUPPORT_SWING_MODE,
    SUPPORT_PRESET_MODE,
    ATTR_FAN_MODES,
    ATTR_SWING_MODES,
    ATTR_PRESET_MODES,
    CURRENT_HVAC_OFF,
    CURRENT_HVAC_HEAT,
    CURRENT_HVAC_COOL,
    CURRENT_HVAC_DRY,
    CURRENT_HVAC_IDLE,
    CURRENT_HVAC_FAN,
    HVAC_MODE_OFF,
    HVAC_MODE_HEAT,
    HVAC_MODE_COOL,
    HVAC_MODE_HEAT_COOL,
    HVAC_MODE_AUTO,
    HVAC_MODE_DRY,
    HVAC_MODE_FAN_ONLY,
)
from homeassistant.const import (
    TEMP_CELSIUS,
    TEMP_FAHRENHEIT,
    ATTR_TEMPERATURE,
    CONF_HOST,
    CONF_IP_ADDRESS,
    CONF_NAME,
    PRECISION_WHOLE,
)
from .const import (
    DOMAIN, HVAC_AUTO_SWING_OFF, HVAC_AUTO_SWING_VERT, HVAC_SWING_BOTH, HVAC_SWING_HORIZ, HVAC_SWING_OFF, HVAC_SWING_SPLIT, HVAC_SWING_VERT, HVAC_OP_FAN, HVAC_OP_AUTO, HVAC_OP_SWING, HVAC_OP_HORIZ, HVAC_OP_VERT
)
SUPPORT_FLAGS = 0

async def async_setup_entry(hass, config_entry, async_add_devices):
    """Set up entry."""
    entities = []
    for entity in hass.data[DOMAIN][config_entry.entry_id]:
        if entity['instance_data']['eojgc'] == 1 and entity['instance_data']['eojcc'] == 48: #Home Air Conditioner
             entities.append(EchonetClimate(config_entry.data["title"], entity['API'], hass.config.units))
    async_add_devices(entities, True)

"""Representation of an ECHONETLite climate device."""
class EchonetClimate(ClimateEntity):
    def __init__(self, name, instance, units: UnitSystem, fan_modes=None, swing_modes=None, preset_modes=None):
        """Initialize the climate device."""
        self._name = name
        self._instance = instance  # new line
        self._uid = self._instance._uid
        self._unit_of_measurement = units.temperature_unit
        self._precision = 1.0
        self._target_temperature_step = 1
        self._support_flags = SUPPORT_FLAGS
        self._support_flags = self._support_flags | SUPPORT_TARGET_TEMPERATURE
        if ENL_FANSPEED in list(instance._api.propertyMaps[ENL_SETMAP].values()):
            self._support_flags = self._support_flags | SUPPORT_FAN_MODE
        if ENL_AIR_VERT in list(instance._api.propertyMaps[ENL_SETMAP].values()):
            self._support_flags = self._support_flags | SUPPORT_SWING_MODE
        if ENL_AIR_HORZ in list(instance._api.propertyMaps[ENL_SETMAP].values()):
            self._support_flags = self._support_flags | SUPPORT_PRESET_MODE
        if fan_modes is not None:
            self._fan_modes = fan_modes
        else:
            self._fan_modes = ['minimum', 'low', 'medium-low', 'medium-high', 'high', 'auto']
        self._hvac_modes = ["heat", "cool", "dry", "fan_only", "heat_cool", "off"]
        if swing_modes is not None:
            self._swing_modes = swing_modes
        else:
            self._swing_modes = ['swing', 'upper', 'upper-central', 'central', 'lower-central', 'lower', 'auto']
        if preset_modes is not None:
            self._preset_modes = preset_modes
        else:
            self._preset_modes = ['swing', 'left', 'lc', 'center', 'rc', 'right', 'left-right']

    async def async_update(self):
        """Get the latest state from the HVAC."""
        await self._instance.async_update()

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return self._support_flags

    @property
    def precision(self) -> float:
        return PRECISION_WHOLE

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._uid

    @property
    def device_info(self):
        return {
            "identifiers": {
                  (DOMAIN, self._instance._uid, self._instance._api.eojgc, self._instance._api.eojcc, self._instance._api.instance)
            },
            "name": EOJX_CLASS[self._instance._api.eojgc][self._instance._api.eojcc]
            #"manufacturer": "Mitsubishi",
            #"model": "",
            #"sw_version": "",
        }

    @property
    def should_poll(self):
        """Return the polling state."""
        return True

    @property
    def name(self):
        """Return the name of the climate device."""
        return self._name

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement

    @property
    def current_temperature(self):
        """Return the current temperature."""
        if ENL_HVAC_ROOM_TEMP in list(self._instance._api.propertyMaps[ENL_SETMAP].values()):
            return self._instance._update_data[ENL_HVAC_ROOM_TEMP] if ENL_HVAC_ROOM_TEMP in self._instance._update_data else 'unavailable'
        else:
            return self._instance._update_data[ENL_HVAC_SET_TEMP]

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self._instance._update_data[ENL_HVAC_SET_TEMP] if ENL_HVAC_SET_TEMP in self._instance._update_data else 'unavailable'

    @property
    def target_temperature_step(self):
        """Return the supported step of target temperature."""
        return self._target_temperature_step

    @property
    def hvac_mode(self):
        """Return current operation ie. heat, cool, idle."""
        return self._instance._update_data[ENL_HVAC_MODE] if self._instance._update_data[ENL_STATUS] == "On" else "off"

    @property
    def hvac_action(self):
        """Return current operation ie. heat, cool, idle."""
        if self._instance._update_data[ENL_STATUS] == "On":
            if self._instance._update_data[ENL_HVAC_MODE] == HVAC_MODE_HEAT:
                return CURRENT_HVAC_HEAT
            elif self._instance._update_data[ENL_HVAC_MODE] == HVAC_MODE_COOL:
                return CURRENT_HVAC_COOL
            elif self._instance._update_data[ENL_HVAC_MODE]== HVAC_MODE_DRY:
                return CURRENT_HVAC_DRY
            elif self._instance._update_data[ENL_HVAC_MODE] == HVAC_MODE_FAN_ONLY:
                return CURRENT_HVAC_FAN
            elif self._instance._update_data[ENL_HVAC_MODE] == HVAC_MODE_HEAT_COOL:
                if ENL_HVAC_ROOM_TEMP in self._instance._update_data:
                    if self._instance._update_data[ENL_HVAC_SET_TEMP]  < self._instance._update_data[ENL_HVAC_ROOM_TEMP]:
                        return CURRENT_HVAC_COOL
                    elif self._instance._update_data[ENL_HVAC_SET_TEMP]  > self._instance._update_data[ENL_HVAC_ROOM_TEMP]:
                        return CURRENT_HVAC_HEAT
                return CURRENT_HVAC_IDLE
        return CURRENT_HVAC_OFF

    @property
    def hvac_modes(self):
        """Return the list of available operation modes."""
        return self._hvac_modes

    @property
    def is_on(self):
        """Return true if the device is on."""
        return True if self._instance._update_data[ENL_STATUS] == "On" else False

    @property
    def fan_mode(self):
        """Return the fan setting."""
        return self._instance._update_data[ENL_FANSPEED] if ENL_FANSPEED in self._instance._update_data else "unavailable"

    @property
    def fan_modes(self):
        """Return the list of available fan modes."""
        return self._fan_modes

    async def async_set_fan_mode(self, fan_mode):
        """Set new fan mode."""
        await self.hass.async_add_executor_job(self._instance._api.setFanSpeed, fan_mode)
        self._instance._update_data[ENL_FANSPEED] = fan_mode

    @property
    def swing_modes(self):
        """Return the list of available swing modes."""
        return self._swing_modes
    
    @property
    def swing_mode(self):
        """Return the swing mode setting."""
        # Code updated to reflect ability to set auto and swing modes
        # check first to see if auto mode is engaged and if so return auto
        if self._instance._update_data[ENL_AUTO_DIRECTION] == HVAC_AUTO_SWING_VERT:
            return "auto"
            # check next for swing mode
        elif (self._instance._update_data[ENL_SWING_MODE] == HVAC_SWING_VERT or self._instance._update_data[ENL_SWING_MODE] == HVAC_SWING_BOTH):
            return "swing"
        return self._instance._update_data[ENL_AIR_VERT] if ENL_AIR_VERT in self._instance._update_data else "unavailable"

    async def async_set_swing_mode(self, swing_mode):
        """Set new swing mode."""
        # code updated to reflect ability to set auto and swing modes
        # check if auto, swing or manual mode is specified and branch accordingly
        if swing_mode == "auto":
            # first we need to check for swing mode as we may need to stop it and/or move to only horizontal if required
            if self._instance._update_data[ENL_SWING_MODE] == HVAC_SWING_VERT:
                # single vertical swing mode activated - need to disable before setting auto swing mode
                await self.hass.async_add_executor_job(self._instance._api.setSwingMode, HVAC_SWING_OFF)
                self._instance._update_data[ENL_SWING_MODE] = HVAC_SWING_OFF
            elif self._instance._update_data[ENL_SWING_MODE] == HVAC_SWING_BOTH:
                # dual swing mode activated - need to switch to horiztonal only before setting auto swing mode
                await self.hass.async_add_executor_job(self._instance._api.setSwingMode, HVAC_SWING_HORIZ)
                self._instance._update_data[ENL_SWING_MODE] = HVAC_SWING_HORIZ
            # switch to auto mode (we assume that no units can do auto horizontal mode)
            await self.hass.async_add_executor_job(self._instance._api.setAutoDirection, HVAC_AUTO_SWING_VERT)
            self._instance._update_data[ENL_AUTO_DIRECTION] = HVAC_AUTO_SWING_VERT
        elif swing_mode == "swing":
            # first we check for auto mode and disable if active (we assume no units can do auto horizontal mode)
            if self._instance._update_data[ENL_AUTO_DIRECTION] == HVAC_AUTO_SWING_VERT:
                await self.hass.async_add_executor_job(self._instance._api.setAutoDirection, HVAC_AUTO_SWING_OFF)
                self._instance._update_data[ENL_AUTO_DIRECTION] = HVAC_AUTO_SWING_OFF
            # then we check if current mode is already swinging for horizontal mode or not
            if self._instance._update_data[ENL_SWING_MODE] == HVAC_SWING_HORIZ:
                # set dual vertical/horizontal swing mode
                await self.hass.async_add_executor_job(self._instance._api.setSwingMode, HVAC_SWING_BOTH)
                self._instance._update_data[ENL_SWING_MODE] = HVAC_SWING_BOTH
            else:
                # set swing mode for vertical only
                await self.hass.async_add_executor_job(self._instance._api.setSwingMode, HVAC_SWING_VERT)
                self._instance._update_data[ENL_SWING_MODE] = HVAC_SWING_VERT
        else:
            # if we get to here we assume it's just a standard manual position setting for vertical vane
            # but we still need to disable auto and swing modes if they were previously selected!
            """ This is really ugly as it is duplicating some of the code above """
            if self._instance._update_data[ENL_SWING_MODE] == HVAC_SWING_VERT:
                # single vertical swing mode activated - need to disable
                await self.hass.async_add_executor_job(self._instance._api.setSwingMode, HVAC_SWING_OFF)
                self._instance._update_data[ENL_SWING_MODE] = HVAC_SWING_OFF
            elif self._instance._update_data[ENL_SWING_MODE] == HVAC_SWING_BOTH:
                # dual swing mode activated - need to switch to horiztonal only before setting auto swing mode
                await self.hass.async_add_executor_job(self._instance._api.setSwingMode, HVAC_SWING_HORIZ)
                self._instance._update_data[ENL_SWING_MODE] = HVAC_SWING_HORIZ
            elif self._instance._update_data[ENL_AUTO_DIRECTION] == HVAC_AUTO_SWING_VERT:
                # check for auto mode and disable if active (we assume no units can do auto horizontal mode)
                await self.hass.async_add_executor_job(self._instance._api.setAutoDirection, HVAC_AUTO_SWING_OFF)
                self._instance._update_data[ENL_AUTO_DIRECTION] = HVAC_AUTO_SWING_OFF
            await self.hass.async_add_executor_job(self._instance._api.setAirflowVert, swing_mode)
            self._instance._update_data[ENL_AIR_VERT] = swing_mode

    """ Code to allow setting of horizontal swing using the presets function in the HA climate entity """
    @property
    def preset_mode(self):
        """Return the horizt  mode setting."""
        # check if mode is set to swing or split first and return different results if yes
        # check first for swing mode
        if (self._instance._update_data[ENL_SWING_MODE] == HVAC_SWING_HORIZ or self._instance._update_data[ENL_SWING_MODE] == HVAC_SWING_BOTH):
            return "swing"
        # check next for split mode
        check = self._instance._update_data[ENL_AIR_HORZ] if ENL_AIR_HORZ in self._instance._update_data else "unavailable"
        if check == HVAC_SWING_SPLIT:
            return "split"
        return check 

    @property
    def preset_modes(self):
        """Return the list of available preset modes."""
        return self._preset_modes

    async def async_set_preset_mode(self, preset_mode):
        """Set new preset mode."""
        # first we check if swing mode was specified
        if preset_mode == "swing":
            # check if vertical mode already set to swing or not and proceed accordingly
            if self._instance._update_data[ENL_SWING_MODE] == HVAC_SWING_VERT:
                # vertical swing mode already set - switch to dual swing mode
                await self.hass.async_add_executor_job(self._instance._api.setSwingMode, HVAC_SWING_BOTH)
                self._instance._update_data[ENL_SWING_MODE] = HVAC_SWING_BOTH
            else:
                # set swing mode for horizontal only
                await self.hass.async_add_executor_job(self._instance._api.setSwingMode, HVAC_SWING_HORIZ)
                self._instance._update_data[ENL_SWING_MODE] = HVAC_SWING_HORIZ            
        elif preset_mode == "split":
            # next we check for split mode
            await self.hass.async_add_executor_job(self._instance._api.setAirflowHoriz, HVAC_SWING_SPLIT)
            self._instance._update_data[ENL_AIR_HORZ] = HVAC_SWING_SPLIT
        else:
            await self.hass.async_add_executor_job(self._instance._api.setAirflowHoriz, preset_mode)
            self._instance._update_data[ENL_AIR_HORZ] = preset_mode













    async def async_set_temperature(self, **kwargs):
        """Set new target temperatures."""
        if kwargs.get(ATTR_TEMPERATURE) is not None:
            await self.hass.async_add_executor_job(self._instance._api.setOperationalTemperature, kwargs.get(ATTR_TEMPERATURE))
            self._instance._update_data[ENL_HVAC_SET_TEMP] =  kwargs.get(ATTR_TEMPERATURE)

    async def async_set_hvac_mode(self, hvac_mode):
        _LOGGER.warning(self._instance._update_data)
        """Set new operation mode (including off)"""
        if hvac_mode == "heat_cool":
            await self.hass.async_add_executor_job(self._instance._api.setMode, "auto")
        else:
            await self.hass.async_add_executor_job(self._instance._api.setMode, hvac_mode)
        self._instance._update_data[ENL_HVAC_MODE]  = hvac_mode
        if hvac_mode == "off":
            self._instance._update_data[ENL_STATUS] = "Off"
        else:
            self._instance._update_data[ENL_STATUS] = "On"

    async def async_turn_on(self):
        """Turn on."""
        self.hass.async_add_executor_job(self._instance._api.on())

    async def async_turn_off(self):
        """Turn off."""
        self.hass.async_add_executor_job(self._instance._api.off())

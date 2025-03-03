"""Constants for the Becker Antriebe CentralControl integration."""

from enum import StrEnum

from homeassistant.components.cover import CoverDeviceClass
from homeassistant.const import Platform

PLATFORMS: list[Platform] = [Platform.COVER, Platform.LIGHT, Platform.SENSOR]
DOMAIN = "becker_centralcontrol_has"
MANUFACTURER = "Becker Antriebe GmbH"


class DEVICE_TYPES(StrEnum):
    """Central Control device types."""

    AWNING = "awning"
    DOOR = "door"
    DOOR_PULSE = "door-pulse"
    ROOF_WINDOW = "roof-window"
    SCREEN = "screen"
    SHUTTER = "shutter"
    SHUTTER_BLINDS = "shutter-blinds"
    SHUTTER_FOLDOUT = "shutter-foldout"
    SUN_SAIL = "sun-sail"
    VENETIAN = "venetian"
    TILT_WINDOW = "tilt-window"
    DIMMER = "dimmer"
    SWITCH = "switch"


class REMOTE_TYPES(StrEnum):
    """Central Control sensor types."""

    SUN = "sensor-sun"
    WIND = "sensor-wind"
    RAIN = "sensor-rain"
    DAWN = "sensor-dawn"
    TEMPERATURE = "sensor-temperature"
    SUN_WIND = "sensor-sun-wind"
    SUN_RAIN = "sensor-sun-rain"
    SUN_WIND_RAIN = "sensor-sun-wind-rain"
    SUN_WIND_RAIN_TEMP = "sensor-sun-wind-rain-temp"
    SUN_WIND_RAIN_DAWN = "sensor-sun-wind-rain-dawn"


REMOTE_SUPPORTED_VALUES = {
    REMOTE_TYPES.SUN: ["sun"],
    REMOTE_TYPES.WIND: ["wind"],
    REMOTE_TYPES.RAIN: ["rain"],
    REMOTE_TYPES.DAWN: ["dawn"],
    REMOTE_TYPES.TEMPERATURE: ["temp"],
    REMOTE_TYPES.SUN_WIND: ["sun", "wind"],
    REMOTE_TYPES.SUN_RAIN: ["sun", "rain"],
    REMOTE_TYPES.SUN_WIND_RAIN: ["sun", "wind", "rain"],
    REMOTE_TYPES.SUN_WIND_RAIN_TEMP: ["sun", "wind", "rain", "temp", "dawn"],
    REMOTE_TYPES.SUN_WIND_RAIN_DAWN: ["sun", "wind", "rain", "dawn"],
}


COVER_MAPPING = {
    DEVICE_TYPES.AWNING: CoverDeviceClass.AWNING,
    DEVICE_TYPES.DOOR: CoverDeviceClass.DOOR,
    DEVICE_TYPES.DOOR_PULSE: CoverDeviceClass.DOOR,
    DEVICE_TYPES.ROOF_WINDOW: CoverDeviceClass.WINDOW,
    DEVICE_TYPES.SCREEN: CoverDeviceClass.SHUTTER,
    DEVICE_TYPES.SHUTTER: CoverDeviceClass.SHUTTER,
    DEVICE_TYPES.SHUTTER_BLINDS: CoverDeviceClass.BLIND,
    DEVICE_TYPES.SHUTTER_FOLDOUT: CoverDeviceClass.SHUTTER,
    DEVICE_TYPES.SUN_SAIL: CoverDeviceClass.SHADE,
    DEVICE_TYPES.VENETIAN: CoverDeviceClass.SHUTTER,
    DEVICE_TYPES.TILT_WINDOW: CoverDeviceClass.WINDOW,
}

BECKER_LIGHT_TYPES = [DEVICE_TYPES.DIMMER, DEVICE_TYPES.SWITCH]

BECKER_COVER_REVERSE_TYPES = [DEVICE_TYPES.AWNING]

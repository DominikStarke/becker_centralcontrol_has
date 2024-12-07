"""Constants for the Becker Antriebe CentralControl integration."""

from enum import StrEnum

from homeassistant.components.cover import CoverDeviceClass
from homeassistant.const import Platform

PLATFORMS: list[Platform] = [Platform.COVER, Platform.LIGHT]
DOMAIN = "beckerantriebe"
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

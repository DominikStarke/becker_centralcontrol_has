"""Tests for CentralControl cover entities."""

from __future__ import annotations

from enum import IntFlag
from types import ModuleType, SimpleNamespace
import sys


def _install_homeassistant_stubs() -> None:
    """Install minimal Home Assistant stubs needed to import the cover."""

    homeassistant = ModuleType("homeassistant")
    components = ModuleType("homeassistant.components")
    cover = ModuleType("homeassistant.components.cover")
    config_entries = ModuleType("homeassistant.config_entries")
    const = ModuleType("homeassistant.const")
    core = ModuleType("homeassistant.core")
    helpers = ModuleType("homeassistant.helpers")
    device_registry = ModuleType("homeassistant.helpers.device_registry")
    entity_platform = ModuleType("homeassistant.helpers.entity_platform")

    class CoverEntity:
        pass

    class CoverEntityFeature(IntFlag):
        OPEN = 1
        CLOSE = 2
        STOP = 4
        SET_POSITION = 8

    class CoverDeviceClass:
        AWNING = "awning"
        DOOR = "door"
        WINDOW = "window"
        SHUTTER = "shutter"
        BLIND = "blind"
        SHADE = "shade"

    class ConfigEntry:
        pass

    class DeviceInfo(dict):
        pass

    class Platform:
        COVER = "cover"
        LIGHT = "light"
        SCENE = "scene"
        SENSOR = "sensor"

    cover.ATTR_POSITION = "position"
    cover.CoverDeviceClass = CoverDeviceClass
    cover.CoverEntity = CoverEntity
    cover.CoverEntityFeature = CoverEntityFeature
    config_entries.ConfigEntry = ConfigEntry
    const.Platform = Platform
    core.HomeAssistant = object
    device_registry.DeviceInfo = DeviceInfo
    entity_platform.AddEntitiesCallback = object

    sys.modules.update(
        {
            "homeassistant": homeassistant,
            "homeassistant.components": components,
            "homeassistant.components.cover": cover,
            "homeassistant.config_entries": config_entries,
            "homeassistant.const": const,
            "homeassistant.core": core,
            "homeassistant.helpers": helpers,
            "homeassistant.helpers.device_registry": device_registry,
            "homeassistant.helpers.entity_platform": entity_platform,
        }
    )


_install_homeassistant_stubs()

from custom_components.becker_centralcontrol_has.cover import BeckerCover  # noqa: E402


def _cover(*, invert_position: bool, position: int) -> BeckerCover:
    central_control = SimpleNamespace(prefix="", invert_position=invert_position)
    cover = BeckerCover(
        central_control=central_control,
        item={"id": 1, "name": "Test", "backend": "btr"},
    )
    cover._attr_current_cover_position = position
    return cover


def test_intermediate_position_is_open() -> None:
    """Treat a cover between its end stops as open."""

    for position in (1, 50, 99):
        assert _cover(invert_position=False, position=position).is_closed is False


def test_intermediate_position_is_open_when_inverted() -> None:
    """Treat an inverted cover between its end stops as open."""

    for position in (1, 50, 99):
        assert _cover(invert_position=True, position=position).is_closed is False


def test_end_stops_keep_existing_state_mapping() -> None:
    """Keep the existing end-stop mapping in both orientation modes."""

    assert _cover(invert_position=False, position=0).is_closed is True
    assert _cover(invert_position=False, position=100).is_closed is False
    assert _cover(invert_position=True, position=0).is_closed is False
    assert _cover(invert_position=True, position=100).is_closed is True

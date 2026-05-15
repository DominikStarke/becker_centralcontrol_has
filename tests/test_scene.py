"""Tests for CentralControl scene entities."""

from __future__ import annotations

from types import ModuleType, SimpleNamespace
from unittest.mock import AsyncMock
import sys


def _install_homeassistant_stubs() -> None:
    """Install minimal Home Assistant stubs needed to import the integration."""

    homeassistant = ModuleType("homeassistant")
    components = ModuleType("homeassistant.components")
    scene = ModuleType("homeassistant.components.scene")
    config_entries = ModuleType("homeassistant.config_entries")
    const = ModuleType("homeassistant.const")
    core = ModuleType("homeassistant.core")
    helpers = ModuleType("homeassistant.helpers")
    device_registry = ModuleType("homeassistant.helpers.device_registry")
    entity_platform = ModuleType("homeassistant.helpers.entity_platform")
    cover = ModuleType("homeassistant.components.cover")

    class Scene:
        pass

    class ConfigEntry:
        def __class_getitem__(cls, item):
            return cls

    class DeviceInfo(dict):
        pass

    class Platform:
        COVER = "cover"
        LIGHT = "light"
        SCENE = "scene"
        SENSOR = "sensor"

    class CoverDeviceClass:
        AWNING = "awning"
        DOOR = "door"
        WINDOW = "window"
        SHUTTER = "shutter"
        BLIND = "blind"
        SHADE = "shade"

    scene.Scene = Scene
    config_entries.ConfigEntry = ConfigEntry
    const.Platform = Platform
    core.HomeAssistant = object
    device_registry.DeviceInfo = DeviceInfo
    entity_platform.AddEntitiesCallback = object
    cover.CoverDeviceClass = CoverDeviceClass

    sys.modules.update(
        {
            "homeassistant": homeassistant,
            "homeassistant.components": components,
            "homeassistant.components.cover": cover,
            "homeassistant.components.scene": scene,
            "homeassistant.config_entries": config_entries,
            "homeassistant.const": const,
            "homeassistant.core": core,
            "homeassistant.helpers": helpers,
            "homeassistant.helpers.device_registry": device_registry,
            "homeassistant.helpers.entity_platform": entity_platform,
        }
    )


_install_homeassistant_stubs()

from custom_components.becker_centralcontrol_has.scene import (  # noqa: E402
    BeckerScene,
    async_setup_entry,
)


async def test_scene_setup_creates_scene_entities() -> None:
    """Create HA scene entities from CentralControl scene items."""

    central_control = SimpleNamespace(
        prefix="",
        get_scene_list=AsyncMock(
            return_value={
                "result": {
                    "item_list": [
                        {"id": 109, "type": "scene", "name": "Terrasse AUF"},
                        {"id": 44, "type": "scene", "name": "Terrasse ZU"},
                        {"id": 17, "type": "group", "name": "TV Stube"},
                    ]
                }
            }
        ),
    )
    entry = SimpleNamespace(runtime_data=central_control)
    added_entities = []

    await async_setup_entry(None, entry, added_entities.extend)

    assert [entity.name for entity in added_entities] == ["Terrasse AUF", "Terrasse ZU"]
    assert [entity.unique_id for entity in added_entities] == ["scene_109", "scene_44"]


async def test_scene_setup_empty_list() -> None:
    """Handle an empty scene list gracefully."""

    central_control = SimpleNamespace(
        prefix="",
        get_scene_list=AsyncMock(return_value={"result": {"item_list": []}}),
    )
    entry = SimpleNamespace(runtime_data=central_control)
    added_entities = []

    await async_setup_entry(None, entry, added_entities.extend)

    assert added_entities == []


async def test_scene_activate_calls_scene_invoke() -> None:
    """Activating a HA scene invokes the CentralControl scene."""

    central_control = SimpleNamespace(prefix="", scene_invoke=AsyncMock())
    scene = BeckerScene(
        central_control=central_control,
        item={"id": 109, "type": "scene", "name": "Terrasse AUF"},
    )

    await scene.async_activate()

    central_control.scene_invoke.assert_awaited_once_with(scene_id=109)

"""Representation of a Scene in the CentralControl."""

from __future__ import annotations

import logging

from homeassistant.components.scene import Scene
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .central_control import CentralControl
from .const import DOMAIN, MANUFACTURER

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Glue CentralControl scene items to HASS entities."""

    central_control: CentralControl = entry.runtime_data
    try:
        item_list = await central_control.get_scene_list()
        scene_list = []

        for item in item_list.get("result", {}).get("item_list", []):
            if item.get("type") == "scene":
                scene_list.append(
                    BeckerScene(
                        central_control=central_control,
                        item=item,
                    )
                )

        async_add_entities(scene_list)
    except TimeoutError:
        _LOGGER.error("Failed to get scene list")
        return


class BeckerScene(Scene):
    """Representation of a Becker scene."""

    def __init__(
        self,
        central_control: CentralControl,
        item: dict,
    ) -> None:
        """Initialize the scene."""
        self._central_control = central_control
        self._item = item

        self._attr_name = f"{central_control.prefix}{item.get('name', 'Unknown')}"
        self._attr_unique_id = f"{central_control.prefix}scene_{item.get('id')}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.unique_id)},
            manufacturer=MANUFACTURER,
            name=self.name,
        )

    @property
    def unique_id(self) -> str:
        """The scene's unique id."""
        return str(self._attr_unique_id)

    @property
    def name(self) -> str:
        """The scene's name, "Unknown" if None."""
        return str(self._attr_name)

    async def async_activate(self, **kwargs) -> None:
        """Activate the scene."""
        await self._central_control.scene_invoke(scene_id=int(self._item.get("id")))

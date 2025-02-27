"""Representation of a Light in the CentralControl."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.components.light import (
    PLATFORM_SCHEMA as LIGHT_PLATFORM_SCHEMA,
    ColorMode,
    LightEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .central_control import CentralControl
from .const import BECKER_LIGHT_TYPES, DOMAIN, MANUFACTURER

_LOGGER = logging.getLogger(__name__)

# Validation of the user's configuration
LIGHT_PLATFORM_SCHEMA = LIGHT_PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
    }
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Glue light items to HASS entities."""

    central_control: CentralControl = entry.runtime_data
    try:
        item_list = await central_control.get_item_list(item_type="group")
        light_list = []

        for item in item_list.get("result", {}).get("item_list", []):
            device_class = item.get("device_type") in BECKER_LIGHT_TYPES
            if device_class is not False:
                light_list.append(
                    BeckerLight(
                        central_control=central_control,
                        item=item,
                    )
                )

        async_add_entities(light_list)
    except TimeoutError:
        _LOGGER.error("Failed to get item list")
        return


class BeckerLight(LightEntity):
    """Representation of a Becker light."""

    def __init__(
        self,
        central_control,
        item,
    ) -> None:
        """Initialize the light."""
        self._central_control: CentralControl = central_control
        self._item = item

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
        """The items unique id."""
        return str(self._item.get("id"))

    @property
    def name(self) -> str:
        """The items name, "Unknown" if None."""
        return self._item.get("name", "Unknown")

    @property
    def should_poll(self) -> bool:
        """True if the item has the feedback flag."""
        if self._item.get("feedback", False) is True:
            return True
        return False

    @property
    def color_mode(self) -> ColorMode | str | None:
        """Flag supported color mode."""
        if self._item.get("device_type") == "dimmer":
            return ColorMode.BRIGHTNESS
        return ColorMode.ONOFF

    @property
    def supported_color_modes(self) -> set[str]:
        """Flag supported color mode."""
        if self._item.get("device_type") == "dimmer":
            return {ColorMode.BRIGHTNESS}
        return {ColorMode.ONOFF}

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the light on."""
        await self._central_control.group_send_command(
            group_id=int(self.unique_id),
            command="switch",
            value=1,
        )

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the the light off."""
        await self._central_control.group_send_command(
            group_id=int(self.unique_id),
            command="switch",
            value=0,
        )

    async def async_added_to_hass(self) -> None:
        """Complete the initialization."""
        await self.async_update()

    async def async_update(self) -> None:
        """Update brightness."""
        state = await self._central_control.get_state(item_id=int(self.unique_id))
        if state.get("value", None) is not None:
            self._attr_is_on = bool(state.get("value"))
            self._attr_brightness = int(state.get("value"))
            _LOGGER.log(logging.INFO, state)

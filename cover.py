"""Representation of a Cover in the CentralControl."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.components.cover import (
    ATTR_POSITION,
    PLATFORM_SCHEMA as COVER_PLATFORM_SCHEMA,
    CoverDeviceClass,
    CoverEntity,
    CoverEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .central_control import CentralControl
from .const import BECKER_COVER_REVERSE_TYPES, COVER_MAPPING, DOMAIN, MANUFACTURER

_LOGGER = logging.getLogger(__name__)

# Validation of the user's configuration
COVER_PLATFORM_SCHEMA = COVER_PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Optional(CONF_USERNAME, default="admin"): cv.string,
        vol.Optional(CONF_PASSWORD): cv.string,
    }
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Glue cover items to HASS entities."""

    central_control: CentralControl = entry.runtime_data
    try:
        item_list = await central_control.get_item_list(item_type="group")
        cover_list = []

        for item in item_list.get("result", {}).get("item_list", []):
            device_class = COVER_MAPPING.get(item.get("device_type"), None)
            if device_class is not None:
                cover_list.append(
                    BeckerCover(
                        central_control=central_control,
                        item=item,
                    )
                )

        async_add_entities(cover_list)
    except TimeoutError:
        _LOGGER.error("Failed to get item list")


class BeckerCover(CoverEntity):
    """Representation of a Becker cover."""

    def __init__(
        self,
        central_control,
        item,
    ) -> None:
        """Initialize the cover."""
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
    def device_class(self) -> CoverDeviceClass | None:
        """Return the class of this device, from component DEVICE_CLASSES."""
        return COVER_MAPPING.get(self._item.get("device_type"))

    @property
    def is_opening(self) -> bool | None:
        """Return if the cover is opening or not."""
        return None

    @property
    def is_closing(self) -> bool | None:
        """Return if the cover is closing or not."""
        return None

    @property
    def is_closed(self) -> bool | None:
        """Return if the cover is closed."""
        if self._item.get("backend") == "centronic":
            return None
        if self._attr_current_cover_position == 0:
            return True
        return False

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
    def supported_features(self) -> CoverEntityFeature:
        """Flag supported features."""
        _supported_features = (
            CoverEntityFeature.OPEN | CoverEntityFeature.STOP | CoverEntityFeature.CLOSE
        )
        if self._item.get("feedback") is True:
            _supported_features |= CoverEntityFeature.SET_POSITION

        return _supported_features

    @property
    def reversed(self) -> bool:
        """Whether the conver is reversed (only awning)."""
        return self._item.get("device_type") in BECKER_COVER_REVERSE_TYPES

    async def async_close_cover(self, **kwargs: Any) -> None:
        """Close the cover."""
        direction = 1
        if self.reversed:
            direction = -1
        await self._central_control.group_send_command(
            group_id=int(self.unique_id),
            command="move",
            value=direction,
        )

    async def async_open_cover(self, **kwargs: Any) -> None:
        """Open the cover."""
        direction = -1
        if self.reversed:
            direction = 1

        await self._central_control.group_send_command(
            group_id=int(self.unique_id),
            command="move",
            value=direction,
        )

    async def async_stop_cover(self, **kwargs: Any) -> None:
        """Stop the cover."""
        await self._central_control.group_send_command(
            group_id=int(self.unique_id),
            command="move",
            value=0,
        )

    async def async_set_cover_position(self, **kwargs: Any) -> None:
        """Set the covers position."""

        value = int(kwargs[ATTR_POSITION])
        if not self.reversed:
            value = 100 - value

        await self._central_control.group_send_command(
            group_id=int(self.unique_id),
            command="moveto",
            value=value,
        )

    async def async_added_to_hass(self) -> None:
        """Complete the initialization."""
        await self.async_update()

    async def async_update(self) -> None:
        """Update brightness."""
        state = await self._central_control.get_state(item_id=int(self.unique_id))
        if state.get("value", None) is not None:
            if self.reversed:
                self._attr_current_cover_position = int(state.get("value", "0"))
            else:
                self._attr_current_cover_position = 100 - int(state.get("value", "0"))
            _LOGGER.log(logging.INFO, state)

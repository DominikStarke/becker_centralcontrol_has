"""Representation of a HVAC zone in the CentralControl."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .central_control import CentralControl
from .const import DOMAIN, MANUFACTURER

_LOGGER = logging.getLogger(__name__)

PRESET_ECO = "eco"
PRESET_COMFORT = "comfort"
PRESET_INDIVIDUAL = "individual"
PRESET_ANTI_FREEZE = "anti-freeze"
PRESETS = [PRESET_COMFORT, PRESET_ECO, PRESET_INDIVIDUAL, PRESET_ANTI_FREEZE]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Glue HVAC zones to climate entities."""

    central_control: CentralControl = entry.runtime_data
    try:
        item_list = await central_control.get_item_list(list_type="climate-zones")
    except TimeoutError:
        _LOGGER.error("Failed to get climate zones")
        return

    zones = [
        item
        for item in item_list.get("result", {}).get("item_list", [])
        if item.get("items")
    ]
    async_add_entities(
        BeckerClimate(central_control=central_control, item=zone) for zone in zones
    )


class BeckerClimate(ClimateEntity):
    """Representation of a Becker HVAC zone."""

    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_hvac_modes = [HVACMode.HEAT, HVACMode.OFF]
    _attr_preset_modes = PRESETS
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.PRESET_MODE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
    )
    _attr_min_temp = 4.0
    _attr_max_temp = 40.0
    _attr_target_temperature_step = 0.5
    _attr_should_poll = True

    def __init__(self, central_control: CentralControl, item: dict) -> None:
        """Initialize the climate entity."""
        self._central_control = central_control
        self._item = item
        self._zone_id = int(item["id"])
        self._attr_unique_id = f"{central_control.prefix}_climate_{self._zone_id}"
        self._attr_name = f"{central_control.prefix}{item.get('name', 'Unknown')}"
        self._mode: str | None = None
        self._target: float | None = None

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._attr_unique_id)},
            manufacturer=MANUFACTURER,
            name=self._attr_name,
        )

    @property
    def hvac_mode(self) -> HVACMode:
        """Return the current hvac mode."""
        return HVACMode.OFF if self._mode == PRESET_ANTI_FREEZE else HVACMode.HEAT

    @property
    def preset_mode(self) -> str | None:
        """Return the current preset."""
        return self._mode

    @property
    def target_temperature(self) -> float | None:
        """Return the target temperature of the active mode."""
        return self._target

    async def async_update(self) -> None:
        """Fetch mode and target temperature."""
        mode = await self._central_control.hvac_zone_get_mode(self._zone_id)
        if mode is None:
            return
        self._mode = mode
        if mode == PRESET_ANTI_FREEZE:
            self._target = None
        else:
            self._target = await self._central_control.hvac_zone_get_temperature(
                self._zone_id, mode
            )

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set an individual target temperature."""
        temp = kwargs.get(ATTR_TEMPERATURE)
        if temp is None:
            return
        await self._central_control.hvac_zone_set_temperature(
            self._zone_id, float(temp), PRESET_INDIVIDUAL
        )
        await self._central_control.hvac_zone_set_mode(self._zone_id, PRESET_INDIVIDUAL)
        self._mode = PRESET_INDIVIDUAL
        self._target = float(temp)

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the operation mode."""
        await self._central_control.hvac_zone_set_mode(self._zone_id, preset_mode)
        await self.async_update()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Map off to anti-freeze and heat to comfort."""
        await self.async_set_preset_mode(
            PRESET_ANTI_FREEZE if hvac_mode == HVACMode.OFF else PRESET_COMFORT
        )

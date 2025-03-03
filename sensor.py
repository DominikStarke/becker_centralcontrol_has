"""Representation of a Sensor in the CentralControl."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import logging
from typing import Any, cast

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .central_control import CentralControl
from .const import DOMAIN, MANUFACTURER, REMOTE_SUPPORTED_VALUES, REMOTE_TYPES

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Glue light items to HASS entities."""

    central_control: CentralControl = entry.runtime_data
    try:
        item_list = await central_control.get_item_list(item_type="remote")
        sensor_list: list[BeckerSensor] = []

        for item in item_list.get("result", {}).get("item_list", []):
            remote_type = item.get("remote_type") in REMOTE_TYPES

            if remote_type is not False:
                supported_values = REMOTE_SUPPORTED_VALUES.get(
                    item.get("remote_type", ""), []
                )

                sensor_list.extend(
                    BeckerSensor(
                        central_control=central_control,
                        item=item,
                        value_type=value_type,
                    )
                    for value_type in supported_values
                )

        async_add_entities(sensor_list)
    except TimeoutError:
        _LOGGER.error("Failed to get item list")
        return


@dataclass(frozen=True, kw_only=True)
class CentralControlSensorDescription(SensorEntityDescription):
    """Describes a CentralControl sensor."""

    value_fn: Callable[[dict[str, Any]], str | int | float | None]


class BeckerSensor(SensorEntity):
    """Representation of a sensor."""

    _attr_has_entity_name = True
    entity_description: CentralControlSensorDescription

    def __init__(
        self,
        central_control,
        item,
        value_type,
    ) -> None:
        """Initialize the sensor."""
        self._central_control: CentralControl = central_control
        self._attr_unique_id = f"{item['id']}-{value_type}"
        self._item = item
        self._value_type = value_type
        self.entity_id = f"sensor.{DOMAIN}_{item['name']}_{value_type}"

        if value_type is REMOTE_SUPPORTED_VALUES[REMOTE_TYPES.TEMPERATURE][0]:
            self.entity_description = CentralControlSensorDescription(
                key=value_type,
                value_fn=lambda data: data,
                device_class=SensorDeviceClass.TEMPERATURE,
                translation_key=value_type,
                native_unit_of_measurement=UnitOfTemperature.CELSIUS,
                state_class=SensorStateClass.MEASUREMENT,
            )
        elif value_type is REMOTE_SUPPORTED_VALUES[REMOTE_TYPES.SUN][0]:
            self.entity_description = CentralControlSensorDescription(
                key=value_type,
                value_fn=lambda data: data,
                icon="mdi:white-balance-sunny",
                translation_key=value_type,
                native_unit_of_measurement="/ 15",
                state_class=SensorStateClass.MEASUREMENT,
            )
        elif value_type is REMOTE_SUPPORTED_VALUES[REMOTE_TYPES.WIND][0]:
            self.entity_description = CentralControlSensorDescription(
                key=value_type,
                value_fn=lambda data: data,
                icon="mdi:weather-dust",
                translation_key=value_type,
                native_unit_of_measurement="/ 11",
                state_class=SensorStateClass.MEASUREMENT,
            )
        elif value_type is REMOTE_SUPPORTED_VALUES[REMOTE_TYPES.RAIN][0]:
            options = ["dry", "rain"]
            self.entity_description = CentralControlSensorDescription(
                key=value_type,
                value_fn=lambda data: options[data],
                device_class=SensorDeviceClass.ENUM,
                options=options,
                icon="mdi:weather-rainy",
                translation_key=value_type,
            )
        elif value_type is REMOTE_SUPPORTED_VALUES[REMOTE_TYPES.DAWN][0]:
            self.entity_description = CentralControlSensorDescription(
                key=value_type,
                value_fn=lambda data: data,
                icon="mdi:weather-sunset",
                translation_key=value_type,
                native_unit_of_measurement="/ 15",
                state_class=SensorStateClass.MEASUREMENT,
            )

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._item.get("id"))},
            manufacturer=MANUFACTURER,
            name=self._item.get("name"),
        )

    @property
    def native_value(self) -> str | int | float | None:
        """Return the state."""

        if self._attr_native_value is None:
            return None

        return self.entity_description.value_fn(self._attr_native_value)

    async def async_update(self) -> None:
        """Update brightness."""

        state = await self._central_control.get_state(item_id=int(self._item.get("id")))
        value = state.get(f"value-{self._value_type}")
        if value is not None:
            self._attr_native_value = round(state.get(f"value-{self._value_type}"), 1)
            # self._attr_extra_state_attributes = {"rain": bool(self._attr_native_value)}

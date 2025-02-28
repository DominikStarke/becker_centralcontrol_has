"""Representation of a Sensor in the CentralControl."""

from __future__ import annotations

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    LIGHT_LUX,
    UnitOfSpeed,
    UnitOfTemperature,
    UnitOfVolumeFlowRate,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .central_control import CentralControl
from .const import DOMAIN, MANUFACTURER, SENSOR_MAPPING, SENSOR_TYPES

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
            device_class = item.get("remote_type") in SENSOR_TYPES

            if device_class is not False:
                supported_values = SENSOR_MAPPING.get(item.get("remote_type", ""))

                sensor_list.extend(
                    BeckerSensor(
                        central_control=central_control,
                        item=item,
                        value=sensor_type,
                    )
                    for sensor_type in supported_values
                )

        async_add_entities(sensor_list)
    except TimeoutError:
        _LOGGER.error("Failed to get item list")
        return


class BeckerSensor(SensorEntity):
    """Representation of a sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        central_control,
        item,
        value,
    ) -> None:
        """Initialize the sensor."""
        self._central_control: CentralControl = central_control
        self._item = item
        self._sensor_type = value

        if value is SENSOR_MAPPING[SENSOR_TYPES.SUN][0]:
            self._attr_native_unit_of_measurement = LIGHT_LUX
            self._attr_device_class = SensorDeviceClass.ILLUMINANCE
            self._attr_state_class = SensorStateClass.MEASUREMENT
        elif value is SENSOR_MAPPING[SENSOR_TYPES.WIND][0]:
            self._attr_native_unit_of_measurement = UnitOfSpeed.KILOMETERS_PER_HOUR
            self._attr_device_class = SensorDeviceClass.WIND_SPEED
            self._attr_state_class = SensorStateClass.MEASUREMENT
        elif value is SENSOR_MAPPING[SENSOR_TYPES.RAIN][0]:
            self._attr_native_unit_of_measurement = (
                UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR
            )
            self._attr_device_class = SensorDeviceClass.VOLUME_FLOW_RATE
            self._attr_state_class = SensorStateClass.MEASUREMENT
        elif value is SENSOR_MAPPING[SENSOR_TYPES.TEMPERATURE][0]:
            self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
            self._attr_device_class = SensorDeviceClass.TEMPERATURE
            self._attr_state_class = SensorStateClass.MEASUREMENT
        elif value is SENSOR_MAPPING[SENSOR_TYPES.DAWN][0]:
            self._attr_native_unit_of_measurement = LIGHT_LUX
            self._attr_device_class = SensorDeviceClass.ILLUMINANCE
            self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def name(self) -> str:
        """The items name, "Unknown" if None."""
        return self._sensor_type

    @property
    def unique_id(self) -> str:
        """The items unique id."""
        return f"{self._item['id']}-{self._sensor_type}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._item.get("id"))},
            manufacturer=MANUFACTURER,
            name=self._item.get("name"),
        )

    async def async_update(self) -> None:
        """Update brightness."""

        state = await self._central_control.get_state(item_id=int(self._item.get("id")))
        value = state.get(f"value-{self._sensor_type}")
        if value is not None:
            self._attr_native_value = round(state.get(f"value-{self._sensor_type}"), 1)

"""Sensor platform for LG-Plug."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import LgPlugDataUpdateCoordinator
from .switch import LgPlugBaseEntity


@dataclass(frozen=True, kw_only=True)
class LgPlugSensorEntityDescription(SensorEntityDescription):
    """Class describing LG-Plug sensor entities."""

    value_fn: Callable[[dict[str, Any]], float | int | None]


SENSOR_TYPES: tuple[LgPlugSensorEntityDescription, ...] = (
    LgPlugSensorEntityDescription(
        key="power",
        translation_key="power",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        suggested_display_precision=1,
        value_fn=lambda data: data.get("_power_w"),
    ),
    LgPlugSensorEntityDescription(
        key="energy",
        translation_key="energy",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=2,
        value_fn=lambda data: data.get("_energy_kwh"),
    ),
    LgPlugSensorEntityDescription(
        key="voltage",
        translation_key="voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        suggested_display_precision=1,
        value_fn=lambda data: data.get("_voltage_v"),
    ),
    LgPlugSensorEntityDescription(
        key="temperature",
        translation_key="temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        suggested_display_precision=1,
        value_fn=lambda data: data.get("_temp_c"),
    ),
    LgPlugSensorEntityDescription(
        key="wifi_signal",
        translation_key="wifi_signal",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        suggested_display_precision=0,
        value_fn=lambda data: data.get("_wifi_signal"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up LG-Plug sensor entities."""
    coordinator: LgPlugDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[LgPlugSensor] = []
    for description in SENSOR_TYPES:
        entities.append(LgPlugSensor(coordinator, entry, description))

    async_add_entities(entities)


class LgPlugSensor(LgPlugBaseEntity, SensorEntity):
    """Representation of an LG-Plug sensor."""

    entity_description: LgPlugSensorEntityDescription

    def __init__(
        self,
        coordinator: LgPlugDataUpdateCoordinator,
        entry: ConfigEntry,
        description: LgPlugSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry)
        self.entity_description = description
        mac = self.coordinator.mac or entry.entry_id
        self._attr_unique_id = f"{mac}_{description.key}"

    @property
    def native_value(self) -> float | int | None:
        """Return the state of the sensor."""
        return self.entity_description.value_fn(self.coordinator.data)

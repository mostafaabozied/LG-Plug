"""Binary sensor platform for PowerK."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import PowerkDataUpdateCoordinator
from .switch import PowerkBaseEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up PowerK binary sensor platform."""
    coordinator: PowerkDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([PowerkConnectivityBinarySensor(coordinator, entry)])


class PowerkConnectivityBinarySensor(PowerkBaseEntity, BinarySensorEntity):
    """Binary sensor representing device connectivity state."""

    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(
        self,
        coordinator: PowerkDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize binary sensor."""
        super().__init__(coordinator, entry)
        mac = self.coordinator.mac or entry.entry_id
        self._attr_unique_id = f"{mac}_connectivity"
        self._attr_translation_key = "connectivity"

    @property
    def is_on(self) -> bool:
        """Return True if device is connected and online."""
        return bool(self.coordinator.data.get("_online", True))

    @property
    def available(self) -> bool:
        """Always available if coordinator update succeeded."""
        return self.coordinator.last_update_success

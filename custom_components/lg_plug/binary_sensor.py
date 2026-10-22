"""Binary sensor platform for LG-Plug."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import LgPlugDataUpdateCoordinator
from .switch import LgPlugBaseEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up LG-Plug binary sensor platform."""
    coordinator: LgPlugDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([LgPlugConnectivityBinarySensor(coordinator, entry)])


class LgPlugConnectivityBinarySensor(LgPlugBaseEntity, BinarySensorEntity):
    """Binary sensor representing device connectivity state."""

    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(
        self,
        coordinator: LgPlugDataUpdateCoordinator,
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

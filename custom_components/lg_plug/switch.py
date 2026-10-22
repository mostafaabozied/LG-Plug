"""Switch platform for LG-Plug."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL
from .coordinator import LgPlugDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the LG-Plug switch platform."""
    coordinator: LgPlugDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SwitchEntity] = []

    # Individual outlets 1 to 4
    for outlet_id in range(1, 5):
        entities.append(LgPlugSwitch(coordinator, entry, outlet_id))

    # Master switch (All outlets)
    entities.append(LgPlugMasterSwitch(coordinator, entry))

    async_add_entities(entities)


class LgPlugBaseEntity(CoordinatorEntity[LgPlugDataUpdateCoordinator]):
    """Base entity for LG-Plug."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: LgPlugDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self.entry = entry

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        mac = self.coordinator.mac or self.entry.entry_id
        return DeviceInfo(
            identifiers={(DOMAIN, mac)},
            name=f"LG-Plug ({mac})" if self.coordinator.mac else "LG-Plug",
            manufacturer=MANUFACTURER,
            model=MODEL,
            sw_version="1.0.0",
        )

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return (
            self.coordinator.last_update_success
            and self.coordinator.data.get("_online", True)
        )


class LgPlugSwitch(LgPlugBaseEntity, SwitchEntity):
    """Representation of an individual LG-Plug outlet switch."""

    _attr_device_class = SwitchDeviceClass.OUTLET

    def __init__(
        self,
        coordinator: LgPlugDataUpdateCoordinator,
        entry: ConfigEntry,
        outlet_id: int,
    ) -> None:
        """Initialize switch."""
        super().__init__(coordinator, entry)
        self.outlet_id = outlet_id
        mac = self.coordinator.mac or entry.entry_id
        self._attr_unique_id = f"{mac}_outlet_{outlet_id}"
        self._attr_translation_key = f"outlet_{outlet_id}"
        self._attr_icon = "mdi:power-socket-eu"

    @property
    def is_on(self) -> bool:
        """Return True if the outlet is on."""
        outlets = self.coordinator.data.get("_normalized_outlets", {})
        return outlets.get(self.outlet_id, False)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the outlet on."""
        await self.coordinator.async_set_outlet(self.outlet_id, True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the outlet off."""
        await self.coordinator.async_set_outlet(self.outlet_id, False)


class LgPlugMasterSwitch(LgPlugBaseEntity, SwitchEntity):
    """Representation of the master switch (controlling all outlets)."""

    _attr_device_class = SwitchDeviceClass.SWITCH

    def __init__(
        self,
        coordinator: LgPlugDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize master switch."""
        super().__init__(coordinator, entry)
        mac = self.coordinator.mac or entry.entry_id
        self._attr_unique_id = f"{mac}_master_switch"
        self._attr_translation_key = "master_switch"
        self._attr_icon = "mdi:power"

    @property
    def is_on(self) -> bool:
        """Return True if any outlet is on."""
        outlets = self.coordinator.data.get("_normalized_outlets", {})
        return any(outlets.values()) if outlets else False

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn all outlets on."""
        await self.coordinator.async_set_outlet(0, True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn all outlets off."""
        await self.coordinator.async_set_outlet(0, False)

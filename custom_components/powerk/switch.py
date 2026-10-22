"""Switch platform for PowerK."""
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
from .coordinator import PowerkDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the PowerK switch platform."""
    coordinator: PowerkDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SwitchEntity] = []

    # Individual outlets 1 to 4
    for outlet_id in range(1, 5):
        entities.append(PowerkSwitch(coordinator, entry, outlet_id))

    # Master switch (All outlets)
    entities.append(PowerkMasterSwitch(coordinator, entry))

    async_add_entities(entities)


class PowerkBaseEntity(CoordinatorEntity[PowerkDataUpdateCoordinator]):
    """Base entity for PowerK."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: PowerkDataUpdateCoordinator,
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
            name=f"Korean Smart Strip ({mac})" if self.coordinator.mac else "Korean Smart Strip",
            manufacturer=MANUFACTURER,
            model=MODEL,
            sw_version="PowerK 1.0",
        )

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return (
            self.coordinator.last_update_success
            and self.coordinator.data.get("_online", True)
        )


class PowerkSwitch(PowerkBaseEntity, SwitchEntity):
    """Representation of an individual PowerK outlet switch."""

    _attr_device_class = SwitchDeviceClass.OUTLET

    def __init__(
        self,
        coordinator: PowerkDataUpdateCoordinator,
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


class PowerkMasterSwitch(PowerkBaseEntity, SwitchEntity):
    """Representation of the master switch (controlling all outlets)."""

    _attr_device_class = SwitchDeviceClass.SWITCH

    def __init__(
        self,
        coordinator: PowerkDataUpdateCoordinator,
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

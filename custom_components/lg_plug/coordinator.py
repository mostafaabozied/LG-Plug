"""DataUpdateCoordinator for LG-Plug."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import API_ONOFF, API_STATE, DOMAIN

_LOGGER = logging.getLogger(__name__)


class LgPlugDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching LG-Plug data from device server."""

    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        port: int,
        token: str,
        scan_interval: int,
    ) -> None:
        """Initialize coordinator."""
        self.host = host
        self.port = port
        self.token = token
        self.session = async_get_clientsession(hass)
        self.base_url = f"http://{host}:{port}"
        self.mac: str = ""

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )

    def _get_headers(self) -> dict[str, str]:
        """Return authentication headers."""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
            headers["X-Token"] = self.token
        return headers

    def _get_params(self) -> dict[str, str]:
        """Return authentication params."""
        params: dict[str, str] = {}
        if self.token:
            params["t"] = self.token
            params["token"] = self.token
        return params

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from device API endpoint."""
        url = f"{self.base_url}{API_STATE}"
        try:
            async with asyncio.timeout(10):
                response = await self.session.get(
                    url,
                    headers=self._get_headers(),
                    params=self._get_params(),
                )

                if response.status in (401, 403):
                    raise ConfigEntryAuthFailed("Invalid authentication token")

                if response.status != 200:
                    raise UpdateFailed(
                        f"Error communicating with LG-Plug API: status {response.status}"
                    )

                data: dict[str, Any] = await response.json()
                self._normalize_data(data)
                return data

        except ConfigEntryAuthFailed:
            raise
        except (TimeoutError, asyncio.TimeoutError) as err:
            raise UpdateFailed(f"Timeout communicating with LG-Plug server: {err}") from err
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Connection error with LG-Plug server: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Unexpected error communicating with LG-Plug: {err}") from err

    def _normalize_data(self, data: dict[str, Any]) -> None:
        """Normalize raw response data into consistent schema."""
        # The server returns {"devices": [{...}], "local_ip": ..., "port": ...}
        dev: dict[str, Any] = data
        if "devices" in data and isinstance(data["devices"], list) and len(data["devices"]) > 0:
            dev = data["devices"][0]

        # MAC extraction
        mac = str(dev.get("mac") or data.get("mac") or "").strip().upper()
        if mac and not self.mac:
            self.mac = mac

        # Normalize outlets: mapping 1..4 to bool
        normalized_outlets: dict[int, bool] = {1: False, 2: False, 3: False, 4: False}
        raw_outlets = dev.get("outlets") or data.get("outlets")

        if isinstance(raw_outlets, list):
            for item in raw_outlets:
                if isinstance(item, dict):
                    num = item.get("n")
                    if num is not None and 1 <= int(num) <= 4:
                        normalized_outlets[int(num)] = bool(item.get("on", False))
                elif isinstance(item, bool):
                    idx = raw_outlets.index(item) + 1
                    if 1 <= idx <= 4:
                        normalized_outlets[idx] = item
        elif isinstance(raw_outlets, dict):
            for k, val in raw_outlets.items():
                try:
                    out_num = int(k)
                    if 1 <= out_num <= 4:
                        if isinstance(val, dict):
                            normalized_outlets[out_num] = bool(val.get("on", False))
                        else:
                            normalized_outlets[out_num] = bool(val)
                except ValueError:
                    pass

        data["_normalized_outlets"] = normalized_outlets

        # Telemetry normalization
        data["_power_w"] = _extract_float(dev, ["power_w", "watts", "power", "watt", "p_w"])
        data["_energy_kwh"] = _extract_float(dev, ["energy_kwh", "kwh", "energy", "total_kwh"])
        data["_voltage_v"] = _extract_float(dev, ["voltage", "voltage_v", "volt", "v"])

        # Temperature: from device root or highest outlet temperature
        temp = _extract_float(dev, ["temperature", "temp", "temp_c", "temperature_c"])
        if temp is None and isinstance(raw_outlets, list):
            temps = [
                float(o["temp_c"])
                for o in raw_outlets
                if isinstance(o, dict) and o.get("temp_c") is not None
            ]
            if temps:
                temp = max(temps)
        data["_temp_c"] = temp

        data["_wifi_signal"] = _extract_float(dev, ["rssi", "wifi", "wifi_rssi", "signal"])
        data["_online"] = bool(dev.get("online", True))

        # Per-outlet power extraction
        outlet_power: dict[int, float] = {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0}
        if isinstance(raw_outlets, list):
            for item in raw_outlets:
                if isinstance(item, dict):
                    num = item.get("n")
                    if num is not None and 1 <= int(num) <= 4:
                        outlet_power[int(num)] = float(item.get("power_w", 0.0) or 0.0)
        data["_outlet_power"] = outlet_power

    async def async_set_outlet(self, outlet_id: int, state: bool) -> bool:
        """Control an outlet (1-4) or master (0)."""
        url = f"{self.base_url}{API_ONOFF}"
        mac = self.mac
        if not mac:
            if "devices" in self.data and isinstance(self.data["devices"], list) and self.data["devices"]:
                mac = self.data["devices"][0].get("mac", "")
            else:
                mac = self.data.get("mac", "")

        payload = {
            "mac": mac,
            "outlet": outlet_id,
            "on": state,
        }

        try:
            async with asyncio.timeout(10):
                response = await self.session.post(
                    url,
                    json=payload,
                    headers=self._get_headers(),
                    params=self._get_params(),
                )
                if response.status != 200:
                    _LOGGER.error(
                        "Failed to toggle outlet %s (HTTP %s)", outlet_id, response.status
                    )
                    return False

                # Optimistically update cached outlet state
                if "_normalized_outlets" in self.data:
                    if outlet_id == 0:
                        for idx in range(1, 5):
                            self.data["_normalized_outlets"][idx] = state
                    elif 1 <= outlet_id <= 4:
                        self.data["_normalized_outlets"][outlet_id] = state

                self.async_update_listeners()
                self.hass.async_create_task(self.async_request_refresh())
                return True

        except Exception as err:
            _LOGGER.error("Error toggling outlet %s: %s", outlet_id, err)
            return False


def _extract_float(data: dict[str, Any], keys: list[str]) -> float | None:
    """Extract a float value from dictionary given a list of candidate keys."""
    for key in keys:
        if key in data and data[key] is not None:
            try:
                return float(data[key])
            except (ValueError, TypeError):
                continue
    return None

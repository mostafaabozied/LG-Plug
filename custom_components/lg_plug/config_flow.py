"""Config flow for LG-Plug integration."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    API_STATE,
    CONF_HOST,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    CONF_TOKEN,
    DEFAULT_NAME,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate that the user input allows us to connect."""
    host = data[CONF_HOST]
    port = data.get(CONF_PORT, DEFAULT_PORT)
    token = data.get(CONF_TOKEN, "")

    session = async_get_clientsession(hass)
    url = f"http://{host}:{port}{API_STATE}"

    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
        headers["X-Token"] = token

    params = {}
    if token:
        params["token"] = token

    try:
        async with asyncio.timeout(10):
            response = await session.get(url, headers=headers, params=params)

            if response.status in (401, 403):
                raise InvalidAuth

            if response.status != 200:
                raise CannotConnect(f"HTTP status {response.status}")

            resp_data = await response.json()
            mac = ""
            if "devices" in resp_data and isinstance(resp_data["devices"], list) and resp_data["devices"]:
                mac = str(resp_data["devices"][0].get("mac") or "").strip().upper()
            if not mac:
                mac = str(resp_data.get("mac") or resp_data.get("id") or "").strip().upper()
            return {"title": f"LG-Plug ({mac})" if mac else DEFAULT_NAME, "mac": mac}

    except InvalidAuth:
        raise
    except (TimeoutError, asyncio.TimeoutError) as err:
        raise CannotConnect("Timeout") from err
    except aiohttp.ClientError as err:
        raise CannotConnect(f"Client error: {err}") from err
    except Exception as err:
        raise CannotConnect(f"Unknown error: {err}") from err


class LgPlugConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for LG-Plug."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                mac = info.get("mac")
                if mac:
                    await self.async_set_unique_id(mac)
                    self._abort_if_unique_id_configured()

                return self.async_create_entry(title=info["title"], data=user_input)

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
                vol.Optional(CONF_TOKEN, default=""): str,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=schema, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return LgPlugOptionsFlowHandler(config_entry)


class LgPlugOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options for LG-Plug."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_scan_interval = self.config_entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        )

        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=current_scan_interval,
                ): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL),
                ),
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)


class CannotConnect(Exception):
    """Error to indicate we cannot connect."""


class InvalidAuth(Exception):
    """Error to indicate there is invalid auth."""

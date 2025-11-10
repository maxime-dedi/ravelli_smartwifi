from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, CONF_EMAIL, CONF_PASSWORD, CONF_BASE_URL, CONF_DEVICE_ID, CONF_SCAN_INTERVAL, DEFAULT_BASE_URL, DEFAULT_SCAN_INTERVAL
from .api import RavelliSmartWifiClient
from homeassistant.helpers.aiohttp_client import async_get_clientsession

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        errors = {}
        if user_input is not None:
            session = async_get_clientsession(self.hass)
            client = RavelliSmartWifiClient(
                session,
                user_input[CONF_BASE_URL],
                user_input[CONF_EMAIL],
                user_input[CONF_PASSWORD],
                user_input[CONF_DEVICE_ID],
            )
            try:
                await client.async_login()
            except Exception:
                errors["base"] = "invalid_auth"
            else:
                await self.async_set_unique_id(user_input[CONF_DEVICE_ID])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=f"Ravelli {user_input[CONF_DEVICE_ID]}", data=user_input)

        schema = vol.Schema({
            vol.Required(CONF_EMAIL): str,
            vol.Required(CONF_PASSWORD): str,
            vol.Required(CONF_BASE_URL, default=DEFAULT_BASE_URL): str,
            vol.Required(CONF_DEVICE_ID): str,
        })
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_import(self, import_config):
        return await self.async_step_user(import_config)

    async def async_step_options(self, user_input=None):
        return await self.async_step_init(user_input)

    async def async_step_init(self, user_input=None):
        return await self.async_step_options(user_input)

class OptionsFlow(config_entries.OptionsFlow):
    def __init__(self, entry):
        self.entry = entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="Options", data=user_input)

        schema = vol.Schema({
            vol.Required(CONF_SCAN_INTERVAL, default=self.entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)): int,
            vol.Required(CONF_BASE_URL, default=self.entry.options.get(CONF_BASE_URL, self.entry.data.get(CONF_BASE_URL))): str,
            vol.Required(CONF_DEVICE_ID, default=self.entry.options.get(CONF_DEVICE_ID, self.entry.data.get(CONF_DEVICE_ID))): str,
        })
        return self.async_show_form(step_id="init", data_schema=schema)

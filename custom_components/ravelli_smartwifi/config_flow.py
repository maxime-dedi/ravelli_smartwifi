from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, CONF_TOKEN, CONF_BASE_URL, CONF_SCAN_INTERVAL, DEFAULT_BASE_URL, DEFAULT_SCAN_INTERVAL
from .api import RavelliSmartWifiClient
from homeassistant.helpers.aiohttp_client import async_get_clientsession

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        errors = {}
        if user_input is not None:
            session = async_get_clientsession(self.hass)
            client = RavelliSmartWifiClient(session, user_input[CONF_BASE_URL], user_input[CONF_TOKEN])
            try:
                await client.async_get_status()
            except Exception:
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(user_input[CONF_TOKEN])
                self._abort_if_unique_id_configured()
                title_token = user_input[CONF_TOKEN][:8]
                return self.async_create_entry(
                    title=f"Ravelli {title_token}",
                    data={
                        CONF_TOKEN: user_input[CONF_TOKEN],
                        CONF_BASE_URL: user_input[CONF_BASE_URL],
                    },
                )

        schema = vol.Schema({
            vol.Required(CONF_TOKEN): str,
            vol.Required(CONF_BASE_URL, default=DEFAULT_BASE_URL): str,
        })
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_import(self, import_config):
        return await self.async_step_user(import_config)

class OptionsFlow(config_entries.OptionsFlow):
    def __init__(self, entry):
        self.entry = entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="Options", data=user_input)

        schema = vol.Schema({
            vol.Required(CONF_SCAN_INTERVAL, default=self.entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)): int,
            vol.Required(CONF_BASE_URL, default=self.entry.options.get(CONF_BASE_URL, self.entry.data.get(CONF_BASE_URL))): str,
        })
        return self.async_show_form(step_id="init", data_schema=schema)

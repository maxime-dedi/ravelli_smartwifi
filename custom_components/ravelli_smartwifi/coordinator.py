from __future__ import annotations

import asyncio
from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_EMAIL, CONF_PASSWORD, CONF_BASE_URL, CONF_DEVICE_ID, CONF_SCAN_INTERVAL, DEFAULT_BASE_URL, DEFAULT_SCAN_INTERVAL, DOMAIN
from .api import RavelliSmartWifiClient

_LOGGER = logging.getLogger(__name__)

class RavelliCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.entry = entry
        session = async_get_clientsession(hass)
        email = entry.data[CONF_EMAIL]
        password = entry.data[CONF_PASSWORD]
        base_url = entry.options.get(CONF_BASE_URL, entry.data.get(CONF_BASE_URL, DEFAULT_BASE_URL))
        device_id = entry.options.get(CONF_DEVICE_ID, entry.data.get(CONF_DEVICE_ID))
        self.client = RavelliSmartWifiClient(session, base_url, email, password, device_id)
        scan_int = int(entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))
        super().__init__(
            hass,
            _LOGGER,
            name="Ravelli Smart Wi‑Fi Coordinator",
            update_interval=timedelta(seconds=scan_int),
        )

    async def _async_update_data(self):
        try:
            if not self.client._token:
                await self.client.async_login()
            return await self.client.async_get_status()
        except Exception as err:
            raise UpdateFailed(str(err)) from err

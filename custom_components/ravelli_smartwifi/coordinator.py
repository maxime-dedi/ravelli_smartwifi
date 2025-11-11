from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_TOKEN,
    CONF_BASE_URL,
    CONF_SCAN_INTERVAL,
    CONF_DEBUG,
    DEFAULT_BASE_URL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)
from .api import RavelliSmartWifiClient

_LOGGER = logging.getLogger(__name__)

class RavelliCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.entry = entry
        session = async_get_clientsession(hass)
        self.token = entry.data[CONF_TOKEN]
        self.base_url = entry.options.get(
            CONF_BASE_URL, entry.data.get(CONF_BASE_URL, DEFAULT_BASE_URL)
        )
        self.device_name = entry.title or f"Ravelli Stove {self.token[:4].upper()}"
        debug_enabled = entry.options.get(CONF_DEBUG, entry.data.get(CONF_DEBUG, False))
        self.client = RavelliSmartWifiClient(
            session, self.base_url, self.token, debug=debug_enabled
        )
        scan_int = int(entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))
        super().__init__(
            hass,
            _LOGGER,
            name="Ravelli Smart Wi‑Fi Coordinator",
            update_interval=timedelta(seconds=scan_int),
        )

    async def _async_update_data(self):
        try:
            return await self.client.async_get_status()
        except Exception as err:
            raise UpdateFailed(str(err)) from err

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
        self._pending_ignition = False
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
            data = await self.client.async_get_status()
        except Exception as err:
            raise UpdateFailed(str(err)) from err

        if self._pending_ignition:
            status_code = data.get("status_code")
            if status_code == 0:
                try:
                    await self.client.async_turn_on()
                except Exception as err:
                    _LOGGER.warning(
                        "Deferred ignition failed for stove %s: %s",
                        self.token[:4],
                        err,
                    )
                else:
                    self._pending_ignition = False
            elif data.get("is_on") and status_code not in (0, 6):
                # Stove already restarted via another command; clear the queue.
                self._pending_ignition = False

        data["pending_ignition"] = self._pending_ignition
        return data

    @property
    def status_code(self) -> int | None:
        data = self.data or {}
        return data.get("status_code")

    @property
    def is_final_cleaning(self) -> bool:
        return self.status_code == 6

    def queue_ignition_after_cleaning(self) -> None:
        if not self._pending_ignition:
            _LOGGER.info(
                "Ignition queued after cleaning for stove ending with %s",
                self.token[:4],
            )
        self._pending_ignition = True

    def cancel_pending_ignition(self) -> None:
        if self._pending_ignition:
            _LOGGER.info(
                "Cancelled pending ignition request for stove ending with %s",
                self.token[:4],
            )
        self._pending_ignition = False

    @property
    def pending_ignition(self) -> bool:
        return self._pending_ignition

from __future__ import annotations
import asyncio
import aiohttp
import logging
from typing import Any, Dict, Optional

_LOGGER = logging.getLogger(__name__)

class RavelliSmartWifiClient:
    """Minimal client for Ravelli Smart Wi‑Fi cloud (endpoints are placeholders)."""

    def __init__(self, session: aiohttp.ClientSession, base_url: str, email: str, password: str, device_id: str):
        self._session = session
        self._base = base_url.rstrip('/')
        self._email = email
        self._password = password
        self._device_id = device_id
        self._token: Optional[str] = None

    async def async_login(self) -> None:
        """Authenticate and store a bearer token.

        TODO: Replace endpoint and payload/keys with real values captured from app traffic.
        """
        url = f"{self._base}/api/login"
        payload = {"email": self._email, "password": self._password}
        _LOGGER.debug("POST %s %s", url, payload)
        async with self._session.post(url, json=payload, timeout=30) as resp:
            data = await resp.json(content_type=None)
            if resp.status in (200, 201) and "token" in data:
                self._token = data["token"]
                return
            raise RuntimeError(f"Login failed: {resp.status} {data}")

    def _headers(self) -> Dict[str, str]:
        hdr = {"Accept": "application/json"}
        if self._token:
            hdr["Authorization"] = f"Bearer {self._token}"
        return hdr

    async def async_get_status(self) -> Dict[str, Any]:
        """Get stove status.

        Expected (example):
        {"ambient_temp": 21.5, "set_temp": 22, "power": 3, "status": "heating", "is_on": true}
        TODO: Replace the path and keys according to real API.
        """
        url = f"{self._base}/api/devices/{self._device_id}/status"
        _LOGGER.debug("GET %s", url)
        async with self._session.get(url, headers=self._headers(), timeout=30) as resp:
            if resp.status != 200:
                raise RuntimeError(f"Status failed: {resp.status}")
            return await resp.json(content_type=None)

    async def async_turn_on(self) -> None:
        url = f"{self._base}/api/devices/{self._device_id}/actions/on"
        _LOGGER.debug("POST %s", url)
        async with self._session.post(url, headers=self._headers(), timeout=30) as resp:
            if resp.status not in (200, 204): raise RuntimeError("turn_on failed")

    async def async_turn_off(self) -> None:
        url = f"{self._base}/api/devices/{self._device_id}/actions/off"
        _LOGGER.debug("POST %s", url)
        async with self._session.post(url, headers=self._headers(), timeout=30) as resp:
            if resp.status not in (200, 204): raise RuntimeError("turn_off failed")

    async def async_set_temperature(self, temperature: float) -> None:
        url = f"{self._base}/api/devices/{self._device_id}/setpoint"
        _LOGGER.debug("POST %s temp=%s", url, temperature)
        async with self._session.post(url, headers=self._headers(), json={"set_temp": temperature}, timeout=30) as resp:
            if resp.status not in (200, 204): raise RuntimeError("set_temperature failed")

    async def async_set_power(self, power: int) -> None:
        url = f"{self._base}/api/devices/{self._device_id}/power"
        _LOGGER.debug("POST %s power=%s", url, power)
        async with self._session.post(url, headers=self._headers(), json={"power": power}, timeout=30) as resp:
            if resp.status not in (200, 204): raise RuntimeError("set_power failed")

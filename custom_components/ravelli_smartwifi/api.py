from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Dict
from urllib.parse import quote

import aiohttp

_LOGGER = logging.getLogger(__name__)


class RavelliSmartWifiClient:
    """Client for the CloudWiNet (Ravelli Smart Wi‑Fi) JSON API."""

    def __init__(self, session: aiohttp.ClientSession, base_url: str, token: str, debug: bool = False) -> None:
        self._session = session
        self._base = base_url.rstrip("/")
        self._token = token
        self._debug = debug

    def _url(self, endpoint: str, *extra: str, suffix: str = "") -> str:
        parts = [self._base, endpoint, quote(self._token, safe="")]
        if extra:
            parts.extend(quote(str(arg), safe="") for arg in extra)
        if suffix:
            parts[-1] = f"{parts[-1]}{suffix}"
        return "/".join(parts)

    def _redact(self, value: str) -> str:
        if not self._token:
            return value
        prefix = self._token[:4]
        return value.replace(self._token, f"{prefix}***")

    async def _request(self, endpoint: str, *extra: str, suffix: str = "") -> Dict[str, Any]:
        url = self._url(endpoint, *extra, suffix=suffix)
        _LOGGER.debug("GET %s", self._redact(url))
        async with self._session.get(url, timeout=30) as resp:
            text = await resp.text()
            if resp.status != 200:
                raise RuntimeError(f"{endpoint} failed: HTTP {resp.status} {text}")
            if self._debug:
                _LOGGER.debug("%s response: %s", endpoint, text)
            try:
                data = json.loads(text)
            except json.JSONDecodeError as err:
                raise RuntimeError(f"{endpoint} returned invalid JSON: {text}") from err
            return data

    @staticmethod
    def _ensure_success(endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not payload.get("Success", False):
            raise RuntimeError(
                f"{endpoint} failed: {payload.get('Error')} {payload.get('ErrorDescription')}"
            )
        return payload

    async def _call_result(self, endpoint: str, *extra: str) -> float:
        data = self._ensure_success(endpoint, await self._request(endpoint, *extra))
        if "Result" not in data:
            raise RuntimeError(f"{endpoint} response missing 'Result': {data}")
        return data["Result"]

    async def _call_status(self) -> Dict[str, Any]:
        return self._ensure_success("GetStatus", await self._request("GetStatus"))

    async def async_get_status(self) -> Dict[str, Any]:
        status_task = self._call_status()
        power_task = self._call_result("GetPower")
        set_temp_task = self._call_result("GetTemperature")
        ambient_temp_task = self._call_result("GetActualTemperature")

        status_data, power, set_temp, ambient_temp = await asyncio.gather(
            status_task, power_task, set_temp_task, ambient_temp_task
        )

        status_code = status_data.get("Status")
        status_text = status_data.get("StatusDescription")
        is_on = self._derive_is_on(status_code, status_text)

        summary = {
            "status_code": status_code,
            "status": status_text,
            "error": status_data.get("Error"),
            "error_description": status_data.get("ErrorDescription"),
            "power": power,
            "set_temp": set_temp,
            "ambient_temp": ambient_temp,
            "is_on": is_on,
        }
        if self._debug:
            _LOGGER.debug("Aggregated status: %s", summary)
        return summary

    async def async_turn_on(self) -> None:
        self._ensure_success("Ignit", await self._request("Ignit"))

    async def async_turn_off(self) -> None:
        self._ensure_success("Shutdown", await self._request("Shutdown"))

    async def async_set_temperature(self, temperature: float) -> None:
        target = int(round(float(temperature)))
        self._ensure_success(
            "SetTemperature",
            await self._request("SetTemperature", suffix=f";{target}"),
        )

    async def async_set_power(self, power: int) -> None:
        level = int(power)
        self._ensure_success(
            "SetPower",
            await self._request("SetPower", suffix=f";{level}"),
        )

    @staticmethod
    def _derive_is_on(status_code: int | None, status_text: str | None) -> bool:
        """Return True when the stove is actively heating or igniting."""
        if status_code in (None, 0):
            return False
        if status_code == 6:
            return False
        if status_text and status_code is None:
            normalized = status_text.upper()
            if any(keyword in normalized for keyword in ("CLEANING", "OFF", "STOP")):
                return False
        return True

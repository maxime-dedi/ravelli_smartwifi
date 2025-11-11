from __future__ import annotations

from homeassistant.components.number import NumberEntity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_BASE_URL, CONF_TOKEN, DOMAIN
from .coordinator import RavelliCoordinator

PARALLEL_UPDATES = 0


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator: RavelliCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([RavelliPowerLevelNumber(coordinator)], True)


class RavelliPowerLevelNumber(CoordinatorEntity, NumberEntity):
    _attr_has_entity_name = True
    _attr_name = "Power Level"
    _attr_native_min_value = 1
    _attr_native_max_value = 5
    _attr_native_step = 1
    _attr_icon = "mdi:fire"

    def __init__(self, coordinator: RavelliCoordinator) -> None:
        super().__init__(coordinator)
        self._client = coordinator.client

    @property
    def unique_id(self) -> str:
        return f"{self.coordinator.entry.data[CONF_TOKEN]}_power_level"

    @property
    def native_value(self):
        return self.coordinator.data.get("power")

    async def async_set_native_value(self, value):
        await self._client.async_set_power(int(value))
        await self.coordinator.async_request_refresh()

    @property
    def device_info(self) -> DeviceInfo:
        token = self.coordinator.entry.data[CONF_TOKEN]
        base_url = self.coordinator.entry.options.get(
            CONF_BASE_URL, self.coordinator.entry.data.get(CONF_BASE_URL)
        )
        return DeviceInfo(
            identifiers={(DOMAIN, token)},
            manufacturer="Ravelli",
            model="Smart Wi‑Fi",
            name=f"Ravelli Stove {token[:4].upper()}",
            configuration_url=base_url,
        )

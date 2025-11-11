from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import RavelliCoordinator

PARALLEL_UPDATES = 0
POWER_OPTIONS = ["1", "2", "3", "4", "5"]


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator: RavelliCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([RavelliPowerLevelSelect(coordinator)], True)


class RavelliPowerLevelSelect(CoordinatorEntity, SelectEntity):
    _attr_has_entity_name = True
    _attr_name = "Power Level"
    _attr_icon = "mdi:fire"
    _attr_options = POWER_OPTIONS
    _attr_translation_key = "power_level"

    def __init__(self, coordinator: RavelliCoordinator) -> None:
        super().__init__(coordinator)
        self._client = coordinator.client

    @property
    def unique_id(self) -> str:
        return f"{self.coordinator.token}_power_level"

    @property
    def current_option(self) -> str | None:
        power = self.coordinator.data.get("power")
        if power is None:
            return None
        return str(int(power))

    async def async_select_option(self, option: str) -> None:
        if option not in POWER_OPTIONS:
            raise ValueError(f"Unsupported power level {option}")
        await self._client.async_set_power(int(option))
        await self.coordinator.async_request_refresh()

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.token)},
            manufacturer="Ravelli",
            model="Smart Wi‑Fi",
            name=self.coordinator.device_name,
            configuration_url=self.coordinator.base_url,
        )

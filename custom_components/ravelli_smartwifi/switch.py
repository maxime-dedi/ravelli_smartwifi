from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import RavelliCoordinator

PARALLEL_UPDATES = 0


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator: RavelliCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([RavelliStoveSwitch(coordinator)], True)


class RavelliStoveSwitch(CoordinatorEntity, SwitchEntity):
    _attr_has_entity_name = False

    def __init__(self, coordinator: RavelliCoordinator) -> None:
        super().__init__(coordinator)
        self._client = coordinator.client
        self._attr_name = coordinator.device_name

    @property
    def unique_id(self) -> str:
        return f"{self.coordinator.token}_switch"

    @property
    def is_on(self) -> bool:
        return bool(self.coordinator.data.get("is_on"))

    async def async_turn_on(self, **kwargs):
        if self.coordinator.is_final_cleaning:
            self.coordinator.queue_ignition_after_cleaning()
        else:
            self.coordinator.cancel_pending_ignition()
        await self._client.async_turn_on()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        self.coordinator.cancel_pending_ignition()
        await self._client.async_turn_off()
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

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data or {}
        return {
            "status": data.get("status"),
            "status_code": data.get("status_code"),
            "pending_ignition": self.coordinator.pending_ignition,
        }

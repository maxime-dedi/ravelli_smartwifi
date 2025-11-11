from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.exceptions import HomeAssistantError
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

    def _ensure_action_allowed(self) -> None:
        if self.coordinator.is_final_cleaning:
            raise HomeAssistantError(
                "Le poêle termine son extinction (FINAL CLEANING). "
                "Attendez la fin du cycle avant d'envoyer une nouvelle commande."
            )

    async def async_turn_on(self, **kwargs):
        self._ensure_action_allowed()
        await self._client.async_turn_on()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        self._ensure_action_allowed()
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

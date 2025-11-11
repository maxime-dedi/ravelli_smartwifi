from __future__ import annotations

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import ClimateEntityFeature, HVACMode
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import RavelliCoordinator

PARALLEL_UPDATES = 0

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator: RavelliCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([RavelliClimate(coordinator)], True)

class RavelliClimate(CoordinatorEntity, ClimateEntity):
    _attr_has_entity_name = True
    _attr_name = "Stove"
    _attr_hvac_modes = [HVACMode.HEAT, HVACMode.OFF]
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_min_temp = 5
    _attr_max_temp = 30

    def __init__(self, coordinator: RavelliCoordinator):
        super().__init__(coordinator)
        self._client = coordinator.client

    @property
    def unique_id(self):
        return f"{self.coordinator.token}_climate"

    @property
    def current_temperature(self):
        return self.coordinator.data.get("ambient_temp")

    @property
    def target_temperature(self):
        return self.coordinator.data.get("set_temp")

    @property
    def hvac_mode(self):
        return HVACMode.HEAT if self.coordinator.data.get("is_on") else HVACMode.OFF

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.token)},
            manufacturer="Ravelli",
            model="Smart Wi‑Fi",
            name=self.coordinator.device_name,
            configuration_url=self.coordinator.base_url,
        )

    async def async_set_temperature(self, **kwargs):
        temp = kwargs.get(ATTR_TEMPERATURE)
        if temp is not None:
            await self._client.async_set_temperature(float(temp))
            await self.coordinator.async_request_refresh()

    async def async_set_hvac_mode(self, hvac_mode):
        if hvac_mode == HVACMode.OFF:
            self.coordinator.cancel_pending_ignition()
            await self._client.async_turn_off()
        else:
            if self.coordinator.is_final_cleaning:
                self.coordinator.queue_ignition_after_cleaning()
            else:
                self.coordinator.cancel_pending_ignition()
            await self._client.async_turn_on()
        await self.coordinator.async_request_refresh()

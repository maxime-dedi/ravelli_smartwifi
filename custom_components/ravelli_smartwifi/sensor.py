from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import UnitOfTemperature
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import RavelliCoordinator

SENSORS = (
    ("ambient_temp", "Ambient Temperature", UnitOfTemperature.CELSIUS),
    ("set_temp", "Target Temperature", UnitOfTemperature.CELSIUS),
    ("power", "Power Level", None),
    ("status", "Status", None),
    ("status_code", "Status Code", None),
    ("error", "Error Code", None),
    ("error_description", "Error Description", None),
    ("pending_ignition", "Pending Ignition", None),
)

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator: RavelliCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [RavelliSensor(coordinator, key, name, unit) for key, name, unit in SENSORS]
    async_add_entities(entities, True)

class RavelliSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator: RavelliCoordinator, key: str, name: str, unit):
        super().__init__(coordinator)
        self._key = key
        self._attr_name = name
        self._unit = unit

    @property
    def unique_id(self):
        return f"{self.coordinator.token}_{self._key}"

    @property
    def native_unit_of_measurement(self):
        return self._unit

    @property
    def native_value(self):
        return self.coordinator.data.get(self._key)

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.token)},
            manufacturer="Ravelli",
            model="Smart Wi‑Fi",
            name=self.coordinator.device_name,
            configuration_url=self.coordinator.base_url,
        )

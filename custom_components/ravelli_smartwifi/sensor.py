from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import UnitOfTemperature
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import RavelliCoordinator

SENSORS = (
    ("ambient_temp", "Ambient Temperature", "ambient_temp", UnitOfTemperature.CELSIUS),
    ("set_temp", "Target Temperature", "set_temp", UnitOfTemperature.CELSIUS),
    ("power", "Power Level", "power", None),
    ("status", "Status", "status", None),
    ("status_code", "Status Code", "status_code", None),
    ("error", "Error Code", "error", None),
    ("error_description", "Error Description", "error_description", None),
    ("pending_ignition", "Pending Ignition", "pending_ignition", None),
)

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator: RavelliCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [
        RavelliSensor(coordinator, key, name, translation_key, unit)
        for key, name, translation_key, unit in SENSORS
    ]
    async_add_entities(entities, True)

class RavelliSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: RavelliCoordinator,
        key: str,
        name: str,
        translation_key: str,
        unit,
    ):
        super().__init__(coordinator)
        self._key = key
        self._attr_name = name
        self._attr_translation_key = translation_key
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

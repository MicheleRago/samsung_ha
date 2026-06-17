import logging
from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the binary_sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    binary_sensors = []
    
    for device_id, device_data in coordinator.data.items():
        components = device_data.get("status", {})
        device_info = device_data.get("device_info", {})
        device_name = device_info.get("name", "Samsung Appliance")
        
        for comp_name, status in components.items():
            name = f"{device_name} ({comp_name})" if comp_name != "main" else device_name

            if "contactSensor" in status:
                binary_sensors.append(GenericContactSensor(coordinator, device_id, comp_name, name))

    async_add_entities(binary_sensors)

class GenericContactSensor(CoordinatorEntity, BinarySensorEntity):
    """Generic contact sensor."""

    def __init__(self, coordinator, device_id, component, device_name):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._component = component
        self._device_name = device_name
        
        comp_prefix = f"_{component}" if component != "main" else ""
        self._attr_unique_id = f"{device_id}{comp_prefix}_contactSensor"
        
        if component == "cooler":
            self._attr_name = "Fridge Door"
        elif component == "freezer":
            self._attr_name = "Freezer Door"
        else:
            self._attr_name = "Door"
            
        self._attr_device_class = BinarySensorDeviceClass.DOOR
        self._attr_has_entity_name = True

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._device_name.replace(f" ({self._component})", ""),
            "manufacturer": "Samsung",
        }

    @property
    def is_on(self):
        """Return true if the binary sensor is on (door open)."""
        data = self.coordinator.data.get(self._device_id, {}).get("status", {}).get(self._component, {})
        if not data:
            return None
        return data.get("contactSensor", {}).get("contact", {}).get("value") == "open"

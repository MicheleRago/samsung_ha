import logging
from dataclasses import dataclass

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorEntityDescription, BinarySensorDeviceClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

@dataclass(kw_only=True)
class SamsungBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Class describing Samsung binary sensor entities."""
    capability: str
    attribute: str

BINARY_SENSOR_TYPES: tuple[SamsungBinarySensorEntityDescription, ...] = (
    SamsungBinarySensorEntityDescription(
        key="contact_sensor",
        name="Door",
        capability="contactSensor",
        attribute="contact",
        device_class=BinarySensorDeviceClass.DOOR,
    ),
)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the binary_sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    binary_sensors = []
    
    for device_id, device_data in coordinator.data.items():
        components = device_data.get("status", {})
        device_info = device_data.get("device_info", {})
        device_name = device_info.get("name", "Samsung Appliance")
        
        for comp_name, status in components.items():
            name_prefix = f"{device_name} ({comp_name})" if comp_name != "main" else device_name

            for description in BINARY_SENSOR_TYPES:
                if description.capability in status:
                    binary_sensors.append(GenericBinarySensor(coordinator, device_id, comp_name, name_prefix, description))

    async_add_entities(binary_sensors)


class GenericBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Generic binary sensor."""
    entity_description: SamsungBinarySensorEntityDescription

    def __init__(self, coordinator, device_id, component, device_name, description: SamsungBinarySensorEntityDescription):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._device_id = device_id
        self._component = component
        self._device_name = device_name
        
        comp_prefix = f"_{component}" if component != "main" else ""
        self._attr_unique_id = f"{device_id}{comp_prefix}_{description.capability}"
        
        # Override name dynamically based on component for doors
        if description.capability == "contactSensor":
            if component == "cooler":
                self._attr_name = "Fridge Door"
            elif component == "freezer":
                self._attr_name = "Freezer Door"
            else:
                self._attr_name = description.name
        else:
            self._attr_name = description.name
            
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
        """Return true if the binary sensor is on."""
        data = self.coordinator.data.get(self._device_id, {}).get("status", {}).get(self._component, {})
        if not data:
            return None
        
        val = data.get(self.entity_description.capability, {}).get(self.entity_description.attribute, {}).get("value")
        
        if self.entity_description.capability == "contactSensor":
            return val == "open"
            
        if isinstance(val, bool):
            return val
            
        return val == "on"

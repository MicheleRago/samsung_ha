import logging
from dataclasses import dataclass
from typing import Optional

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN, CAP_OPERATING_STATE, CAP_DISHWASHER_OPERATION, CAP_REMOTE_CONTROL,
    CAP_WASHER_OPERATING_STATE, CAP_DRYER_OPERATING_STATE, CAP_OVEN_OPERATING_STATE,
    CAP_TEMPERATURE_MEASUREMENT
)

_LOGGER = logging.getLogger(__name__)

@dataclass(kw_only=True)
class SamsungSensorEntityDescription(SensorEntityDescription):
    """Class describing Samsung sensor entities."""
    capability: str
    attribute: str


SENSOR_TYPES: tuple[SamsungSensorEntityDescription, ...] = (
    SamsungSensorEntityDescription(
        key="machine_state",
        name="Machine State",
        icon="mdi:washing-machine",
        capability=CAP_OPERATING_STATE,
        attribute="machineState",
    ),
    SamsungSensorEntityDescription(
        key="dishwasher_job_state",
        name="Job State",
        icon="mdi:state-machine",
        capability=CAP_OPERATING_STATE,
        attribute="dishwasherJobState",
    ),
    SamsungSensorEntityDescription(
        key="washer_state",
        name="Washer State",
        icon="mdi:washing-machine",
        capability=CAP_WASHER_OPERATING_STATE,
        attribute="machineState",
    ),
    SamsungSensorEntityDescription(
        key="dryer_state",
        name="Dryer State",
        icon="mdi:tumble-dryer",
        capability=CAP_DRYER_OPERATING_STATE,
        attribute="machineState",
    ),
    SamsungSensorEntityDescription(
        key="oven_state",
        name="Oven State",
        icon="mdi:stove",
        capability=CAP_OVEN_OPERATING_STATE,
        attribute="machineState",
    ),
    SamsungSensorEntityDescription(
        key="remaining_time",
        name="Remaining Time",
        icon="mdi:timer-outline",
        capability=CAP_DISHWASHER_OPERATION,
        attribute="remainingTimeStr",
    ),
    SamsungSensorEntityDescription(
        key="remote_control",
        name="Remote Control",
        icon="mdi:remote",
        capability=CAP_REMOTE_CONTROL,
        attribute="remoteControlEnabled",
    ),
    SamsungSensorEntityDescription(
        key="temperature",
        name="Temperature",
        icon="mdi:thermometer",
        capability=CAP_TEMPERATURE_MEASUREMENT,
        attribute="temperature",
        device_class="temperature",
        native_unit_of_measurement="°C",
    ),
)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    sensors = []
    
    for device_id, device_data in coordinator.data.items():
        components = device_data.get("status", {})
        device_info = device_data.get("device_info", {})
        device_name = device_info.get("name", "Samsung Appliance")
        
        for comp_name, status in components.items():
            name_prefix = f"{device_name} ({comp_name})" if comp_name != "main" else device_name
            
            for description in SENSOR_TYPES:
                if description.capability in status:
                    sensors.append(GenericStateSensor(coordinator, device_id, comp_name, name_prefix, description))

    async_add_entities(sensors)


class GenericStateSensor(CoordinatorEntity, SensorEntity):
    """Generic sensor for device state."""
    entity_description: SamsungSensorEntityDescription

    def __init__(self, coordinator, device_id, component, device_name, description: SamsungSensorEntityDescription):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._device_id = device_id
        self._component = component
        self._device_name = device_name
        
        comp_prefix = f"_{component}" if component != "main" else ""
        self._attr_unique_id = f"{device_id}{comp_prefix}_{description.capability}_{description.attribute}"
        
        # Add a prefix to the name based on the component if not main
        if component != "main":
            self._attr_name = f"{component.capitalize()} {description.name}"
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
    def native_value(self):
        """Return the state of the sensor."""
        data = self.coordinator.data.get(self._device_id, {}).get("status", {}).get(self._component, {})
        if not data:
            return None
            
        val = data.get(self.entity_description.capability, {}).get(self.entity_description.attribute, {}).get("value")
        
        if isinstance(val, dict) and "value" in val:
            val = val.get("value")
            
        return val

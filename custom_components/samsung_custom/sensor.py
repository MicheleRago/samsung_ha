import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN, CAP_OPERATING_STATE, CAP_DISHWASHER_OPERATION, CAP_REMOTE_CONTROL,
    CAP_WASHER_OPERATING_STATE, CAP_DRYER_OPERATING_STATE, CAP_OVEN_OPERATING_STATE,
    CAP_TEMPERATURE_MEASUREMENT
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    sensors = []
    
    for device_id, device_data in coordinator.data.items():
        components = device_data.get("status", {})
        device_info = device_data.get("device_info", {})
        device_name = device_info.get("name", "Samsung Appliance")
        
        for comp_name, status in components.items():
            name = f"{device_name} ({comp_name})" if comp_name != "main" else device_name

            if CAP_OPERATING_STATE in status:
                sensors.append(GenericStateSensor(coordinator, device_id, comp_name, name, CAP_OPERATING_STATE, "machineState", "Machine State", "mdi:washing-machine"))
                sensors.append(GenericStateSensor(coordinator, device_id, comp_name, name, CAP_OPERATING_STATE, "dishwasherJobState", "Job State", "mdi:state-machine"))
            
            if CAP_WASHER_OPERATING_STATE in status:
                sensors.append(GenericStateSensor(coordinator, device_id, comp_name, name, CAP_WASHER_OPERATING_STATE, "machineState", "Washer State", "mdi:washing-machine"))
                
            if CAP_DRYER_OPERATING_STATE in status:
                sensors.append(GenericStateSensor(coordinator, device_id, comp_name, name, CAP_DRYER_OPERATING_STATE, "machineState", "Dryer State", "mdi:tumble-dryer"))
                
            if CAP_OVEN_OPERATING_STATE in status:
                sensors.append(GenericStateSensor(coordinator, device_id, comp_name, name, CAP_OVEN_OPERATING_STATE, "machineState", "Oven State", "mdi:stove"))
                
            if CAP_DISHWASHER_OPERATION in status:
                sensors.append(GenericStateSensor(coordinator, device_id, comp_name, name, CAP_DISHWASHER_OPERATION, "remainingTimeStr", "Remaining Time", "mdi:timer-outline"))
                
            if CAP_REMOTE_CONTROL in status:
                sensors.append(GenericStateSensor(coordinator, device_id, comp_name, name, CAP_REMOTE_CONTROL, "remoteControlEnabled", "Remote Control", "mdi:remote"))
                
            if CAP_TEMPERATURE_MEASUREMENT in status:
                sensors.append(GenericStateSensor(coordinator, device_id, comp_name, name, CAP_TEMPERATURE_MEASUREMENT, "temperature", "Temperature", "mdi:thermometer"))

    async_add_entities(sensors)

class GenericStateSensor(CoordinatorEntity, SensorEntity):
    """Generic sensor for device state."""

    def __init__(self, coordinator, device_id, component, device_name, capability, attribute, name, icon):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._device_id = device_id
        self._component = component
        self._device_name = device_name
        self._capability = capability
        self._attribute = attribute
        
        comp_prefix = f"_{component}" if component != "main" else ""
        self._attr_unique_id = f"{device_id}{comp_prefix}_{capability}_{attribute}"
        
        self._attr_name = name
        self._attr_icon = icon
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
        return data.get(self._capability, {}).get(self._attribute, {}).get("value")



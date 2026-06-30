from dataclasses import dataclass

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN, CAP_OPERATING_STATE, CAP_DISHWASHER_OPERATION, CAP_REMOTE_CONTROL,
    CAP_WASHER_OPERATING_STATE, CAP_DRYER_OPERATING_STATE, CAP_OVEN_OPERATING_STATE,
    CAP_TEMPERATURE_MEASUREMENT, OVEN_JOB_STATE_MAP, DISHWASHER_JOB_STATE_MAP
)
from .entity import (
    capability_value,
    component_prefix,
    component_status,
    iter_component_statuses,
    samsung_device_info,
)

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
        key="oven_job_state",
        name="Oven Job State",
        icon="mdi:state-machine",
        capability=CAP_OVEN_OPERATING_STATE,
        attribute="ovenJobState",
    ),
    SamsungSensorEntityDescription(
        key="oven_completion_time",
        name="Oven Completion Time",
        icon="mdi:clock",
        capability=CAP_OVEN_OPERATING_STATE,
        attribute="completionTime",
        device_class="timestamp",
    ),
    SamsungSensorEntityDescription(
        key="dishwasher_completion_time",
        name="Dishwasher Completion Time",
        icon="mdi:clock",
        capability=CAP_OPERATING_STATE,
        attribute="completionTime",
        device_class="timestamp",
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
    
    for device_id, component, status, name_prefix in iter_component_statuses(coordinator):
        for description in SENSOR_TYPES:
            if description.capability in status:
                sensors.append(GenericStateSensor(coordinator, device_id, component, name_prefix, description))

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
        
        comp_prefix = component_prefix(component)
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
        return samsung_device_info(self._device_id, self._device_name, self._component)

    @property
    def native_value(self):
        """Return the state of the sensor."""
        data = component_status(self.coordinator, self._device_id, self._component)
        if not data:
            return None

        val = capability_value(
            data,
            self.entity_description.capability,
            self.entity_description.attribute,
        )
            
        # Translate based on attribute
        if self.entity_description.attribute == "ovenJobState" and val in OVEN_JOB_STATE_MAP:
            return OVEN_JOB_STATE_MAP[val]
        if self.entity_description.attribute == "dishwasherJobState" and val in DISHWASHER_JOB_STATE_MAP:
            return DISHWASHER_JOB_STATE_MAP[val]
        if self.entity_description.device_class == "timestamp" and val:
            from homeassistant.util import dt as dt_util
            try:
                parsed = dt_util.parse_datetime(val)
                if parsed is not None:
                    return parsed
            except Exception:
                pass
                
        return val

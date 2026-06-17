import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CAP_OPERATING_STATE, CAP_DISHWASHER_OPERATION, CAP_REMOTE_CONTROL

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    sensors = [
        DishwasherStateSensor(coordinator),
        DishwasherRemainingTimeSensor(coordinator),
        DishwasherJobStateSensor(coordinator),
        DishwasherRemoteControlSensor(coordinator),
    ]
    async_add_entities(sensors)

class SmartThingsSensorBase(CoordinatorEntity, SensorEntity):
    """Base class for SmartThings sensors."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_has_entity_name = True

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.api.device_id)},
            "name": "Samsung Dishwasher",
            "manufacturer": "Samsung",
        }

class DishwasherStateSensor(SmartThingsSensorBase):
    """Sensor for machine state."""

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.api.device_id}_machine_state"
        self._attr_name = "Machine State"
        self._attr_icon = "mdi:washing-machine"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        data = self.coordinator.data
        if not data:
            return None
        return data.get(CAP_OPERATING_STATE, {}).get("machineState", {}).get("value")

class DishwasherRemainingTimeSensor(SmartThingsSensorBase):
    """Sensor for remaining time."""

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.api.device_id}_remaining_time"
        self._attr_name = "Remaining Time"
        self._attr_icon = "mdi:timer-outline"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        data = self.coordinator.data
        if not data:
            return None
        return data.get(CAP_DISHWASHER_OPERATION, {}).get("remainingTimeStr", {}).get("value")

class DishwasherJobStateSensor(SmartThingsSensorBase):
    """Sensor for job state."""

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.api.device_id}_job_state"
        self._attr_name = "Job State"
        self._attr_icon = "mdi:state-machine"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        data = self.coordinator.data
        if not data:
            return None
        return data.get(CAP_OPERATING_STATE, {}).get("dishwasherJobState", {}).get("value")

class DishwasherRemoteControlSensor(SmartThingsSensorBase):
    """Sensor for remote control status."""

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.api.device_id}_remote_control"
        self._attr_name = "Remote Control"
        self._attr_icon = "mdi:remote"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        data = self.coordinator.data
        if not data:
            return None
        return data.get(CAP_REMOTE_CONTROL, {}).get("remoteControlEnabled", {}).get("value")

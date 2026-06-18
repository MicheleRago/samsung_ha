import logging
from dataclasses import dataclass
from typing import Optional

from homeassistant.components.number import NumberEntity, NumberEntityDescription, NumberDeviceClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CAP_THERMOSTAT_COOLING

_LOGGER = logging.getLogger(__name__)

@dataclass(kw_only=True)
class SamsungNumberEntityDescription(NumberEntityDescription):
    """Class describing Samsung number entities."""
    capability: str
    attribute: str
    command: str
    native_min_value: float = -30.0
    native_max_value: float = 30.0
    native_step: float = 1.0


NUMBER_TYPES: tuple[SamsungNumberEntityDescription, ...] = (
    SamsungNumberEntityDescription(
        key="cooling_setpoint",
        name="Target Temperature",
        icon="mdi:thermometer",
        capability=CAP_THERMOSTAT_COOLING,
        attribute="coolingSetpoint",
        command="setCoolingSetpoint",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement="°C",
        native_min_value=-25.0,
        native_max_value=10.0,
        native_step=1.0,
    ),
    SamsungNumberEntityDescription(
        key="oven_setpoint",
        name="Oven Target Temperature",
        icon="mdi:thermometer",
        capability="ovenSetpoint",
        attribute="ovenSetpoint",
        command="setOvenSetpoint",
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement="°C",
        native_min_value=40.0,
        native_max_value=250.0,
        native_step=5.0,
    ),
)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the number platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    numbers = []
    
    for device_id, device_data in coordinator.data.items():
        components = device_data.get("status", {})
        device_info = device_data.get("device_info", {})
        device_name = device_info.get("name", "Samsung Appliance")
        
        for comp_name, status in components.items():
            name_prefix = f"{device_name} ({comp_name})" if comp_name != "main" else device_name

            for description in NUMBER_TYPES:
                if description.capability in status:
                    numbers.append(GenericNumber(coordinator, device_id, comp_name, name_prefix, description))
                    
            if "ovenOperatingState" in status:
                numbers.append(VirtualCookTimeNumber(coordinator, device_id, comp_name, name_prefix))

    async_add_entities(numbers)


class GenericNumber(CoordinatorEntity, NumberEntity):
    """Generic number entity."""
    entity_description: SamsungNumberEntityDescription

    def __init__(self, coordinator, device_id, component, device_name, description: SamsungNumberEntityDescription):
        """Initialize the number entity."""
        super().__init__(coordinator)
        self.entity_description = description
        self._device_id = device_id
        self._component = component
        self._device_name = device_name
        
        comp_prefix = f"_{component}" if component != "main" else ""
        self._attr_unique_id = f"{device_id}{comp_prefix}_{description.capability}_{description.attribute}"
        
        # Override name dynamically based on component for fridges
        if component == "cooler":
            self._attr_name = "Fridge Target Temp"
        elif component == "freezer":
            self._attr_name = "Freezer Target Temp"
        elif component != "main":
            self._attr_name = f"{component.capitalize()} {description.name}"
        else:
            self._attr_name = description.name
            
        self._attr_has_entity_name = True
        self._attr_native_min_value = description.native_min_value
        self._attr_native_max_value = description.native_max_value
        self._attr_native_step = description.native_step

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._device_name.replace(f" ({self._component})", ""),
            "manufacturer": "Samsung",
        }

    @property
    def native_min_value(self) -> float:
        """Return the minimum value."""
        data = self.coordinator.data.get(self._device_id, {}).get("status", {}).get(self._component, {})
        if data:
            range_data = data.get(self.entity_description.capability, {}).get("coolingSetpointRange", {}).get("value")
            if isinstance(range_data, list) and len(range_data) >= 1:
                try:
                    return float(range_data[0])
                except (ValueError, TypeError):
                    pass
            elif isinstance(range_data, dict) and "minimum" in range_data:
                try:
                    return float(range_data["minimum"])
                except (ValueError, TypeError):
                    pass
        return self._attr_native_min_value

    @property
    def native_max_value(self) -> float:
        """Return the maximum value."""
        data = self.coordinator.data.get(self._device_id, {}).get("status", {}).get(self._component, {})
        if data:
            range_data = data.get(self.entity_description.capability, {}).get("coolingSetpointRange", {}).get("value")
            if isinstance(range_data, list) and len(range_data) >= 2:
                try:
                    return float(range_data[1])
                except (ValueError, TypeError):
                    pass
            elif isinstance(range_data, dict) and "maximum" in range_data:
                try:
                    return float(range_data["maximum"])
                except (ValueError, TypeError):
                    pass
        return self._attr_native_max_value

    @property
    def native_value(self):
        """Return the state of the number."""
        data = self.coordinator.data.get(self._device_id, {}).get("status", {}).get(self._component, {})
        if not data:
            return None
        
        # If it's ovenSetpoint, check local cache first (if oven is off)
        if self.entity_description.capability == "ovenSetpoint":
            cache_key = f"{self._device_id}_pending_oven_state"
            if cache_key in self.coordinator.hass.data.get(DOMAIN, {}):
                cached_temp = self.coordinator.hass.data[DOMAIN][cache_key].get("temp")
                if cached_temp is not None:
                    machine_state = data.get("ovenOperatingState", {}).get("machineState", {}).get("value")
                    job_state = data.get("ovenOperatingState", {}).get("ovenJobState", {}).get("value")
                    if machine_state not in ["running", "paused"] and job_state in ["ready", "finished", None]:
                        return float(cached_temp)

        val = data.get(self.entity_description.capability, {}).get(self.entity_description.attribute, {}).get("value")
        
        if val is None:
            return None
            
        try:
            return float(val)
        except (ValueError, TypeError):
            return None

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        import asyncio
        
        # Cache the selected temp for the start button
        if self.entity_description.capability == "ovenSetpoint":
            cache_key = f"{self._device_id}_pending_oven_state"
            if cache_key not in self.hass.data[DOMAIN]:
                self.hass.data[DOMAIN][cache_key] = {}
            self.hass.data[DOMAIN][cache_key]["temp"] = value
            
            # Check if oven is running. If not, don't send the API command yet.
            data = self.coordinator.data.get(self._device_id, {}).get("status", {}).get(self._component, {})
            machine_state = data.get("ovenOperatingState", {}).get("machineState", {}).get("value")
            job_state = data.get("ovenOperatingState", {}).get("ovenJobState", {}).get("value")
            if machine_state not in ["running", "paused"] and job_state in ["ready", "finished", None]:
                # Just cache it and write state
                self.async_write_ha_state()
                return
            
        await self.coordinator.api.execute_command(
            self._device_id, 
            self._component, 
            self.entity_description.capability, 
            self.entity_description.command, 
            [value]
        )
        await asyncio.sleep(2)
        await self.coordinator.async_request_refresh()

class VirtualCookTimeNumber(CoordinatorEntity, NumberEntity):
    """Virtual number entity for oven cook time."""
    
    def __init__(self, coordinator, device_id, component, device_name):
        super().__init__(coordinator)
        self._device_id = device_id
        self._component = component
        self._device_name = device_name
        self._attr_unique_id = f"{device_id}_oven_cook_time"
        self._attr_name = "Oven Cook Time"
        self._attr_icon = "mdi:timer-outline"
        self._attr_has_entity_name = True
        self._attr_native_min_value = 1.0
        self._attr_native_max_value = 600.0
        self._attr_native_step = 1.0
        self._attr_native_unit_of_measurement = "min"
        
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
        """Return the state of the number."""
        cache_key = f"{self._device_id}_pending_oven_state"
        if cache_key in self.hass.data.get(DOMAIN, {}):
            return self.hass.data[DOMAIN][cache_key].get("cook_time", 30.0)
        return 30.0

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value in local cache."""
        cache_key = f"{self._device_id}_pending_oven_state"
        if cache_key not in self.hass.data[DOMAIN]:
            self.hass.data[DOMAIN][cache_key] = {}
        self.hass.data[DOMAIN][cache_key]["cook_time"] = value
        self.async_write_ha_state()

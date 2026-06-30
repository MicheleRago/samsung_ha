from dataclasses import dataclass

from homeassistant.components.number import NumberEntity, NumberEntityDescription, NumberDeviceClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    CAP_OVEN_SETPOINT,
    CAP_THERMOSTAT_COOLING,
    OVEN_OPERATING_STATE_CAPABILITIES,
)
from .entity import (
    capability_value,
    component_prefix,
    component_status,
    iter_component_statuses,
    refresh_after_command,
    samsung_device_info,
)
from .oven import (
    DEFAULT_OVEN_COOK_TIME,
    cached_oven_setting,
    cache_oven_setting,
    oven_is_waiting_for_start,
)

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
        capability=CAP_OVEN_SETPOINT,
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
    
    for device_id, component, status, name_prefix in iter_component_statuses(coordinator):
        for description in NUMBER_TYPES:
            if description.capability in status:
                numbers.append(GenericNumber(coordinator, device_id, component, name_prefix, description))

        if any(capability in status for capability in OVEN_OPERATING_STATE_CAPABILITIES):
            numbers.append(VirtualCookTimeNumber(coordinator, device_id, component, name_prefix))

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
        
        comp_prefix = component_prefix(component)
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
        return samsung_device_info(self._device_id, self._device_name, self._component)

    @property
    def native_min_value(self) -> float:
        """Return the minimum value."""
        data = component_status(self.coordinator, self._device_id, self._component)
        if data:
            range_data = capability_value(
                data,
                self.entity_description.capability,
                "coolingSetpointRange",
            )
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
        data = component_status(self.coordinator, self._device_id, self._component)
        if data:
            range_data = capability_value(
                data,
                self.entity_description.capability,
                "coolingSetpointRange",
            )
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
        data = component_status(self.coordinator, self._device_id, self._component)
        if not data:
            return None
        
        # If it's ovenSetpoint, check local cache first (if oven is off)
        if self.entity_description.capability == CAP_OVEN_SETPOINT:
            cached_temp = cached_oven_setting(self.coordinator.hass, self._device_id, "temp")
            if cached_temp is not None and oven_is_waiting_for_start(data):
                return float(cached_temp)

        val = capability_value(
            data,
            self.entity_description.capability,
            self.entity_description.attribute,
        )
        
        if val is None:
            return None
            
        try:
            return float(val)
        except (ValueError, TypeError):
            return None

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        # Cache the selected temp for the start button
        if self.entity_description.capability == CAP_OVEN_SETPOINT:
            cache_oven_setting(self.hass, self._device_id, "temp", value)
            
            # Check if oven is running. If not, don't send the API command yet.
            data = component_status(self.coordinator, self._device_id, self._component)
            if oven_is_waiting_for_start(data):
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
        await refresh_after_command(self.coordinator)

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
        return samsung_device_info(self._device_id, self._device_name, self._component)

    @property
    def native_value(self):
        """Return the state of the number."""
        return cached_oven_setting(self.hass, self._device_id, "cook_time", DEFAULT_OVEN_COOK_TIME)

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value in local cache."""
        cache_oven_setting(self.hass, self._device_id, "cook_time", value)
        self.async_write_ha_state()

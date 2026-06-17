import logging
from homeassistant.components.select import SelectEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CAP_WASHING_COURSE, CAP_WASHER_COURSE, CAP_DRYER_COURSE

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the select platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    selects = []
    
    for device_id, device_data in coordinator.data.items():
        components = device_data.get("status", {})
        device_info = device_data.get("device_info", {})
        device_name = device_info.get("name", "Samsung Appliance")
        
        for comp_name, status in components.items():
            name = f"{device_name} ({comp_name})" if comp_name != "main" else device_name

            if CAP_WASHING_COURSE in status:
                selects.append(GenericCourseSelect(coordinator, device_id, comp_name, name, CAP_WASHING_COURSE, "washingCourse", "setWashingCourse", "Dishwasher Course"))
                
            if CAP_WASHER_COURSE in status:
                selects.append(GenericCourseSelect(coordinator, device_id, comp_name, name, CAP_WASHER_COURSE, "washerCycle", "setWasherCycle", "Washer Course"))
                
            if CAP_DRYER_COURSE in status:
                selects.append(GenericCourseSelect(coordinator, device_id, comp_name, name, CAP_DRYER_COURSE, "dryerCycle", "setDryerCycle", "Dryer Course"))
            
    async_add_entities(selects)

class GenericCourseSelect(CoordinatorEntity, SelectEntity):
    """Select for washing/drying course."""

    def __init__(self, coordinator, device_id, component, device_name, capability, attribute, command, name):
        super().__init__(coordinator)
        self._device_id = device_id
        self._component = component
        self._device_name = device_name
        self._capability = capability
        self._attribute = attribute
        self._command = command
        
        comp_prefix = f"_{component}" if component != "main" else ""
        self._attr_unique_id = f"{device_id}{comp_prefix}_{capability}"
        self._attr_name = name
        self._attr_has_entity_name = True

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._device_name.replace(f" ({self._component})", ""),
            "manufacturer": "Samsung",
        }

    @property
    def current_option(self):
        """Return the current selected option."""
        data = self.coordinator.data.get(self._device_id, {}).get("status", {}).get(self._component, {})
        if not data:
            return None
        return data.get(self._capability, {}).get(self._attribute, {}).get("value")

    @property
    def options(self):
        """Return a set of selectable options."""
        data = self.coordinator.data.get(self._device_id, {}).get("status", {}).get(self._component, {})
        if not data:
            return []
        
        # Le opzioni possono chiamarsi supportedCourses o supportedCycles
        cap_data = data.get(self._capability, {})
        supported = cap_data.get("supportedCourses", {}).get("value")
        if not supported:
            supported = cap_data.get("supportedCycles", {}).get("value")
        
        return supported or []

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        import asyncio
        await self.coordinator.api.execute_command(self._device_id, self._component, self._capability, self._command, [option])
        await asyncio.sleep(2)
        await self.coordinator.async_request_refresh()



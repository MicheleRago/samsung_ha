import logging
from dataclasses import dataclass

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CAP_WASHING_COURSE, CAP_WASHER_COURSE, CAP_DRYER_COURSE, SAMSUNG_WASHER_CYCLES, OVEN_MODE_MAP

_LOGGER = logging.getLogger(__name__)

@dataclass(kw_only=True)
class SamsungSelectEntityDescription(SelectEntityDescription):
    """Class describing Samsung select entities."""
    capability: str
    attribute: str
    options_attribute: str
    command: str
    is_course: bool = False

SELECT_TYPES: tuple[SamsungSelectEntityDescription, ...] = (
    SamsungSelectEntityDescription(
        key="dishwasher_course",
        name="Dishwasher Course",
        capability=CAP_WASHING_COURSE,
        attribute="washingCourse",
        options_attribute="supportedCourses",
        command="setWashingCourse",
        is_course=True,
    ),
    SamsungSelectEntityDescription(
        key="washer_course",
        name="Washer Course",
        capability=CAP_WASHER_COURSE,
        attribute="washerCycle",
        options_attribute="supportedCycles",
        command="setWasherCycle",
        is_course=True,
    ),
    SamsungSelectEntityDescription(
        key="dryer_course",
        name="Dryer Course",
        capability=CAP_DRYER_COURSE,
        attribute="dryerCycle",
        options_attribute="supportedCycles",
        command="setDryerCycle",
        is_course=True,
    ),
    SamsungSelectEntityDescription(
        key="freezer_mode",
        name="Freezer Mode",
        capability="samsungce.freezerConvertMode",
        attribute="freezerConvertMode",
        options_attribute="supportedFreezerConvertModes",
        command="setFreezerConvertMode",
        is_course=False,
    ),
    SamsungSelectEntityDescription(
        key="oven_mode",
        name="Oven Mode",
        capability="samsungce.ovenMode",
        attribute="ovenMode",
        options_attribute="supportedOvenModes",
        command="setOvenMode",
        is_course=False,
    ),
    SamsungSelectEntityDescription(
        key="microwave_power",
        name="Microwave Power",
        capability="samsungce.microwavePower",
        attribute="powerLevel",
        options_attribute="supportedPowerLevels",
        command="setPowerLevel",
        is_course=False,
    ),
)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the select platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    selects = []
    
    for device_id, device_data in coordinator.data.items():
        components = device_data.get("status", {})
        device_info = device_data.get("device_info", {})
        device_name = device_info.get("name", "Samsung Appliance")
        
        for comp_name, status in components.items():
            name_prefix = f"{device_name} ({comp_name})" if comp_name != "main" else device_name

            for description in SELECT_TYPES:
                if description.capability in status:
                    selects.append(GenericSelect(coordinator, device_id, comp_name, name_prefix, description))
            
    async_add_entities(selects)


class GenericSelect(CoordinatorEntity, SelectEntity):
    """Select for generic options and courses."""
    entity_description: SamsungSelectEntityDescription

    def __init__(self, coordinator, device_id, component, device_name, description: SamsungSelectEntityDescription):
        super().__init__(coordinator)
        self.entity_description = description
        self._device_id = device_id
        self._component = component
        self._device_name = device_name
        
        comp_prefix = f"_{component}" if component != "main" else ""
        self._attr_unique_id = f"{device_id}{comp_prefix}_{description.capability}_{description.attribute}"
        self._attr_name = description.name
        self._attr_has_entity_name = True

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._device_name.replace(f" ({self._component})", ""),
            "manufacturer": "Samsung",
        }

    def _translate_code(self, code):
        """Map code to name if possible, otherwise return code."""
        if not self.entity_description.is_course or not code:
            return code
            
        if isinstance(code, str) and "_Course_" in code:
            code = code.split("_Course_")[-1]
            
        if self.entity_description.capability in (CAP_WASHER_COURSE, CAP_DRYER_COURSE):
            return SAMSUNG_WASHER_CYCLES.get(code, f"Cycle {code}")
            
        if self.entity_description.capability == "samsungce.ovenMode":
            return OVEN_MODE_MAP.get(code, code)
            
        return code

    def _reverse_translate(self, name):
        """Map name back to code if possible, otherwise return name."""
        if not self.entity_description.is_course and self.entity_description.capability != "samsungce.ovenMode":
            return name
            
        if self.entity_description.capability in (CAP_WASHER_COURSE, CAP_DRYER_COURSE):
            for k, v in SAMSUNG_WASHER_CYCLES.items():
                if v == name:
                    return k
            if name.startswith("Cycle "):
                return name.replace("Cycle ", "")
        
        if self.entity_description.capability == "samsungce.ovenMode":
            for k, v in OVEN_MODE_MAP.items():
                if v == name:
                    return k
                    
        return name

    @property
    def current_option(self):
        """Return the current selected option."""
        data = self.coordinator.data.get(self._device_id, {}).get("status", {}).get(self._component, {})
        if not data:
            return None
        # If it's ovenMode, check local cache first (if oven is off)
        if self.entity_description.capability == "samsungce.ovenMode":
            cache_key = f"{self._device_id}_pending_oven_state"
            if cache_key in self.coordinator.hass.data.get(DOMAIN, {}):
                cached_mode = self.coordinator.hass.data[DOMAIN][cache_key].get("mode")
                if cached_mode is not None:
                    machine_state = data.get("ovenOperatingState", {}).get("machineState", {}).get("value")
                    job_state = data.get("ovenOperatingState", {}).get("ovenJobState", {}).get("value")
                    if machine_state not in ["running", "paused"] and job_state in ["ready", "finished", None]:
                        return self._translate_code(cached_mode)

        val = data.get(self.entity_description.capability, {}).get(self.entity_description.attribute, {}).get("value")
        return self._translate_code(val)

    @property
    def options(self):
        """Return a set of selectable options."""
        data = self.coordinator.data.get(self._device_id, {}).get("status", {}).get(self._component, {})
        if not data:
            return []
        
        supported = data.get(self.entity_description.capability, {}).get(self.entity_description.options_attribute, {}).get("value")
        
        # Fallback for old washer APIs
        if not supported and self.entity_description.is_course:
            supported = data.get(self.entity_description.capability, {}).get("supportedCycles", {}).get("value")
            
        if self.entity_description.is_course and isinstance(supported, list) and len(supported) > 0 and isinstance(supported[0], dict):
            return [self._translate_code(str(item.get("cycle"))) for item in supported if "cycle" in item]
        
        options = [self._translate_code(opt) for opt in (supported or [])]
        
        # Fallbacks for empty supported arrays
        if not options:
            if self.entity_description.capability == "samsungce.microwavePower":
                options = ["100W", "300W", "450W", "600W", "700W", "800W", "850W", "900W"]
            elif self.entity_description.capability == "samsungce.ovenMode":
                options = [self._translate_code(opt) for opt in ["NoOperation", "ConvectionBake", "Conventional", "Broil", "Auto", "BottomHeat"]]

        current = self.current_option
        if current and current not in options:
            options.append(current)
            
        return options

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        import asyncio
        code = self._reverse_translate(option)
        
        # Cache the selected mode for the start button
        if self.entity_description.capability == "samsungce.ovenMode":
            cache_key = f"{self._device_id}_pending_oven_state"
            if cache_key not in self.hass.data[DOMAIN]:
                self.hass.data[DOMAIN][cache_key] = {}
            self.hass.data[DOMAIN][cache_key]["mode"] = code
            
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
            [code]
        )
        await asyncio.sleep(2)
        await self.coordinator.async_request_refresh()

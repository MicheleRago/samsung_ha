from dataclasses import dataclass

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    CAP_FREEZER_CONVERT_MODE,
    CAP_OVEN_MODE,
    CAP_WASHING_COURSE,
    CAP_WASHER_COURSE,
    CAP_DRYER_COURSE,
    SAMSUNG_WASHER_CYCLES,
    OVEN_MODE_MAP,
    OVEN_SELECT_MODES,
    normalize_oven_mode_code,
)
from .oven import cached_oven_setting, cache_oven_setting, component_status, oven_is_waiting_for_start

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
        capability=CAP_FREEZER_CONVERT_MODE,
        attribute="freezerConvertMode",
        options_attribute="supportedFreezerConvertModes",
        command="setFreezerConvertMode",
        is_course=False,
    ),
    SamsungSelectEntityDescription(
        key="oven_mode",
        name="Oven Mode",
        capability=CAP_OVEN_MODE,
        attribute="ovenMode",
        options_attribute="supportedOvenModes",
        command="setOvenMode",
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
        if not code:
            return code

        if self.entity_description.capability == CAP_OVEN_MODE:
            return OVEN_MODE_MAP.get(code, code)

        if not self.entity_description.is_course:
            return code
            
        if isinstance(code, str) and "_Course_" in code:
            code = code.split("_Course_")[-1]
            
        if self.entity_description.capability in (CAP_WASHER_COURSE, CAP_DRYER_COURSE):
            return SAMSUNG_WASHER_CYCLES.get(code, f"Cycle {code}")
            
        return code

    def _oven_supported_mode_codes(self):
        """Return device-supported oven mode codes, if SmartThings exposes them."""
        data = component_status(self.coordinator, self._device_id, self._component)
        supported = data.get(self.entity_description.capability, {}).get(self.entity_description.options_attribute, {}).get("value")
        if not isinstance(supported, list):
            return []

        mode_codes = []
        for item in supported:
            if isinstance(item, str):
                mode_codes.append(item)
            elif isinstance(item, dict):
                mode = item.get("mode") or item.get("ovenMode") or item.get("value")
                if isinstance(mode, str):
                    mode_codes.append(mode)
        return mode_codes

    def _reverse_translate(self, name):
        """Map name back to code if possible, otherwise return name."""
        if not self.entity_description.is_course and self.entity_description.capability != CAP_OVEN_MODE:
            return name
            
        if self.entity_description.capability in (CAP_WASHER_COURSE, CAP_DRYER_COURSE):
            for k, v in SAMSUNG_WASHER_CYCLES.items():
                if v == name:
                    return k
            if name.startswith("Cycle "):
                return name.replace("Cycle ", "")
        
        if self.entity_description.capability == CAP_OVEN_MODE:
            alias_code = normalize_oven_mode_code(name)
            if alias_code != name:
                return alias_code
            for k in self._oven_supported_mode_codes():
                if OVEN_MODE_MAP.get(k, k) == name:
                    return k
            for k in OVEN_SELECT_MODES:
                if OVEN_MODE_MAP.get(k) == name:
                    return k
            for k, v in OVEN_MODE_MAP.items():
                if v == name:
                    return normalize_oven_mode_code(k)
            return normalize_oven_mode_code(name)
                    
        return name

    @property
    def current_option(self):
        """Return the current selected option."""
        data = component_status(self.coordinator, self._device_id, self._component)
        if not data:
            return None
        # If it's ovenMode, check local cache first (if oven is off)
        if self.entity_description.capability == CAP_OVEN_MODE:
            cached_mode = cached_oven_setting(self.coordinator.hass, self._device_id, "mode")
            if cached_mode is not None and oven_is_waiting_for_start(data):
                return self._translate_code(cached_mode)

        val = data.get(self.entity_description.capability, {}).get(self.entity_description.attribute, {}).get("value")
        return self._translate_code(val)

    @property
    def options(self):
        """Return a set of selectable options."""
        data = component_status(self.coordinator, self._device_id, self._component)
        if not data:
            return []
        
        # For ovenMode, prefer the device-reported modes; use known Samsung
        # oven modes only when SmartThings does not expose supportedOvenModes.
        if self.entity_description.capability == CAP_OVEN_MODE:
            mode_codes = self._oven_supported_mode_codes() or list(OVEN_SELECT_MODES)
            if not mode_codes:
                mode_codes = list(OVEN_SELECT_MODES)

            options = []
            seen = set()
            for opt in mode_codes:
                label = self._translate_code(opt)
                if label not in seen:
                    options.append(label)
                    seen.add(label)
            current = self.current_option
            if current and current not in options:
                options.append(current)
            return options
            
        supported = data.get(self.entity_description.capability, {}).get(self.entity_description.options_attribute, {}).get("value")
        
        # Fallback for old washer APIs
        if not supported and self.entity_description.is_course:
            supported = data.get(self.entity_description.capability, {}).get("supportedCycles", {}).get("value")
            
        if self.entity_description.is_course and isinstance(supported, list) and len(supported) > 0 and isinstance(supported[0], dict):
            return [self._translate_code(str(item.get("cycle"))) for item in supported if "cycle" in item]
        
        options = [self._translate_code(opt) for opt in (supported or [])]
        
        current = self.current_option
        if current and current not in options:
            options.append(current)
            
        return options

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        import asyncio
        code = self._reverse_translate(option)
        
        # Cache the selected mode for the start button
        if self.entity_description.capability == CAP_OVEN_MODE:
            code = normalize_oven_mode_code(code)
            cache_oven_setting(self.hass, self._device_id, "mode", code)
            
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
            [code]
        )
        await asyncio.sleep(2)
        await self.coordinator.async_request_refresh()

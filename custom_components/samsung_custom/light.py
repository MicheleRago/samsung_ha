import asyncio
import math
from typing import Any

from homeassistant.components.light import (
    LightEntity,
    ColorMode,
    ATTR_BRIGHTNESS,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CAP_OVEN_LAMP, DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the light platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    lights = []
    
    for device_id, device_data in coordinator.data.items():
        components = device_data.get("status", {})
        device_info = device_data.get("device_info", {})
        device_name = device_info.get("name", "Samsung Appliance")
        
        for comp_name, status in components.items():
            name_prefix = f"{device_name} ({comp_name})" if comp_name != "main" else device_name
            
            if CAP_OVEN_LAMP in status:
                lights.append(SamsungLampLight(coordinator, device_id, comp_name, name_prefix))
                
    async_add_entities(lights)


class SamsungLampLight(CoordinatorEntity, LightEntity):
    """Light entity for the oven lamp."""

    def __init__(self, coordinator, device_id, component, name):
        super().__init__(coordinator)
        self._device_id = device_id
        self._component = component
        self._device_name = name
        
        comp_prefix = f"_{component}" if component != "main" else ""
        self._attr_unique_id = f"{device_id}{comp_prefix}_samsungce_lamp"
        self._attr_name = "Light"
        self._attr_has_entity_name = True
        self._attr_supported_color_modes = {ColorMode.BRIGHTNESS}
        self._attr_color_mode = ColorMode.BRIGHTNESS

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._device_name.replace(f" ({self._component})", ""),
            "manufacturer": "Samsung",
        }

    @property
    def is_on(self):
        """Return true if light is on."""
        data = self.coordinator.data.get(self._device_id, {}).get("status", {}).get(self._component, {})
        if not data:
            return False
        
        level = data.get(CAP_OVEN_LAMP, {}).get("brightnessLevel", {}).get("value")
        return level != "off" and level is not None

    @property
    def brightness(self):
        """Return the brightness of the light."""
        data = self.coordinator.data.get(self._device_id, {}).get("status", {}).get(self._component, {})
        if not data:
            return 0
            
        level = data.get(CAP_OVEN_LAMP, {}).get("brightnessLevel", {}).get("value")
        
        if level == "off" or level is None:
            return 0
            
        supported_levels = self._get_supported_levels(data)
        if not supported_levels:
            return 255
            
        if level not in supported_levels:
            return 255
            
        step = 255 / len(supported_levels)
        return int(step * (supported_levels.index(level) + 1))

    def _get_supported_levels(self, data):
        """Get list of supported brightness levels without 'off'."""
        supported = data.get(CAP_OVEN_LAMP, {}).get("supportedBrightnessLevel", {}).get("value", [])
        if not isinstance(supported, list):
            supported = []
        return [l for l in supported if l != "off"]

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the light on."""
        brightness = kwargs.get(ATTR_BRIGHTNESS)
        
        data = self.coordinator.data.get(self._device_id, {}).get("status", {}).get(self._component, {})
        supported_levels = self._get_supported_levels(data)
        
        if brightness is not None and supported_levels:
            # Map HA brightness (0-255) to a supported level
            step = 255 / len(supported_levels)
            level_index = min(len(supported_levels) - 1, max(0, math.ceil(brightness / step) - 1))
            target_level = supported_levels[level_index]
        else:
            # Default to the highest available level, or "high"
            target_level = supported_levels[-1] if supported_levels else "high"
            
        await self.coordinator.api.execute_command(
            self._device_id, 
            self._component, 
            CAP_OVEN_LAMP,
            "setBrightnessLevel", 
            [target_level]
        )
        await asyncio.sleep(2)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the light off."""
        await self.coordinator.api.execute_command(
            self._device_id, 
            self._component, 
            CAP_OVEN_LAMP,
            "setBrightnessLevel", 
            ["off"]
        )
        await asyncio.sleep(2)
        await self.coordinator.async_request_refresh()

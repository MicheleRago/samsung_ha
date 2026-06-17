import logging
from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN, CAP_OPERATING_STATE, CAP_WASHER_OPERATING_STATE, 
    CAP_DRYER_OPERATING_STATE, CAP_OVEN_OPERATING_STATE
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the button platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    buttons = []
    
    for device_id, device_data in coordinator.data.items():
        status = device_data.get("status", {})
        device_info = device_data.get("device_info", {})
        name = device_info.get("name", "Samsung Appliance")
        
        # Check which capability this device uses for operating state
        cap = None
        if CAP_OPERATING_STATE in status:
            cap = CAP_OPERATING_STATE
        elif CAP_WASHER_OPERATING_STATE in status:
            cap = CAP_WASHER_OPERATING_STATE
        elif CAP_DRYER_OPERATING_STATE in status:
            cap = CAP_DRYER_OPERATING_STATE
        elif CAP_OVEN_OPERATING_STATE in status:
            cap = CAP_OVEN_OPERATING_STATE
            
        if cap:
            buttons.append(GenericCommandButton(coordinator, device_id, name, cap, "Run", "run", "mdi:play"))
            buttons.append(GenericCommandButton(coordinator, device_id, name, cap, "Pause", "pause", "mdi:pause"))
            buttons.append(GenericCommandButton(coordinator, device_id, name, cap, "Stop", "stop", "mdi:stop"))

    async_add_entities(buttons)

class GenericCommandButton(CoordinatorEntity, ButtonEntity):
    """Button for sending commands."""

    def __init__(self, coordinator, device_id, device_name, capability, btn_name, command_arg, icon):
        super().__init__(coordinator)
        self._device_id = device_id
        self._device_name = device_name
        self._capability = capability
        self._command_arg = command_arg
        self._attr_unique_id = f"{device_id}_{capability}_{command_arg}"
        self._attr_name = btn_name
        self._attr_icon = icon
        self._attr_has_entity_name = True

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._device_name,
            "manufacturer": "Samsung",
        }

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.coordinator.api.execute_command(self._device_id, self._capability, "setMachineState", [self._command_arg])
        await self.coordinator.async_request_refresh()


import logging
from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CAP_OPERATING_STATE

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the button platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    buttons = [
        DishwasherCommandButton(coordinator, "Run", "run", "mdi:play"),
        DishwasherCommandButton(coordinator, "Pause", "pause", "mdi:pause"),
        DishwasherCommandButton(coordinator, "Stop", "stop", "mdi:stop"),
    ]
    async_add_entities(buttons)

class DishwasherCommandButton(CoordinatorEntity, ButtonEntity):
    """Button for sending commands."""

    def __init__(self, coordinator, name, command_arg, icon):
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.api.device_id}_btn_{command_arg}"
        self._attr_name = name
        self._attr_icon = icon
        self._command_arg = command_arg
        self._attr_has_entity_name = True

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.coordinator.api.device_id)},
            "name": "Samsung Dishwasher",
            "manufacturer": "Samsung",
        }

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.coordinator.api.execute_command(CAP_OPERATING_STATE, "setMachineState", [self._command_arg])
        await self.coordinator.async_request_refresh()

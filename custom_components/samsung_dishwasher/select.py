import logging
from homeassistant.components.select import SelectEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CAP_WASHING_COURSE

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the select platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([DishwasherCourseSelect(coordinator)])

class DishwasherCourseSelect(CoordinatorEntity, SelectEntity):
    """Select for washing course."""

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.api.device_id}_course"
        self._attr_name = "Washing Course"
        self._attr_has_entity_name = True

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.coordinator.api.device_id)},
            "name": "Samsung Dishwasher",
            "manufacturer": "Samsung",
        }

    @property
    def current_option(self):
        """Return the current selected option."""
        data = self.coordinator.data
        if not data:
            return None
        return data.get(CAP_WASHING_COURSE, {}).get("washingCourse", {}).get("value")

    @property
    def options(self):
        """Return a set of selectable options."""
        data = self.coordinator.data
        if not data:
            return []
        return data.get(CAP_WASHING_COURSE, {}).get("supportedCourses", {}).get("value", [])

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        await self.coordinator.api.execute_command(CAP_WASHING_COURSE, "setDishwasherWashingCourse", [option])
        await self.coordinator.async_request_refresh()

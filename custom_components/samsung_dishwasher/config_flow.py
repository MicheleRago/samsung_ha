import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CONF_PAT, CONF_DEVICE_ID
from .api import SmartThingsApi

class SamsungDishwasherConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Samsung Dishwasher."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            pat = user_input[CONF_PAT]
            device_id = user_input[CONF_DEVICE_ID]

            api = SmartThingsApi(pat, device_id)
            try:
                await api.get_device_status()
                return self.async_create_entry(title="Samsung Dishwasher", data=user_input)
            except Exception:
                errors["base"] = "cannot_connect"

        data_schema = vol.Schema({
            vol.Required(CONF_PAT): str,
            vol.Required(CONF_DEVICE_ID): str,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

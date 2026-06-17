import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CONF_PAT
from .api import SmartThingsApi

class SamsungCustomConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Samsung Custom Appliances."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            pat = user_input[CONF_PAT]

            api = SmartThingsApi(pat)
            try:
                devices = await api.get_devices()
                if not devices:
                    errors["base"] = "no_devices"
                else:
                    return self.async_create_entry(title="Samsung Appliances", data=user_input)
            except Exception:
                errors["base"] = "cannot_connect"

        data_schema = vol.Schema({
            vol.Required(CONF_PAT): str,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )


from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN, CONF_IP_ADDRESS

class FroniusMpptConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title=f"Fronius ({user_input[CONF_IP_ADDRESS]})", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_IP_ADDRESS): str,
            }),
            errors=errors,
        )

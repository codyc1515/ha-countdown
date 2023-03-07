from homeassistant import config_entries
from homeassistant.const import CONF_ACCESS_TOKEN
import voluptuous as vol

from .const import (
    DOMAIN,
    SENSOR_NAME
)

@config_entries.HANDLERS.register(DOMAIN)
class ExampleConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title=SENSOR_NAME,
                data={
                    CONF_ACCESS_TOKEN: user_input[CONF_ACCESS_TOKEN]
                }
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_ACCESS_TOKEN): str
            })
        )

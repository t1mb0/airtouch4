"""Config flow for AirTouch4."""
from airtouch4pyapi import AirTouch
import voluptuous as vol

from homeassistant import config_entries, core
from homeassistant.const import CONF_HOST

from .const import DOMAIN

DATA_SCHEMA = vol.Schema({vol.Required(CONF_HOST): str})


async def _validate_connection(hass: core.HomeAssistant, host):
    airtouch = AirTouch(host)
    if hasattr(airtouch, "error"):
        return airtouch.error
    return bool(airtouch.GetGroups())


class AirtouchConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle an Airtouch config flow."""

    DOMAIN = DOMAIN
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    @core.callback
    def _async_get_entry(self, data):

        return self.async_create_entry(
            title=data[CONF_HOST],
            data={
                CONF_HOST: data[CONF_HOST],
            },
        )

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA)

        errors = {}

        host = user_input[CONF_HOST]

        result = await _validate_connection(self.hass, host)
        if not result:
            errors["base"] = "no_units"
        elif isinstance(result, OSError):
            errors["base"] = "cannot_connect"

        if errors:
            return self.async_show_form(
                step_id="user", data_schema=DATA_SCHEMA, errors=errors
            )

        return self._async_get_entry(user_input)

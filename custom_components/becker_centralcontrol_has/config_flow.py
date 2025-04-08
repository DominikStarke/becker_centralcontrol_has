"""Config flow for Becker Antriebe GmbH CentralControl."""

import ipaddress
import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries, exceptions
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for the CentralControl."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None) -> config_entries.ConfigFlowResult:
        """Handle the initial step."""

        errors = {}

        if user_input is not None:
            if not _is_valid_ip(user_input.get("host_address", "")):
                errors["host_address"] = "invalid_ip"
            try:
                return self.async_create_entry(title="CentralControl", data=user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidHost:
                errors["host"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        "host_address",
                        default="",
                    ): cv.string,
                    vol.Optional(
                        "prefix",
                        default="",
                    ): str,
                    vol.Optional(
                        "invert_position",
                        default=False,
                    ): bool,
                }
            ),
            errors=errors,
        )

    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None):
        """Handle reconfiguration of the entry."""

        errors = {}
        if user_input is None:
            tmp_user_input = {}
        else:
            tmp_user_input = user_input

        config_entry = self._get_reconfigure_entry()
        host_address = tmp_user_input.get(
            "host_address", config_entry.data.get("host_address", "")
        )
        prefix = tmp_user_input.get("prefix", config_entry.data.get("prefix", ""))
        invert_position = tmp_user_input.get(
            "invert_position", config_entry.data.get("invert_position", False)
        )

        if user_input is not None:
            if not _is_valid_ip(user_input.get("host_address", "")):
                errors["host_address"] = "invalid_ip"
            else:
                try:
                    self.hass.config_entries.async_update_entry(
                        config_entry, data=user_input
                    )
                    await self.hass.config_entries.async_reload(config_entry.entry_id)
                    return self.async_abort(reason="reconfigure_successful")
                except CannotConnect:
                    errors["base"] = "cannot_connect"
                except InvalidHost:
                    errors["host"] = "cannot_connect"
                except Exception:
                    _LOGGER.exception("Unexpected exception")
                    errors["base"] = "unknown"

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        "host_address",
                        default=host_address,
                    ): cv.string,
                    vol.Optional(
                        "prefix",
                        default=prefix,
                    ): str,
                    vol.Optional(
                        "invert_position",
                        default=invert_position,
                    ): bool,
                }
            ),
            errors=errors,
        )


def _is_valid_ip(ip: str) -> bool:
    """Check for valid ip address."""

    try:
        ipaddress.ip_address(ip)
    except ValueError:
        return False
    else:
        return True


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidHost(exceptions.HomeAssistantError):
    """Error to indicate there is an invalid hostname."""


async def validate_input(hass: HomeAssistant, data: dict) -> bool:
    """Validate the user input allows us to connect.

    Data has the keys from DATA_SCHEMA with values provided by the user.
    """
    return True

"""The CentralControl integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .central_control import CentralControl
from .const import PLATFORMS

type CentralControlConfigEntry = ConfigEntry[CentralControl]


async def async_setup_entry(
    hass: HomeAssistant, entry: CentralControlConfigEntry
) -> bool:
    """Set up CentralControl from a config entry."""

    address = entry.data["host_address"]
    cookie = entry.data.get("gw_token", None)
    invert_position = entry.data.get("invert_position", False)
    prefix = entry.data.get("prefix", None)

    central_control = CentralControl(
        address=address,
        cookie=cookie,
        invert_position=invert_position,
        prefix=prefix,
    )
    entry.runtime_data = central_control

    item_list: dict
    try:
        item_list = await central_control.get_item_list(item_type="group")
    except TimeoutError:
        return False

    if item_list.get("result", {}).get("item_list") is None:
        return False

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

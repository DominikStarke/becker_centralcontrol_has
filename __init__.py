"""The CentralControl integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_TOKEN
from homeassistant.core import HomeAssistant

from .central_control import CentralControl
from .const import PLATFORMS

type CentralControlConfigEntry = ConfigEntry[CentralControl]  # noqa: F821


async def async_setup_entry(
    hass: HomeAssistant, entry: CentralControlConfigEntry
) -> bool:
    """Set up CentralControl from a config entry."""

    address = entry.data[CONF_HOST]
    cookie = entry.data.get(CONF_TOKEN, None)
    # shortName = "" # short name of the central control device (login to gw.b-tronic.net, connect to a box and check the URL)

    central_control = CentralControl(
        address=address,
        # address="https://gw.b-tronic.net/cc{}/cgi-bin/cc51rpc.cgi".format(shortName), # Connect through the gateway. Not recommended.
        cookie=cookie,
    )
    entry.runtime_data = central_control

    item_list: dict
    try:
        item_list = await central_control.get_item_list(item_type="group")
    except TimeoutError:
        return False

    # # Run zeroconf discovery, in case no address was supplied?
    # aiozc = await zeroconf.async_get_async_instance(hass)
    # discovery = CentralControlDiscovery()
    # await aiozc.async_add_service_listener("_http._tcp.local.", discovery)

    if item_list.get("result") is None:
        return False
    if item_list["result"].get("item_list") is None:
        return False
    if item_list["result"]["item_list"] is False:
        return False

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

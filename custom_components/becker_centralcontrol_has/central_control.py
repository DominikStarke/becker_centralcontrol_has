"""Representation of a Becker Antriebe GmbH CentralControl."""

import asyncio
import json

import requests


class CentralControl:
    """API Client for the CentralControl devices."""

    def __init__(
        self,
        address: str,
        cookie: str | None = None,
        prefix: str = "",
        invert_position: bool = False,
    ) -> None:
        """Init.

        address -- CGI Endpoint for the deviced. This needs to point to the correct path for example: http://192.168.1.10/cgi-bin/cc51rpc.cgi
        cookie -- in case you want to connect through gw.b-tronic.net
        prefix -- prefix for the entity names
        invert_position -- invert the position display
        """

        self._prefix = f"{prefix}_" if prefix else ""
        self._invert_position = invert_position
        self.address = f"http://{address}/cgi-bin/cc51rpc.cgi"
        self._headers = {
            "Origin": "https://gw.b-tronic.net",
            "Host": "gw.b-tronic.net",
            "Content-Type": "text/plain",
        }
        if cookie is not None:
            self._headers["Cookie"] = cookie

    @property
    def prefix(self) -> str:
        """Return the prefix."""

        return self._prefix

    @property
    def invert_position(self) -> bool:
        """If position display should be inverted."""

        return self._invert_position

    async def _jrpc_request(
        self, data: dict | list[dict], timeout: int = 10
    ) -> dict | list | None:
        try:
            async with asyncio.timeout(timeout):
                response: requests.Response = await asyncio.to_thread(
                    requests.post,
                    url=self.address,
                    data=json.dumps(data) + "\0",
                    headers=self._headers,
                )

                return json.loads(response.content.decode("utf-8").replace("\0", ""))
        except TimeoutError:
            if data is list:
                return []
            return {}
        except json.decoder.JSONDecodeError:
            if data is list:
                return []
            return {}

    async def get_item_list(
        self,
        item_type: str | None = None,
        list_type: str | None = None,
        parent_id: str | None = None,
        action: str | None = None,
    ) -> dict:
        """Retrieve a list of items, with names, which match given criteria.

        ### Output values
        * item_list: list of items matching the query (Array) Returns an array with a description of all items. The item elements contain:
        * item_id - the id of the item described
        * item_type - the type of the item described
        * name - the name of the item
        * icon - an possibly empty icon descriptor
        * device_type - if it is a group: the type of the group

        Parameters:
        ----------
        item_type : str
            The type of items requested (optional String)
        list_type : str
            The type of list requested. Must be either empty, or one of "receivers", "groups", "climate-zones" (optional String)
        parent_id : str
            The id of a container in question (optional Number)
        action : str
            An action that can be done to the items in relation to the container (add/del) (optional String)

        Returns:
        -------
        list of items

        """
        return await self._jrpc_request(
            data={
                "jsonrpc": "2.0",
                "id": 0,
                "params": {
                    k: v for k, v in locals().items() if k != "self" and v is not None
                },
                "method": "deviced.deviced_get_item_list",
            }
        )

    async def get_scene_list(self) -> dict:
        """Retrieve the list of configured scenes."""
        return await self.get_item_list(item_type="scene")

    async def scene_invoke(self, scene_id: int) -> dict:
        """Invoke a configured scene."""
        return await self._jrpc_request(
            data={
                "jsonrpc": "2.0",
                "id": 0,
                "params": {"scene_id": scene_id},
                "method": "deviced.scene_invoke",
            }
        )

    async def scene_stop(self, scene_id: int) -> dict:
        """Stop a configured scene."""
        return await self._jrpc_request(
            data={
                "jsonrpc": "2.0",
                "id": 0,
                "params": {"scene_id": scene_id},
                "method": "deviced.scene_stop",
            }
        )

    async def group_send_command(self, group_id: int, command: str, value) -> dict:
        """Send a command to a group.

         A check if the command is suitable is performed.

        * group_id: int -- target group id (Number)
        * command: str -- command to send (String)
        * value: float -- value for command (Number)

        The different device types accept different commands:

        Shutter, roof_window, awning, screen, and sun_sail accept:
        * move with integer values -1 (open), 0 (stop), 1 (close)
        * moveto with float values from 0 (open) to 100 (close)
        * movepreset with integer values 1 and 2

        For roof windows, the preset 2 has the special meaning of a timer-controlled closing of the window.

        Device type venetian understands the same commands, but additionally:
        * step with integer values -1 (open), 0, 1 (close)

        Device type dimmer understands the following commands:
        * switch with integer value 0 or 1
        * dim with integer value -1 (darker), 0, 1 (brighter)
        * dimto with a float value from 0 (off) to 100 (on)
        * dimpreset with integer value 1 or 2

        Device type switch and heater understand:
        * switch with integer value 0 or 1

        Device type door understands:
        * move with integer value -1 (open), 0, 1 (close)

        Device type door_pulse understands:
        * step with integer value 1

        Device type thermostat understands:
        * switch with integer value 0 or 1
        * tempmode with integer value 0, 1, 2, 3
        * tempset with float value between 4.0 and 40.0
        """
        return await self._jrpc_request(
            data={
                "jsonrpc": "2.0",
                "id": 0,
                "params": {"group_id": group_id, "command": command, "value": value},
                "method": "deviced.group_send_command",
            }
        )

    async def get_state(self, item_id) -> dict:
        """Get combined group and item state.

        * value: the group value (optional Number)
        * mode: the mode of the group (depends on device type) (optional String)
        * moving_up: the number of shutters moving up (optional Number)
        * moving_down: the number of shutters moving down (optional Number)
        * error_flags: the (collected) error states of the child devices (Array of Strings) (optional Array)
        * error_count: the number of erroneous devices (optional Number)
        * scheduled_cmd: True if there is a pending close command on this group. (optional Bool)
        """
        data: list = await self._jrpc_request(
            data=[
                {
                    "jsonrpc": "2.0",
                    "id": 0,
                    "params": {"group_id": item_id},
                    "method": "deviced.group_get_state",
                },
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "params": {"item_id": item_id},
                    "method": "deviced.item_get_state",
                },
            ]
        )

        if len(data) < 1:
            return {}
        if len(data) < 2:
            return data[0].get("result", {}).get("state", {})

        group_state = data[0].get("result", {}).get("state", {})
        item_state = data[1].get("result", {}).get("state", {})

        return {**group_state, **item_state} if group_state or item_state else None

    async def hvac_zone_get_mode(self, hvac_id: int) -> str | None:
        """Retrieve the operation mode of a hvac zone.

        HVAC zones are groups of thermostats (device type thermostat), optionally
        with a temperature sensor and window sensors. Zones can be listed with
        get_item_list(list_type="climate-zones").

        Parameters:
        ----------
        hvac_id : int
            Id of the hvac zone (Number)

        Returns:
        -------
        The operation mode (String): "eco", "comfort", "individual" or "anti-freeze".
        None if the request failed.

        """
        data = await self._jrpc_request(
            data={
                "jsonrpc": "2.0",
                "id": 0,
                "params": {"hvac_id": hvac_id},
                "method": "deviced.hvac_zone_get_mode",
            }
        )
        return (data or {}).get("result", {}).get("mode")

    async def hvac_zone_set_mode(self, hvac_id: int, mode: str) -> dict:
        """Select the basic operation mode of a hvac zone.

        Parameters:
        ----------
        hvac_id : int
            Id of the hvac zone (Number)
        mode : str
            "eco", "comfort", "individual" or "anti-freeze" (String)

        """
        return await self._jrpc_request(
            data={
                "jsonrpc": "2.0",
                "id": 0,
                "params": {"hvac_id": hvac_id, "mode": mode},
                "method": "deviced.hvac_zone_set_mode",
            }
        )

    async def hvac_zone_get_temperature(
        self, hvac_id: int, mode: str = "individual"
    ) -> float | None:
        """Retrieve the target temperature of an operation mode of a hvac zone.

        Parameters:
        ----------
        hvac_id : int
            Id of the hvac zone (Number)
        mode : str
            "eco", "comfort" or "individual" (default). "anti-freeze" has no
            configurable temperature and is rejected by the device. (String)

        Returns:
        -------
        The target temperature in centigrade (Number), None if the request failed.

        """
        data = await self._jrpc_request(
            data={
                "jsonrpc": "2.0",
                "id": 0,
                "params": {"hvac_id": hvac_id, "mode": mode},
                "method": "deviced.hvac_zone_get_temperature",
            }
        )
        return (data or {}).get("result", {}).get("temp")

    async def hvac_zone_set_temperature(
        self, hvac_id: int, temp: float, mode: str = "individual"
    ) -> dict:
        """Set the target temperature of an operation mode of a hvac zone.

        This does not activate the mode, use hvac_zone_set_mode for that.

        Parameters:
        ----------
        hvac_id : int
            Id of the hvac zone (Number)
        temp : float
            Target temperature in centigrade (Number)
        mode : str
            "eco", "comfort" or "individual" (default) (String)

        """
        return await self._jrpc_request(
            data={
                "jsonrpc": "2.0",
                "id": 0,
                "params": {"hvac_id": hvac_id, "mode": mode, "temp": temp},
                "method": "deviced.hvac_zone_set_temperature",
            }
        )

    async def hvac_zone_get_schedule(self, hvac_id: int) -> dict:
        """Retrieve the heating schedule of a hvac zone.

        Parameters:
        ----------
        hvac_id : int
            Id of the hvac zone (Number)

        Returns:
        -------
        * enabled: scheduling enabled (Bool)
        * schedule: switching points (Array of String), each formatted as
          "weekdays/hh:mm/mode", e.g. "0123456/6:00/comfort"

        """
        return await self._jrpc_request(
            data={
                "jsonrpc": "2.0",
                "id": 0,
                "params": {"hvac_id": hvac_id},
                "method": "deviced.hvac_zone_get_schedule",
            }
        )

    async def hvac_zone_set_schedule(
        self, hvac_id: int, enabled: bool, schedule: list[str] | None = None
    ) -> dict:
        """Set the heating schedule of a hvac zone.

        Parameters:
        ----------
        hvac_id : int
            Id of the hvac zone (Number)
        enabled : bool
            Scheduling active (Bool)
        schedule : list[str]
            Up to 49 switching points (optional Array). Each string follows the
            pattern "w/hh:mm/mode": "w" are weekday indices (0: sunday,
            6: saturday), "hh:mm" the time of day and "mode" one of "anti-freeze",
            "eco", "comfort" or a decimal temperature in centigrade.

        Returns:
        -------
        * overlap: true if there were overlaps (optional Bool)
        * collisions: true if there were collisions (optional Bool)

        """
        params: dict = {"hvac_id": hvac_id, "enabled": enabled}
        if schedule is not None:
            params["schedule"] = schedule
        return await self._jrpc_request(
            data={
                "jsonrpc": "2.0",
                "id": 0,
                "params": params,
                "method": "deviced.hvac_zone_set_schedule",
            }
        )

"""Representation of a Becker Antriebe GmbH CentralControl."""

import asyncio
import json

import requests


class CentralControl:
    """API Client for the CentralControl devices."""

    def __init__(self, address: str, cookie: str | None = None) -> None:
        """Init.

        address -- CGI Endpoint for the deviced. This needs to point to the correct path for example: http://192.168.1.10/cgi-bin/cc51rpc.cgi
        cookie -- in case you want to connect through gw.b-tronic.net
        """

        self.address = address
        self._headers = {
            "Origin": "https://gw.b-tronic.net",
            "Host": "gw.b-tronic.net",
            "Content-Type": "text/plain",
        }
        if cookie is not None:
            self._headers["Cookie"] = cookie

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

                return json.loads(response.text.replace("\0", ""))
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

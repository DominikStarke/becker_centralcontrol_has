"""Tests for the CentralControl API client."""

import importlib.util
import json
from pathlib import Path
from unittest.mock import Mock, patch

MODULE_PATH = (
    Path(__file__).parents[1]
    / "custom_components"
    / "becker_centralcontrol_has"
    / "central_control.py"
)
spec = importlib.util.spec_from_file_location("central_control", MODULE_PATH)
central_control_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(central_control_module)
CentralControl = central_control_module.CentralControl


async def test_jrpc_request_decodes_utf8_response_content() -> None:
    """Decode CentralControl JSON-RPC responses as UTF-8.

    The CC51 returns text/plain without a charset, so requests may expose
    response.text as ISO-8859-1/latin-1 mojibake (for example ``KÃ¼che``).
    """

    response = Mock()
    response.content = (
        json.dumps(
            {
                "jsonrpc": "2.0",
                "id": 0,
                "result": {
                    "item_list": [
                        {"id": 3, "type": "group", "name": "Küche links"},
                        {"id": 6, "type": "group", "name": "Tür links"},
                    ]
                },
            },
            ensure_ascii=False,
        )
        + "\0"
    ).encode()
    response.text = response.content.decode("latin-1")

    central_control = CentralControl("192.168.1.64")

    with patch.object(central_control_module.requests, "post", return_value=response):
        result = await central_control.get_item_list(item_type="group")

    items = result["result"]["item_list"]
    assert items[0]["name"] == "Küche links"
    assert items[1]["name"] == "Tür links"

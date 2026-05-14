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


def _response(payload: dict) -> Mock:
    response = Mock()
    response.text = json.dumps(payload) + "\0"
    response.content = response.text.encode()
    return response


async def test_get_scene_list_fetches_scene_items() -> None:
    """Fetch configured scenes from the CentralControl."""

    central_control = CentralControl("192.168.1.64")

    with patch.object(
        central_control_module.requests,
        "post",
        return_value=_response({"jsonrpc": "2.0", "id": 0, "result": {}}),
    ) as post:
        await central_control.get_scene_list()

    request = json.loads(post.call_args.kwargs["data"].replace("\0", ""))
    assert request["method"] == "deviced.deviced_get_item_list"
    assert request["params"] == {"item_type": "scene"}


async def test_scene_invoke_sends_scene_command() -> None:
    """Invoke a configured scene."""

    central_control = CentralControl("192.168.1.64")

    with patch.object(
        central_control_module.requests,
        "post",
        return_value=_response({"jsonrpc": "2.0", "id": 0, "result": {}}),
    ) as post:
        await central_control.scene_invoke(109)

    request = json.loads(post.call_args.kwargs["data"].replace("\0", ""))
    assert request["method"] == "deviced.scene_invoke"
    assert request["params"] == {"scene_id": 109}


async def test_scene_stop_sends_scene_command() -> None:
    """Stop a configured scene."""

    central_control = CentralControl("192.168.1.64")

    with patch.object(
        central_control_module.requests,
        "post",
        return_value=_response({"jsonrpc": "2.0", "id": 0, "result": {}}),
    ) as post:
        await central_control.scene_stop(109)

    request = json.loads(post.call_args.kwargs["data"].replace("\0", ""))
    assert request["method"] == "deviced.scene_stop"
    assert request["params"] == {"scene_id": 109}

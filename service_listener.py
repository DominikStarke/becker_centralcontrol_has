"""ZeroConf disovery of Becker Antriebe GmbH CC41."""

from zeroconf import Zeroconf
from zeroconf.asyncio import ServiceListener


class CentralControlDiscovery(ServiceListener):
    """ZeroConf disovery of Becker Antriebe GmbH CC41."""

    def add_service(self, zc: "Zeroconf", type_: str, name: str) -> None:
        """Add Service to discovered Services."""

    def remove_service(self, zc: "Zeroconf", type_: str, name: str) -> None:
        """Remove Service from discovered services."""

    def update_service(self, zc: "Zeroconf", type_: str, name: str) -> None:
        """Update a Service entry."""

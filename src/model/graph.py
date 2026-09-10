"""Module defining the Graph data structure managing network topology."""

from __future__ import annotations

from src.model.connection import Connection
from src.model.zone import Zone


class Graph:
    """Represents the flight network containing zones, connections, and hubs.

    Attributes:
        zones: Mapping from zone names to Zone instances.
        connections: Set of all unique connections in the network.
        adjacency: Adjacency list mapping each Zone to its incident
        Connections.
        start_hub: Unique designated departure zone.
        end_hub: Unique designated destination zone.
        nb_drones: Total number of drones to route through the network.
    """

    def __init__(self, nb_drones: int = 0):
        """Initialize an empty flight network graph.

        Args:
            nb_drones: Total number of drones (default: 0).
        """
        self.zones: dict[str, Zone] = {}
        self.connections: set[Connection] = set()
        self.adjacency: dict[Zone, list[Connection]] = {}
        self.start_hub: Zone | None = None
        self.end_hub: Zone | None = None
        self.nb_drones = nb_drones

    def add_zone(self, zone: Zone) -> None:
        """Register a new zone in the graph.

        Args:
            zone: The Zone instance to add.

        Raises:
            ValueError: If a zone with the same name is already present.
        """
        if zone.name in self.zones:
            raise ValueError(f"Zone {zone.name} already exists in graph")

        self.adjacency[zone] = []
        self.zones[zone.name] = zone

    def add_connection(self, connection: Connection) -> None:
        """Add a bidirectional connection between two zones.

        Args:
            connection: The Connection instance linking two zones.
        """
        self.connections.add(connection)
        self.adjacency[connection.zone_a].append(connection)
        self.adjacency[connection.zone_b].append(connection)

    def get_neighbors(self, zone: Zone) -> list[Zone]:
        """Get all adjacent zones directly reachable from the given zone.

        Args:
            zone: The Zone whose neighbors are requested.

        Returns:
            A list of adjacent Zone instances.
        """
        results = [v.get_other_endpoint(zone) for v in self.adjacency[zone]]
        return results

    def validate(self) -> None:
        """Verify topological and configuration integrity of the graph.

        Raises:
            ValueError: If drone count is non-positive, if start or end hubs
                are missing, or if start_hub equals end_hub.
        """
        if self.nb_drones <= 0:
            raise ValueError(f"Invalid number of drones: {self.nb_drones}. "
                             "Must be greater than 0.")
        if not self.start_hub:
            raise ValueError("Graph missing mandatory start_hub")
        if not self.end_hub:
            raise ValueError("Graph missing mandatory end_hub")
        if self.start_hub == self.end_hub:
            raise ValueError("start_hub and end_hub cannot be the same zone")

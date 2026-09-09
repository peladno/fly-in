"""Module defining the Connection entity linking zones in the network."""

from __future__ import annotations

from src.model.zone import Zone


class Connection:
    """Represents a bidirectional flight link connecting two zones.

    Attributes:
        zone_a: First connected zone endpoint.
        zone_b: Second connected zone endpoint.
        max_link_capacity: Maximum number of drones traversing concurrently.
    """

    def __init__(
            self,
            zone_a: Zone,
            zone_b: Zone,
            max_link_capacity: int | None = None
            ):
        """Initialize a new Connection instance.

        Args:
            zone_a: First zone endpoint.
            zone_b: Second zone endpoint.
            max_link_capacity: Optional max simultaneous crossing limit.
        """
        self.zone_a = zone_a
        self.zone_b = zone_b
        self.max_link_capacity = max_link_capacity

    def __repr__(self) -> str:
        """Return a technical string representation of the connection."""
        return (f"Connection({self.zone_a.name} <-> "
                f"{self.zone_b.name})")

    def __eq__(self, other: object) -> bool:
        """Compare if two connections link the exact same pair of zones."""
        if not isinstance(other, Connection):
            return False
        return (
            {self.zone_a.name, self.zone_b.name} ==
            {other.zone_a.name, other.zone_b.name})

    def __hash__(self) -> int:
        """Hash based on the unordered pair of zone names."""
        return hash(frozenset({self.zone_a.name, self.zone_b.name}))

    def connects(self, zone: Zone) -> bool:
        """Check if this connection is attached to the given zone.

        Args:
            zone: The zone to test.

        Returns:
            True if the zone is either zone_a or zone_b, False otherwise.
        """
        return zone == self.zone_a or zone == self.zone_b

    def get_other_endpoint(self, current: Zone) -> Zone:
        """Retrieve the opposite zone endpoint from the given one.

        Args:
            current: The starting endpoint zone.

        Returns:
            The opposite endpoint Zone.

        Raises:
            ValueError: If current is neither zone_a nor zone_b.
        """
        if current == self.zone_a:
            return self.zone_b
        if current == self.zone_b:
            return self.zone_a
        raise ValueError(f"Zone '{current.name}' is not "
                         "an endpoint of this connection")

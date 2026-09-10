"""Module defining zones and their classifications in the fly-in network."""

from __future__ import annotations
from enum import Enum
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from src.model.drone import Drone


class ZoneType(Enum):
    """Enumeration of possible zone operational classifications."""

    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class Zone:
    """Represents a node/hub in the flight network.

    Attributes:
        name: Unique identifier string for the zone.
        coor: 2D spatial coordinates (x, y).
        zone_type: Operational classification (NORMAL, BLOCKED, etc.).
        max_drones: Maximum concurrent occupancy (None denotes infinite).
        drones: Set of drones currently occupying this zone.
    """

    def __init__(
            self, name: str,
            coord: tuple[float, float],
            zone_type: ZoneType = ZoneType.NORMAL,
            max_drones: int | None = 1
                ):
        """Initialize a new Zone instance.

        Args:
            name: Unique name of the zone.
            coor: Tuple with (x, y) coordinates.
            zone_type: Type of the zone (default: NORMAL).
            max_drones: Maximum drones allowed, or None for unlimited.
        """
        self.name = name
        self.coord = coord
        self.zone_type = zone_type
        self.max_drones = max_drones
        self.drones: set[Drone] = set()

    def is_full(self) -> bool:
        """Check if the zone has reached its maximum drone capacity.

        Returns:
            True if blocked or full, False if space is available or unbounded.
        """
        if self.max_drones is None:
            return False
        if self.zone_type == ZoneType.BLOCKED:
            return True
        return len(self.drones) >= self.max_drones

    def __repr__(self) -> str:
        """Return a technical string representation of the Zone."""
        return f"Zone({self.name!r}, {self.zone_type.value})"

    def __str__(self) -> str:
        """Return the user-facing zone name."""
        return self.name

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Zone):
            return False
        return self.name == other.name

    def __hash__(self) -> int:
        return hash(self.name)

    def add_drone(self, drone: Drone) -> None:
        """Place a drone into this zone.

        Args:
            drone: The drone entering the zone.

        Raises:
            ValueError: If the zone is
            full/blocked or drone is already present.
        """
        if self.is_full():
            raise ValueError(f"Zone '{self.name}' is "
                             f"full or cannot accept drone '{drone}'")
        if drone in self.drones:
            raise ValueError(f"Drone '{drone}' "
                             f"is already in the zone '{self.name}'")
        self.drones.add(drone)

    def remove_drone(self, drone: Drone) -> None:
        """Remove a drone from this zone.

        Args:
            drone: The drone leaving the zone.

        Raises:
            ValueError: If the drone is not present in this zone.
        """
        if drone not in self.drones:
            raise ValueError(f"Drone {drone} not in zone {self.name}")
        self.drones.remove(drone)

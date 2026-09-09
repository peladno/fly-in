"""Module defining the Drone entity and its movement state in the network."""

from __future__ import annotations

from src.model.zone import Zone


class Drone:
    """Represents a drone navigating through the network.

    Attributes:
        id: Unique numeric identifier for the drone.
        current_zone: The zone where the drone is currently located.
        target_zone: Next zone the drone is heading towards (if in transit).
        steps_remaining: Ticks left before completing arrival to target_zone.
    """

    def __init__(
            self,
            id: int,
            current_zone: Zone,
            target_zone: Zone | None = None,
            steps_remaining: int = 0
                ):
        """Initialize a new Drone instance.

        Args:
            id: Unique positive integer identifier.
            current_zone: Starting zone of the drone.
            target_zone: Destination zone if currently in transit.
            steps_remaining: Turns left in transit (e.g. for restricted zones).
        """
        self.id = id
        self.current_zone = current_zone
        self.target_zone = target_zone
        self.steps_remaining = steps_remaining

    @property
    def is_in_transit(self) -> bool:
        """Check if the drone is currently traversing a connection.

        Returns:
            True if the drone has transit steps remaining, False otherwise.
        """
        return self.steps_remaining > 0

    def __repr__(self) -> str:
        """Return a technical string representation of the Drone."""
        return f"Drone(id={self.id}, zone='{self.current_zone.name}')"

    def __str__(self) -> str:
        """Return formatted drone name
        matching simulation protocol (e.g. D1)."""
        return f"D{self.id}"

    def __eq__(self, other: object) -> bool:
        """Compare drones for equality based on their unique ID."""
        if not isinstance(other, Drone):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Return hash based on the drone's unique ID for set/dict storage."""
        return hash(self.id)

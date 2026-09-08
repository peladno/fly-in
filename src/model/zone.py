from __future__ import annotations
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.model.drone import Drone   


class ZoneType(Enum):
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class Zone:
    def __init__(
            self, name: str,
            coor: tuple[float, float],
            zone_type: ZoneType = ZoneType.NORMAL,
            max_drones: int | None = 1
                ):
        self.name = name
        self.coor = coor
        self.zone_type = zone_type
        self.max_drones = max_drones
        self.drones: set[Drone] = set()

    def is_full(self) -> bool:
        if self.max_drones is None:
            return False
        if self.zone_type == ZoneType.BLOCKED:
            return True
        return len(self.drones) >= self.max_drones

    def __repr__(self) -> str:
        return f"Zone({self.name!r}, {self.zone_type.value})"

    def __str__(self) -> str:
        return self.name

    def add_drone(self, drone: Drone) -> None:
        if self.is_full():
            raise ValueError(f"Zone '{self.name}' is "
                             f"full or cannot accept drone '{drone}'")
        if drone in self.drones:
            raise ValueError(f"Drone '{drone}' "
                             f"is already in the zone '{self.name}'")
        self.drones.add(drone)

    def remove_drone(self, drone: Drone) -> None:
        if drone not in self.drones:
            raise ValueError(f"Drone {drone} not in zone {self.name}")
        self.drones.remove(drone)

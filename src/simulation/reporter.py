from __future__ import annotations

from src.model.drone import Drone
from src.model.zone import Zone


class SimulationReporter:
    def report_turn(self, movements: list[tuple[Drone, Zone | str]]) -> str:
        mov_str = " ".join(f"{drone}-{zone}" for drone, zone in movements)
        print(mov_str)
        return mov_str

"""Module providing turn event reporting for drone simulation movements."""

from __future__ import annotations

from src.model.drone import Drone
from src.model.zone import Zone

ANSI_COLORS: dict[str, str] = {
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "magenta": "\033[95m",
    "purple": "\033[95m",
    "cyan": "\033[96m",
    "orange": "\033[33m",
    "gray": "\033[90m",
    "grey": "\033[90m",
}
RESET = "\033[0m"


class SimulationReporter:
    """Formats and prints discrete turn movements to standard output."""

    def __init__(self, use_color: bool | None = False):
        """Initialize a SimulationReporter instance.

        Args:
            use_color: Whether to enable ANSI color output formatting.
        """
        self.use_color = use_color

    def report_turn(self, movements: list[tuple[Drone, Zone | str]]) -> str:
        """Format and print drone movements executed during a discrete turn.

        Args:
            movements: List of (drone, target) tuples where target is a Zone
                or connection string descriptor.

        Returns:
            Space-separated protocol string representing turn actions.
        """

        items: list[str] = []

        for drone, zone in movements:
            color_name = zone.color if isinstance(zone, Zone) else None
            color_code = ANSI_COLORS.get(color_name, "") if color_name else ""

            if self.use_color and color_code:
                items.append(f"{drone}-{color_code}{zone}{RESET}")
            else:
                items.append(f"{drone}-{zone}")

        mov_str = " ".join(items)
        print(mov_str)
        return mov_str

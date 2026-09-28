"""Module defining the turn-based simulation engine coordinating drone movement."""

from __future__ import annotations

from src.model.drone import Drone
from src.model.graph import Graph
from src.model.zone import Zone
from src.simulation.reporter import SimulationReporter


class SimulationEngine:
    """Manages the discrete turn-by-turn simulation of drones navigating paths.

    Attributes:
        graph: Flight network graph containing hubs and zones.
        paths: List of candidate traversal paths from start_hub to end_hub.
        reporter: Output formatter and emitter for turn events.
        drones: Fleet of drones instantiated in the simulation.
        drone_targets: Mapping from each drone to its remaining target waypoints.
        turns: Count of executed simulation turns.
    """

    def __init__(
        self,
        graph: Graph,
        paths: list[list[Zone]],
        reporter: SimulationReporter | None = None
    ) -> None:
        """Initialize the simulation engine and position drones at start_hub.

        Args:
            graph: The Graph model representing the network.
            paths: Non-empty list of available flight paths.
            reporter: Optional custom SimulationReporter instance.

        Raises:
            ValueError: If paths is empty or start_hub is missing.
        """
        if not paths:
            raise ValueError("No paths provided for simulation")

        self.graph = graph
        self.paths = paths
        self.reporter = reporter or SimulationReporter()
        self.drones: list[Drone] = []
        self.drone_targets: dict[Drone, list[Zone]] = {}
        self.turns: int = 0
        if self.graph.start_hub is None:
            raise ValueError("Graph has no start_hub")

        for i in range(1, graph.nb_drones + 1):
            drone = Drone(id=i, current_zone=self.graph.start_hub)
            self.drones.append(drone)
            self.graph.start_hub.add_drone(drone)
            self.drone_targets[drone] = list(self.paths[0][1:])

    def is_finished(self) -> bool:
        """Check if all drones have reached the destination end_hub.

        Returns:
            True if all drones occupy end_hub, False otherwise.
        """
        return all(drone.current_zone == self.graph.end_hub
                   for drone in self.drones)

    def step(self) -> list[tuple[Drone, Zone]]:
        """Execute a single discrete turn advancing active drones forward.

        Returns:
            List of (drone, next_zone) tuples moved during this turn.
        """
        movements: list[tuple[Drone, Zone]] = []

        active_drones = [
            d for d in self.drones
            if len(self.drone_targets[d]) > 0
        ]

        active_drones.sort(key=lambda d: len(self.drone_targets[d]))

        for drone in active_drones:
            next_zone = self.drone_targets[drone][0]

            if not next_zone.is_full():
                drone.current_zone.remove_drone(drone)
                next_zone.add_drone(drone)
                drone.current_zone = next_zone

                self.drone_targets[drone].pop(0)

                movements.append((drone, next_zone))

        self.reporter.report_turn(movements)

        return movements

    def run(self) -> int:
        """Run the simulation loop until all drones reach the destination.

        Returns:
            The total number of turns elapsed during the simulation.
        """
        while not self.is_finished():
            self.step()
            self.turns += 1
        return self.turns



# if __name__ == "__main__":
#     from src.parser import MapParser
#     from src.pathfinding import BFSRouter

#     map_path = "maps/easy/01_linear_path.txt"
#     print(f"=== Running Simulation on {map_path} ===")

#     parser = MapParser()
#     graph = parser.parse_file(map_path)

#     router = BFSRouter()
#     paths = router.find_paths(graph)

#     engine = SimulationEngine(graph, paths)
#     total_turns = engine.run()

#     print(f"=== Simulation Finished in {total_turns} turns ===")

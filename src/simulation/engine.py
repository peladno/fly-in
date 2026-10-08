"""Module defining the turn-based simulation engine coordinating drone
movement."""

from __future__ import annotations

from src.model.connection import Connection
from src.model.drone import Drone
from src.model.graph import Graph
from src.model.zone import Zone, ZoneType
from src.simulation.reporter import SimulationReporter


class SimulationEngine:
    """Manages the discrete turn-by-turn simulation of drones navigating paths.

    Attributes:
        graph: Flight network graph containing hubs and zones.
        paths: List of candidate traversal paths from start_hub to end_hub.
        reporter: Output formatter and emitter for turn events.
        drones: Fleet of drones instantiated in the simulation.
        drone_targets: Mapping from each drone to its remaining target
        waypoints.
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
            assigned_path = self.paths[(i - 1) % len(self.paths)]
            self.drone_targets[drone] = list(assigned_path[1:])

    def is_finished(self) -> bool:
        """Check if all drones have reached the destination end_hub.

        Returns:
            True if all drones occupy end_hub, False otherwise.
        """
        return all(drone.current_zone == self.graph.end_hub
                   for drone in self.drones)

    def step(self) -> list[tuple[Drone, Zone | str]]:
        """Execute a single discrete turn advancing active drones forward.

        Coordinates simultaneous drone movements:
        - Prioritizes drones closest to destination so departing drones
          vacate zones and links for incoming drones in the same turn.
        - Completes landings for in-transit drones arriving at destinations.
        - Respects zone occupancy limits and per-turn max_link_capacity.
        - Initiates 2-turn transit towards restricted zones by reserving
          inbound slots and emitting connection traversals.

        Returns:
            List of (drone, target) tuples where target is a Zone instance
            or connection string descriptor moved during this turn.
        """
        movements: list[tuple[Drone, Zone | str]] = []
        link_usage: dict[Connection, int] = {}

        active_drones = [
            d for d in self.drones
            if len(self.drone_targets[d]) > 0
        ]
        # Sort drones so that those closest to the goal move first.
        # This allows departing drones to vacate zones and connections
        # before following drones attempt to enter them in the same turn.
        # Drones already in transit are completing their arrival this turn,
        # so subtracting 0.5 gives them priority over drones still stationary.
        active_drones.sort(
            key=lambda d:
            len(self.drone_targets[d]) - (0.5 if d.is_in_transit else 0)
        )

        for drone in active_drones:
            if drone.is_in_transit:
                # Phase 1: Complete flight for drones arriving at destination
                drone.steps_remaining -= 1
                if drone.steps_remaining == 0:
                    dest_zone = drone.target_zone
                    if dest_zone is not None:
                        dest_zone.add_drone(drone)
                        drone.current_zone = dest_zone
                        drone.target_zone = None
                        self.drone_targets[drone].pop(0)
                        movements.append((drone, dest_zone))
            else:
                # Phase 2: Handle stationary drone departure
                next_zone = self.drone_targets[drone][0]
                conn = self.graph.get_connection(drone.current_zone, next_zone)
                conn_limit = (
                    conn.max_link_capacity
                    if (conn and conn.max_link_capacity is not None)
                    else 1
                )
                link_available = (
                    (conn is None) or (link_usage.get(conn, 0) < conn_limit)
                )

                if next_zone.zone_type != ZoneType.RESTRICTED:
                    # Case A: Standard 1-turn traversal to normal/priority zone
                    if not next_zone.is_full() and link_available:
                        drone.current_zone.remove_drone(drone)
                        next_zone.add_drone(drone)
                        drone.current_zone = next_zone
                        self.drone_targets[drone].pop(0)
                        movements.append((drone, next_zone))
                        if conn:
                            link_usage[conn] = link_usage.get(conn, 0) + 1
                else:
                    # Case B: Multi-turn movement towards a restricted zone
                    # Only allow departure if inbound transit pipeline has room
                    inbound = sum(1 for d in self.drones
                                  if d.target_zone == next_zone)
                    limit = (next_zone.max_drones
                             if next_zone.max_drones is not None else 1)

                    if (inbound < limit) and link_available:
                        origin_name = drone.current_zone.name
                        drone.current_zone.remove_drone(drone)
                        drone.target_zone = next_zone
                        drone.steps_remaining = 1
                        movements.append(
                            (drone, f"{origin_name}-{next_zone.name}"))
                        if conn:
                            link_usage[conn] = link_usage.get(conn, 0) + 1

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

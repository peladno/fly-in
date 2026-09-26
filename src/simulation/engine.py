from src.model.drone import Drone
from src.model.graph import Graph
from src.model.zone import Zone
from src.simulation.reporter import SimulationReporter


class SimulationEngine:
    def __init__(
        self,
        graph: Graph,
        paths: list[list[Zone]],
        reporter: SimulationReporter | None = None
    ) -> None:
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

    def is_finished(self) -> bool:  # TODO
        raise NotImplementedError

    def step(self) -> list[None]:   # TODO
        raise NotImplementedError

    def run(self) -> int:
        raise NotImplementedError   # TODO

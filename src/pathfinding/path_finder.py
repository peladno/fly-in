"""Module implementing graph pathfinding algorithms for drone routing."""

from __future__ import annotations
from collections import deque

from src.model.graph import Graph
from src.model.zone import Zone, ZoneType
from src.parser.exceptions import InvalidSyntaxError
from src.pathfinding.router import Router


class BFSRouter(Router):
    """Pathfinder implementation using Breadth-First Search (BFS)."""

    def _find_single_path(
        self, graph: Graph, excluded_zones: set[Zone]
    ) -> list[Zone] | None:
        """Find a single valid shortest path from start_hub to end_hub via BFS.

        Args:
            graph: The network Graph containing zones and connections.
            excluded_zones: Set of zones unavailable due to capacity limits.

        Returns:
            A list of Zone instances representing the path from start to end,
            or None if no path could be found.

        Raises:
            InvalidSyntaxError: If start_hub or end_hub are not set in graph.
        """
        if graph.start_hub is None or graph.end_hub is None:
            raise InvalidSyntaxError("Error: invalid start_hub or end_hub")

        queue = deque([[graph.start_hub]])
        visited: set[Zone] = {graph.start_hub}
        while queue:
            current_path = queue.popleft()
            current_zone = current_path[-1]

            if current_zone == graph.end_hub:
                return current_path

            for neighbor in graph.get_neighbors(current_zone):
                if (
                    neighbor not in visited
                    and neighbor.zone_type != ZoneType.BLOCKED
                    and neighbor not in excluded_zones
                ):
                    visited.add(neighbor)
                    new_path = current_path + [neighbor]
                    queue.append(new_path)

        return None

    def find_paths(self, graph: Graph) -> list[list[Zone]]:
        """Find multiple valid paths from start_hub to end_hub using BFS.

        Iteratively discovers paths while respecting intermediate zone
        capacities and avoiding blocked zones. Tracks zone usage to exclude
        saturated zones across iterations.

        Args:
            graph: The network Graph containing zones, connections, and hubs.

        Returns:
            A list of paths, each represented as a list of Zone instances,
            or an empty list if no traversable path exists.

        Raises:
            InvalidSyntaxError: If start_hub or end_hub are not set in graph.
        """

        paths: list[list[Zone]] = []
        excluded_zones: set[Zone] = set()
        zone_usage: dict[Zone, int] = {}

        while True:
            path = self._find_single_path(graph, excluded_zones)
            if path is None:
                break
            paths.append(path)

            for zone in path[1:-1]:
                zone_usage[zone] = zone_usage.get(zone, 0) + 1
                limit = zone.max_drones if zone.max_drones is not None else 1
                if zone_usage[zone] >= limit:
                    excluded_zones.add(zone)
        return paths


# if __name__ == "__main__":
#     from src.parser import MapParser

#     map_file = "maps/easy/01_linear_path.txt"
#     parser = MapParser()
#     graph = parser.parse_file(map_file)

#     print(f"--- Mapa cargado: {map_file} ---")
#     print(f"Total drones: {graph.nb_drones}")
#     print(f"Start: {graph.start_hub}")
#     print(f"Goal: {graph.end_hub}")
#     print(f"Total zonas: {len(graph.zones)}")

#     router = BFSRouter()
#     paths = router.find_paths(graph)

#     print("\n--- Rutas encontradas ---")
#     if paths:
#         for idx, path in enumerate(paths, start=1):
#             path_str = " -> ".join(zone.name for zone in path)
#             print(f"Camino {idx}: {path_str}")
#     else:
#         print("No se encontró ningún camino a la meta.")

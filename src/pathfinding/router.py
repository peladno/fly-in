"""Module defining abstract router interface for pathfinding strategies."""

from __future__ import annotations
from abc import ABC, abstractmethod

from src.model.graph import Graph
from src.model.zone import Zone


class Router(ABC):
    """Abstract base class defining the routing interface
    for graph traversal."""

    @abstractmethod
    def find_paths(self, graph: Graph) -> list[list[Zone]]:
        """Find one or more valid paths from start_hub to end_hub.

        Args:
            graph: The Graph representation of the flight network.

        Returns:
            A list of paths, where each path is a list of Zone instances.
        """
        pass

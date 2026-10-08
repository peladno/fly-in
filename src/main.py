"""CLI entry point for the Fly-in drone routing and simulation application."""

from __future__ import annotations
import argparse
import os
import sys


# Ensure project root is present in sys.path for direct invocation
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

from src.parser import MapParser  # noqa: E402
from src.parser.exceptions import MapParserError  # noqa: E402
from src.pathfinding import BFSRouter  # noqa: E402
from src.simulation import SimulationEngine  # noqa: E402
from src.simulation.reporter import SimulationReporter  # noqa: E402


def main() -> None:
    """Parse command line arguments and execute the end-to-end simulation."""
    parser = argparse.ArgumentParser(
        description="Fly-in: Drone routing and discrete simulation system."
    )
    parser.add_argument(
        "map_file",
        help="Path to the .map / map file to simulate"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode to show detailed metrics"
    )
    parser.add_argument(
        "--color",
        action="store_true",
        help="Enable colored visual representation of drone movements"
    )
    args = parser.parse_args()

    try:
        parser_map = MapParser()
        graph = parser_map.parse_file(args.map_file)

        router = BFSRouter()
        paths = router.find_paths(graph)
        if not paths:
            print("Error: No valid path found from start_hub to end_hub.",
                  file=sys.stderr)
            sys.exit(1)

        reporter = SimulationReporter(use_color=args.color)
        engine = SimulationEngine(graph, paths, reporter=reporter)

        total_turns = engine.run()

        if args.debug:
            print(f"[DEBUG] Simulation finished in {total_turns} turns.")

    except MapParserError as e:
        print(f"Parsing error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

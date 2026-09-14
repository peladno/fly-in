"""Module responsible for parsing and validating .map files into Graph
instances."""

from __future__ import annotations
from src.model import Connection, Zone, Graph, ZoneType
from src.parser.exceptions import (
    InvalidSyntaxError,
    MapParserError,
    UnknownZoneError,
)


class MapParser:
    """Parser that validates and converts .map file contents into a Graph."""

    def parse_file(self, file_path: str) -> Graph:
        """Parse a .map file and construct a validated flight network Graph.

        Args:
            file_path: Path to the .map file to be parsed.

        Returns:
            A fully initialized and validated Graph instance.

        Raises:
            MapParserError: If the file is not found or has parsing violations.
        """
        graph = Graph()
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line_num, raw_line in enumerate(f, start=1):
                    self._parse_line(raw_line, line_num, graph)
        except FileNotFoundError:
            raise MapParserError(f"Map file not found: {file_path}")

        graph.validate()
        return graph

    def _parse_line(self, raw_line: str, line_num: int, graph: Graph) -> None:
        """Parse and route a single line of the map file by its prefix
        directive.

        Args:
            raw_line: Raw text line directly from the file.
            line_num: Line number in the file for error reporting.
            graph: Graph instance being populated.

        Raises:
            InvalidSyntaxError: If the line has unknown or malformed
            directives.
        """
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            return

        if ":" not in line:
            raise InvalidSyntaxError(f"Error: Line {line_num}: Missing ':' "
                                     f"directive separator -> '{line}'")

        prefix, content = line.split(":", 1)
        prefix = prefix.strip()
        content = content.strip()

        if prefix == "nb_drones":
            if graph.nb_drones > 0:
                raise InvalidSyntaxError(f"Error: Line {line_num}: "
                                         "'nb_drones' already defined")
            graph.nb_drones = self._parse_nb_drones(content, line_num)

        elif prefix == "start_hub":
            if graph.start_hub is not None:
                raise InvalidSyntaxError(f"Error: Line {line_num}: "
                                         "'start_hub' already defined")
            zone = self._parse_hub(content, line_num, is_unlimited=True)
            graph.add_zone(zone)
            graph.start_hub = zone

        elif prefix == "end_hub":
            if graph.end_hub is not None:
                raise InvalidSyntaxError(f"Error: Line {line_num}: 'end_hub' "
                                         "already defined")
            zone = self._parse_hub(content, line_num, is_unlimited=True)
            graph.add_zone(zone)
            graph.end_hub = zone

        elif prefix == "hub":
            zone = self._parse_hub(content, line_num, is_unlimited=False)
            graph.add_zone(zone)
        elif prefix == "connection":
            conn = self._parse_connection(content, line_num, graph)
            graph.add_connection(conn)

        else:
            raise InvalidSyntaxError(f"Error: Line {line_num}: "
                                     f"Unknown directive '{prefix}'")

    def _parse_nb_drones(self, value: str, line_num: int) -> int:
        """Parse and validate total drone count integer.

        Args:
            value: String containing the drone count.
            line_num: Line number for error reporting.

        Returns:
            The parsed positive integer.

        Raises:
            InvalidSyntaxError: If value is non-numeric or <= 0.
        """
        try:
            nb = int(value)
            if nb <= 0:
                raise InvalidSyntaxError(f"Error: Line {line_num}: "
                                         "Drone count must "
                                         f"be greater than 0, got '{value}'")
            return nb
        except ValueError:
            raise InvalidSyntaxError(f"Error: Line {line_num}: "
                                     "Drone count must "
                                     f"be an integer, got '{value}'")

    def _parse_hub(
            self, content: str, line_num: int, is_unlimited: bool = False
            ) -> Zone:
        """Parse zone declaration line and return a new Zone instance.

        Args:
            content: Zone parameters string (name x y [metadata]).
            line_num: Line number for error reporting.
            is_unlimited: True if capacity is unbounded (start_hub/end_hub).

        Returns:
            The newly created Zone instance.

        Raises:
            InvalidSyntaxError: If syntax is invalid, name has hyphens,
                or coordinates cannot be parsed as floats.
        """
        tokens = content.split()
        if len(tokens) < 3:
            raise InvalidSyntaxError(f"Error: Line {line_num}: "
                                     "Hub requires at least "
                                     f"3 values (name, x, y), "
                                     f"got {len(tokens)}")
        if "-" in tokens[0]:
            raise InvalidSyntaxError(f"{tokens[0]} cannot have a '-'")

        try:
            x = float(tokens[1])
            y = float(tokens[2])
        except ValueError:
            raise InvalidSyntaxError(f"Error: {tokens[1]} and {tokens[2]} "
                                     "should be floats")

        zone_type, max_drones = self._parse_metadata(tokens[3:], line_num)
        final_max = None if is_unlimited else max_drones

        return Zone(
            name=tokens[0],
            coord=(x, y),
            zone_type=zone_type,
            max_drones=final_max
            )

    def _parse_metadata(
            self, meta_tokens: list[str], line_num: int
            ) -> tuple[ZoneType, int]:
        """Extract and validate zone metadata attributes.

        Args:
            meta_tokens: List of key=value metadata strings.
            line_num: Line number for error reporting.

        Returns:
            A tuple of (ZoneType, max_drones).

        Raises:
            InvalidSyntaxError: If format or values are invalid.
        """
        zone_type = ZoneType.NORMAL
        max_drones = 1

        for token in meta_tokens:
            if "=" not in token:
                raise InvalidSyntaxError(f"Error: Line {line_num}: "
                                         f"Invalid metadata token '{token}'")
            key, value = token.split("=", 1)

            if key == "zone":
                try:
                    zone_type = ZoneType(value)
                except ValueError:
                    raise InvalidSyntaxError(f"Error: Line {line_num}: "
                                             f"Invalid zone type '{value}'")

            elif key == "max_drones":
                try:
                    max_drones = int(value)
                    if max_drones <= 0:
                        raise InvalidSyntaxError(f"Error: Line {line_num}: "
                                                 "max_drones must be > 0")
                except ValueError:
                    raise InvalidSyntaxError(f"Error: Line {line_num}: "
                                             f"'{value}' is not an integer")

            elif key == "color":
                pass
            else:
                raise InvalidSyntaxError(f"Error: Line {line_num}: Unknown "
                                         f"metadata key '{key}'")
        return zone_type, max_drones

    def _parse_connection(self,
                          content: str,
                          line_num: int,
                          graph: Graph
                          ) -> Connection:
        """Parse connection declaration and link two existing zones.

        Args:
            content: Connection specification string.
            line_num: Line number for error reporting.
            graph: Graph holding existing zones to connect.

        Returns:
            The newly created Connection instance.

        Raises:
            InvalidSyntaxError: If connection format or capacity is invalid.
            UnknownZoneError: If referenced zones do not exist in graph.
        """
        link_content = content.strip().split()

        if "-" not in link_content[0]:
            raise InvalidSyntaxError(f"Error: {link_content[0]} needs '-'")

        zone_a_name, zone_b_name = link_content[0].split("-", 1)

        if not zone_b_name or not zone_a_name:
            raise InvalidSyntaxError(f"Error: Line {line_num}, both zone has "
                                     "to exist")

        if zone_a_name == zone_b_name:
            raise InvalidSyntaxError(f"Error: Line {line_num}, both names has"
                                     "to be differents")

        if zone_a_name not in graph.zones or zone_b_name not in graph.zones:
            raise UnknownZoneError(f"Error: Line {line_num} "
                                   f"{zone_a_name or zone_b_name} "
                                   "is not in the zone")
        max_capacity: int | None = None

        if len(link_content) > 1:

            token = link_content[1].strip("[]")
            if "=" not in token:
                raise InvalidSyntaxError(f"Error: Line {line_num}, "
                                         "syntaxis has to be key=value")
            k_token, v_token = token.strip().split("=", 1)

            if k_token != "max_link_capacity":
                raise InvalidSyntaxError(f"Error: Line {line_num}"
                                         "unknown metadata")
            try:
                max_capacity = int(v_token)
                if max_capacity <= 0:
                    raise InvalidSyntaxError(f"Error: Line {line_num} "
                                             f"{max_capacity} needs"
                                             "to be a positive int")
            except ValueError:
                raise InvalidSyntaxError(f"Error: Line {line_num}"
                                         f"{v_token} needs to be a int")

        zone_a = graph.zones[zone_a_name]
        zone_b = graph.zones[zone_b_name]
        return Connection(zone_a, zone_b, max_capacity)

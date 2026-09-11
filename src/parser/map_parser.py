# MapParser
# ├── parse_file(file_path: str) -> Graph        # Abre el archivo de forma segura y coordina
# ├── _parse_line(line: str, graph: Graph)       # Limpia y clasifica cada línea según su prefijo
# ├── _parse_nb_drones(value_str: str) -> int    # Parsea la cantidad de drones
# ├── _parse_hub(...) -> Zone                    # Parsea start_hub, end_hub, hub con coordenadas
# ├── _parse_metadata(...) -> dict               # Extrae zone=..., max_drones=..., color=...
# └── _parse_connection(...) -> Connection       # Parsea connection: zone1-zone2
from __future__ import annotations
from src.model.graph import Graph
from src.model.zone import Zone, ZoneType
from src.parser.exceptions import InvalidSyntaxError, MapParserError


class MapParser:
    def parse_file(self, file_path: str) -> Graph:
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
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            return

        if ":" not in line:
            raise InvalidSyntaxError(f"Line {line_num}: Missing ':' "
                                     f"directive separator -> '{line}'")

        prefix, content = line.split(":", 1)
        prefix = prefix.strip()
        content = content.strip()

        if prefix == "nb_drones":
            if graph.nb_drones > 0:
                raise InvalidSyntaxError(f"Line {line_num}: "
                                         f"'nb_drones' already defined")
            graph.nb_drones = self._parse_nb_drones(content, line_num)
        elif prefix == "start_hub":
            ...
        elif prefix == "end_hub":
            ...
        elif prefix == "hub":
            ...
        elif prefix == "connection":
            ...
        else:
            raise InvalidSyntaxError(f"Line {line_num}: "
                                     f"Unknown directive '{prefix}'")

    def _parse_nb_drones(self, value: str, line_num: int) -> int:
        try:
            nb = int(value)
            if nb <= 0:
                raise InvalidSyntaxError(f"Line {line_num}: Drone count must "
                                         f"be greater than 0, got '{value}'")
            return nb
        except ValueError:
            raise InvalidSyntaxError(f"Line {line_num}: Drone count must "
                                     f"be an integer, got '{value}'")

    def _parse_hub(
            self, content: str, line_num: int, is_unlimited: bool = False
            ) -> Zone:
        tokens = content.split()
        if len(tokens) < 3:
            raise InvalidSyntaxError(f"Line {line_num}: Hub requires at least "
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

        return Zone(tokens[0], (x, y))

    def _parse_metadata(
            self, meta_tokens: list[str], line_num: int
            ) -> tuple[ZoneType, int]:
        raise NotImplementedError

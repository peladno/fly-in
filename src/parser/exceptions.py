from __future__ import annotations


class MapParserError(Exception):
    """Base exception for all map parsing errors."""
    pass


class InvalidSyntaxError(MapParserError):
    """Raised when a line in the map file has invalid syntax or format."""
    pass


class DuplicateZoneError(MapParserError):
    """Raised when a zone name is declared more than once."""
    pass


class UnknownZoneError(MapParserError):
    """Raised when a connection references a zone that does not exist."""
    pass


class MissingHubError(MapParserError):
    """Raised when a mandatory hub (start_hub or end_hub) is missing."""
    pass

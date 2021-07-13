from typing import Callable, List

# Definition of a coordinate list
Coordinate = List[float]
Coordinates = List[Coordinate]


def _make_number_parser(decimal: str) -> Callable[[str], float]:
    """ Helper to create a number parser with a potentially custom
        decimal separator. When this is not the '.' character, each
        number will replace the given decimal separator with '.'
        before calling the built-in `float` function.
    """
    if decimal == '.':
        return float

    def inner(value: str) -> float:
        return float(value.replace(decimal, '.'))

    return inner


def parse_coordinates(value: str, cs: str = ',', ts: str = ' ',
                      decimal: str = '.') -> Coordinates:
    """ Parses the the values of a gml:coordinates node to a list of
        lists of floats. Takes the coordinate separator and tuple
        separator into account, and also custom decimal separators.
    """

    number_parser = _make_number_parser(decimal)

    return [
        [
            number_parser(number)
            for number in coordinate.strip().split(ts)
        ]
        for coordinate in value.strip().split(cs)
    ]


def parse_poslist(value: str, dimensions: int = 2) -> Coordinates:
    """ Parses the value of a single gml:posList to a `Coordinates`
        structure.
    """
    raw = [float(v) for v in value.split()]
    if len(raw) % dimensions > 0:
        raise ValueError('Invalid dimensionality of pos list')

    return [
        raw[i:i + dimensions]
        for i in range(0, len(raw), dimensions)
    ]


def parse_pos(value: str) -> Coordinate:
    """ Parses a single gml:pos to a `Coordinate` structure.
    """
    return [float(v) for v in value.split()]


def swap_coordinates_xy(coordinates: Coordinates):
    """ Swaps the X and Y coordinates in-place of a given coordinates list
    """
    for coordinate in coordinates:
        coordinate[1], coordinate[0] = coordinate[0], coordinate[1]

# ------------------------------------------------------------------------------
#
# Project: pygml <https://github.com/geopython/pygml>
# Authors: Fabian Schindler <fabian.schindler@eox.at>
#
# ------------------------------------------------------------------------------
# Copyright (C) 2021 EOX IT Services GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies of this Software or works derived from this Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# ------------------------------------------------------------------------------


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
        tuple(
            number_parser(number)
            for number in coordinate.strip().split(ts)
        )
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
        tuple(raw[i:i + dimensions])
        for i in range(0, len(raw), dimensions)
    ]


def parse_pos(value: str) -> Coordinate:
    """ Parses a single gml:pos to a `Coordinate` structure.
    """
    return tuple(float(v) for v in value.split())


def swap_coordinates_xy(coordinates: Coordinates) -> Coordinates:
    """ Swaps the X and Y coordinates of a given coordinates list
    """
    return [
        (coordinate[1], coordinate[0], *coordinate[2:])
        for coordinate in coordinates
    ]

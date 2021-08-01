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


from typing import Callable

from .types import Coordinates, Coordinate


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

        >>> parse_coordinates('12.34 56.7,89.10 11.12')
        [(12.34, 56.7), (89.1, 11.12)]
        >>> parse_coordinates('12.34 56.7;89.10 11.12', cs=';')
        [(12.34, 56.7), (89.1, 11.12)]
        >>> parse_coordinates('12.34:56.7,89.10:11.12', ts=':')
        [(12.34, 56.7), (89.1, 11.12)]
        >>> parse_coordinates('12.34:56.7;89.10:11.12', cs=';', ts=':')
        [(12.34, 56.7), (89.1, 11.12)]
        >>> parse_coordinates(
        ...     '12,34:56,7;89,10:11,12', cs=';', ts=':', decimal=','
        ... )
        [(12.34, 56.7), (89.1, 11.12)]
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

        >>> parse_poslist('12.34 56.7 89.10 11.12')
        [(12.34, 56.7), (89.1, 11.12)]
        >>> parse_poslist('12.34 56.7 89.10 11.12 13.14 15.16', dimensions=3)
        [(12.34, 56.7, 89.1), (11.12, 13.14, 15.16)]
        >>> parse_poslist('12.34 56.7 89.10 11.12', dimensions=3)
        Traceback (most recent call last):
            ...
        ValueError: Invalid dimensionality of pos list
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

        >>> parse_pos('12.34 56.7')
        (12.34, 56.7)
        >>> parse_pos('12.34 56.7 89.10')
        (12.34, 56.7, 89.1)
    """
    return tuple(float(v) for v in value.split())


def swap_coordinate_xy(coordinate: Coordinate) -> Coordinate:
    """ Swaps the X and Y coordinates of a given coordinate

        >>> swap_coordinate_xy((12.34, 56.7))
        (56.7, 12.34)
        >>> swap_coordinate_xy((12.34, 56.7, 89.10))
        (56.7, 12.34, 89.1)
    """
    return (coordinate[1], coordinate[0], *coordinate[2:])


def swap_coordinates_xy(coordinates: Coordinates) -> Coordinates:
    """ Swaps the X and Y coordinates of a given coordinates list

        >>> swap_coordinates_xy(
        ...     [(12.34, 56.7), (89.10, 11.12)]
        ... )
        [(56.7, 12.34), (11.12, 89.1)]
        >>> swap_coordinates_xy(
        ...     [(12.34, 56.7, 89.10), (11.12, 13.14, 15.16)]
        ... )
        [(56.7, 12.34, 89.1), (13.14, 11.12, 15.16)]
    """
    return [
        (coordinate[1], coordinate[0], *coordinate[2:])
        for coordinate in coordinates
    ]

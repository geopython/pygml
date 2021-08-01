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

from typing import Optional
from collections.abc import Sequence

from .types import GeomDict


def get_dimensionality(geometry: GeomDict) -> Optional[int]:
    """ Returns the dimensionality of a given GeoJSON geometry.
        This is obtained by descending into the first coordinate
        and using its length.
        When no coordinates can be retrieved (e.g: in case of
        GeometryCollections) None is returned.

        >>> get_dimensionality({
        ...     'type': 'Polygon',
        ...     'coordinates': [
        ...         [
        ...             (0.5, 1.0),
        ...             (0.5, 2.0),
        ...             (1.5, 2.0),
        ...             (1.5, 1.0),
        ...             (0.5, 1.0)
        ...         ]
        ...     ]
        ... })
        2
        >>> get_dimensionality({
        ...     'type': 'MultiPoint',
        ...     'coordinates': [
        ...         (1.0, 1.0, 1.0),
        ...         (2.0, 2.0, 1.0),
        ...     ]
        ... })
        3
        >>> get_dimensionality({
        ...     'type': 'GeometryCollection',
        ...     'geometries': [
        ...         {
        ...             'type': 'Point',
        ...             'coordinates': (1.0, 1.0)
        ...         },
        ...         {
        ...             'type': 'Polygon',
        ...             'coordinates': [
        ...                 [(1.0, 1.0)],
        ...                 [(1.0, 1.0)],
        ...             ]
        ...         },
        ...     ]
        ... })
    """

    coordinates = geometry.get('coordinates')

    if coordinates:
        # drill down into nested coordinates
        while isinstance(coordinates[0], Sequence):
            coordinates = coordinates[0]
        return len(coordinates)
    return None

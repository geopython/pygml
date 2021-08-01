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


from pygml.dimensionality import get_dimensionality


def test_dimensionality_point():
    assert 2 == get_dimensionality({
        'type': 'Point',
        'coordinates': (1.0, 1.0)
    })

    assert 3 == get_dimensionality({
        'type': 'Point',
        'coordinates': (1.0, 1.0, 1.0)
    })


def test_dimensionality_multi_point():
    assert 2 == get_dimensionality({
        'type': 'MultiPoint',
        'coordinates': [
            (1.0, 1.0),
            (2.0, 2.0),
        ]
    })

    assert 3 == get_dimensionality({
        'type': 'MultiPoint',
        'coordinates': [
            (1.0, 1.0, 1.0),
            (2.0, 2.0, 1.0),
        ]
    })


def test_dimensionality_linestring():
    assert 2 == get_dimensionality({
        'type': 'LineString',
        'coordinates': [
            (2.0, 1.0),
            (1.0, 2.0)
        ]
    })

    assert 3 == get_dimensionality({
        'type': 'LineString',
        'coordinates': [
            (2.0, 1.0, 1.0),
            (1.0, 2.0, 1.0)
        ]
    })


def test_dimensionality_multi_linestring():
    assert 2 == get_dimensionality({
        'type': 'MultiLineString',
        'coordinates': [
            [
                (1.0, 1.0),
                (2.0, 2.0)
            ], [
                (3.0, 3.0),
                (4.0, 4.0)
            ],
        ]
    })

    assert 3 == get_dimensionality({
        'type': 'MultiLineString',
        'coordinates': [
            [
                (1.0, 1.0, 1.0),
                (2.0, 2.0, 1.0)
            ], [
                (3.0, 3.0, 1.0),
                (4.0, 4.0, 1.0)
            ],
        ]
    })


def test_dimensionality_polygon():
    assert 2 == get_dimensionality({
        'type': 'Polygon',
        'coordinates': [
            [
                (0.5, 1.0),
                (0.5, 2.0),
                (1.5, 2.0),
                (1.5, 1.0),
                (0.5, 1.0)
            ]
        ]
    })

    assert 3 == get_dimensionality({
        'type': 'Polygon',
        'coordinates': [
            [
                (0.5, 1.0, 1.0),
                (0.5, 2.0, 1.0),
                (1.5, 2.0, 1.0),
                (1.5, 1.0, 1.0),
                (0.5, 1.0, 1.0)
            ]
        ]
    })


def test_dimensionality_multi_polygon():
    assert 2 == get_dimensionality({
        'type': 'MultiPolygon',
        'coordinates': [
            [
                [
                    (0.0, 0.0),
                    (1.0, 0.0),
                    (0.0, 1.0),
                    (0.0, 0.0)
                ],
                [
                    (0.2, 0.2),
                    (0.5, 0.2),
                    (0.2, 0.5),
                    (0.2, 0.2)
                ],
            ],
            [
                [
                    (10.0, 10.0),
                    (11.0, 10.0),
                    (10.0, 11.0),
                    (10.0, 10.0)
                ],
                [
                    (10.2, 10.2),
                    (10.5, 10.2),
                    (10.2, 10.5),
                    (10.2, 10.2)
                ],
            ]
        ]
    })

    assert 3 == get_dimensionality({
        'type': 'MultiPolygon',
        'coordinates': [
            [
                [
                    (0.0, 0.0, 1.0),
                    (1.0, 0.0, 1.0),
                    (0.0, 1.0, 1.0),
                    (0.0, 0.0, 1.0)
                ],
                [
                    (0.2, 0.2, 1.0),
                    (0.5, 0.2, 1.0),
                    (0.2, 0.5, 1.0),
                    (0.2, 0.2, 1.0)
                ],
            ],
            [
                [
                    (10.0, 10.0, 1.0),
                    (11.0, 10.0, 1.0),
                    (10.0, 11.0, 1.0),
                    (10.0, 10.0, 1.0)
                ],
                [
                    (10.2, 10.2, 1.0),
                    (10.5, 10.2, 1.0),
                    (10.2, 10.5, 1.0),
                    (10.2, 10.2, 1.0)
                ],
            ]
        ]
    })


def test_dimensionality_geometrycollection():
    assert None is get_dimensionality({
        'type': 'GeometryCollection',
        'geometries': [
            {
                'type': 'Point',
                'coordinates': (1.0, 1.0)
            },
            {
                'type': 'Polygon',
                'coordinates': [
                    [(1.0, 1.0)],
                    [(1.0, 1.0)],
                ]
            },
        ]
    })

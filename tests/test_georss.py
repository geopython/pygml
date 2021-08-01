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


from lxml import etree

from pygml.georss import encode_georss, parse_georss

from .util import compare_trees


def test_parse_point():
    # basic test
    result = parse_georss(
        etree.fromstring("""
            <georss:point xmlns:georss="http://www.georss.org/georss">
                1.0 1.0
            </georss:point>
        """)
    )
    assert result == {'type': 'Point', 'coordinates': (1.0, 1.0)}


def test_parse_line():
    # basic test
    result = parse_georss(
        etree.fromstring("""
            <georss:line xmlns:georss="http://www.georss.org/georss">
                1.0 2.0 2.0 1.0
            </georss:line>
        """)
    )
    assert result == {
        'type': 'LineString',
        'coordinates': [
            (2.0, 1.0),
            (1.0, 2.0)
        ]
    }


def test_parse_box():
    # basic test
    result = parse_georss(
        etree.fromstring("""
            <georss:box xmlns:georss="http://www.georss.org/georss">
                1.0 0.5 2.0 1.5
            </georss:box>
        """)
    )
    assert result == {
        'type': 'Polygon',
        'bbox': (0.5, 1.0, 1.5, 2.0),
        'coordinates': [
            [
                (0.5, 1.0),
                (0.5, 2.0),
                (1.5, 2.0),
                (1.5, 1.0),
                (0.5, 1.0)
            ]
        ]
    }


def test_parse_polygon():
    # basic test
    result = parse_georss(
        etree.fromstring("""
            <georss:polygon xmlns:georss="http://www.georss.org/georss">
                1.0 0.5 2.0 0.5 2.0 1.5 1.0 1.5 1.0 0.5
            </georss:polygon>
        """)
    )
    assert result == {
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
    }


def test_parse_where():
    # TODO: add tests as soon as gml 3.1 is done
    pass


def test_encode_point():
    # test that simple points can be encoded
    result = encode_georss({'type': 'Point', 'coordinates': (1.0, 2.0)})
    expected = etree.fromstring("""
        <georss:point xmlns:georss="http://www.georss.org/georss">
            2.0 1.0
        </georss:point>
    """)
    assert compare_trees(
        expected, result
    ), f'{etree.tostring(expected)} != {etree.tostring(result)}'

    # test that >2D geometries or with a specific CRS
    # can only be encoded using georss:where and GML
    result = encode_georss({'type': 'Point', 'coordinates': (1.0, 2.0, 1.0)})
    assert result.tag == '{http://www.georss.org/georss}where'
    assert etree.QName(result[0].tag).localname == 'Point'

    result = encode_georss({
        'type': 'Point',
        'coordinates': (1.0, 2.0),
        'crs': {
            'type': 'name',
            'properties': {
                'name': 'EPSG:3857'
            }
        }
    })
    assert result.tag == '{http://www.georss.org/georss}where'
    assert etree.QName(result[0].tag).localname == 'Point'


def test_encode_multi_point():
    result = encode_georss({
        'type': 'MultiPoint',
        'coordinates': [
            (1.0, 2.0),
            (3.0, 4.0),
        ]
    })
    assert result.tag == '{http://www.georss.org/georss}where'
    assert etree.QName(result[0].tag).localname == 'MultiPoint'


def test_encode_linestring():
    # test that simple points can be encoded
    result = encode_georss({
        'type': 'LineString',
        'coordinates': [
            (1.0, 2.0),
            (3.0, 4.0),
        ]
    })
    expected = etree.fromstring("""
        <georss:line xmlns:georss="http://www.georss.org/georss">
            2.0 1.0 4.0 3.0
        </georss:line>
    """)
    assert compare_trees(
        expected, result
    ), f'{etree.tostring(expected)} != {etree.tostring(result)}'

    # test that >2D geometries or with a specific CRS
    # can only be encoded using georss:where and GML
    result = encode_georss({
        'type': 'LineString',
        'coordinates': [
            (1.0, 2.0, 1.0),
            (3.0, 4.0, 1.0),
        ]
    })
    assert result.tag == '{http://www.georss.org/georss}where'
    assert etree.QName(result[0].tag).localname == 'LineString'

    result = encode_georss({
        'type': 'LineString',
        'coordinates': [
            (1.0, 2.0),
            (3.0, 4.0),
        ],
        'crs': {
            'type': 'name',
            'properties': {
                'name': 'EPSG:3857'
            }
        }
    })
    assert result.tag == '{http://www.georss.org/georss}where'
    assert etree.QName(result[0].tag).localname == 'LineString'


def test_encode_multi_linestring():
    result = encode_georss({
        'type': 'MultiLineString',
        'coordinates': [
            [
                (1.0, 2.0),
                (3.0, 4.0),
            ], [
                (11.0, 12.0),
                (13.0, 14.0),
            ]
        ]
    })
    assert result.tag == '{http://www.georss.org/georss}where'
    assert etree.QName(result[0].tag).localname == 'MultiCurve'


def test_encode_polygon():
    result = encode_georss({
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
    expected = etree.fromstring("""
        <georss:polygon xmlns:georss="http://www.georss.org/georss">
            1.0 0.5 2.0 0.5 2.0 1.5 1.0 1.5 1.0 0.5
        </georss:polygon>
    """)
    assert compare_trees(
        expected, result
    ), f'{etree.tostring(expected)} != {etree.tostring(result)}'

    # test that >2D geometries or with a specific CRS or polygons with holes
    # can only be encoded using georss:where and GML
    result = encode_georss({
        'type': 'Polygon',
        'coordinates': [
            [
                (0.5, 1.0),
                (0.5, 2.0),
                (1.5, 2.0),
                (1.5, 1.0),
                (0.5, 1.0)
            ], [
                (0.6, 1.1),
                (0.6, 1.9),
                (1.4, 1.9),
                (1.4, 1.1),
                (0.6, 1.1)
            ]
        ]
    })
    assert result.tag == '{http://www.georss.org/georss}where'
    assert etree.QName(result[0].tag).localname == 'Polygon'

    result = encode_georss({
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
    assert result.tag == '{http://www.georss.org/georss}where'
    assert etree.QName(result[0].tag).localname == 'Polygon'

    result = encode_georss({
        'type': 'Polygon',
        'coordinates': [
            [
                (0.5, 1.0),
                (0.5, 2.0),
                (1.5, 2.0),
                (1.5, 1.0),
                (0.5, 1.0)
            ]
        ],
        'crs': {
            'type': 'name',
            'properties': {
                'name': 'EPSG:3857'
            }
        }
    })
    assert result.tag == '{http://www.georss.org/georss}where'
    assert etree.QName(result[0].tag).localname == 'Polygon'


def test_encode_multi_polygon():
    result = encode_georss({
        'type': 'MultiPolygon',
        'coordinates': [
            [
                [
                    (1.0, 2.0),
                    (1.0, 3.0),
                    (2.0, 3.0),
                    (2.0, 2.0),
                    (1.0, 2.0),
                ], [
                    (1.4, 2.4),
                    (1.4, 2.6),
                    (1.6, 2.6),
                    (1.6, 2.4),
                    (1.4, 2.4),
                ],
            ], [
                [
                    (11.0, 12.0),
                    (11.0, 13.0),
                    (12.0, 13.0),
                    (12.0, 12.0),
                    (11.0, 12.0),
                ], [
                    (11.4, 12.4),
                    (11.4, 12.6),
                    (11.6, 12.6),
                    (11.6, 12.4),
                    (11.4, 12.4),
                ],
            ],
        ],
    })
    assert result.tag == '{http://www.georss.org/georss}where'
    assert etree.QName(result[0].tag).localname == 'MultiSurface'


def test_encode_geometry_collection():
    result = encode_georss({
        'type': 'GeometryCollection',
        'geometries': [
            {
                'type': 'Point',
                'coordinates': (1.0, 2.0),
            },
            {
                'type': 'Polygon',
                'coordinates': [
                    [
                        (1.0, 2.0),
                        (1.0, 3.0),
                        (2.0, 3.0),
                        (2.0, 2.0),
                        (1.0, 2.0),
                    ], [
                        (1.4, 2.4),
                        (1.4, 2.6),
                        (1.6, 2.6),
                        (1.6, 2.4),
                        (1.4, 2.4),
                    ],
                ],
            },
        ]
    })
    assert result.tag == '{http://www.georss.org/georss}where'
    assert etree.QName(result[0].tag).localname == 'MultiGeometry'

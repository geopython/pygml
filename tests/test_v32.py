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
import pytest

from pygml.v32 import parse_v32


def test_parse_point():
    # basic test
    result = parse_v32(
        etree.fromstring("""
            <gml:Point gml:id="ID" xmlns:gml="http://www.opengis.net/gml/3.2">
                <gml:pos>1.0 1.0</gml:pos>
            </gml:Point>
        """)
    )
    assert result == {'type': 'Point', 'coordinates': (1.0, 1.0)}

    # using gml:coordinates instead
    result = parse_v32(
        etree.fromstring("""
            <gml:Point gml:id="ID" xmlns:gml="http://www.opengis.net/gml/3.2">
                <gml:coordinates>1.0 1.0</gml:coordinates>
            </gml:Point>
        """)
    )
    assert result == {'type': 'Point', 'coordinates': (1.0, 1.0)}

    # axis order swapping with srsName in pos or Point
    result = parse_v32(
        etree.fromstring("""
            <gml:Point gml:id="ID"
                    xmlns:gml="http://www.opengis.net/gml/3.2">
                <gml:pos srsName="EPSG:4326">2.0 1.0</gml:pos>
            </gml:Point>
        """)
    )
    assert result == {
        'type': 'Point',
        'coordinates': (1.0, 2.0),
        'crs': {
            'type': 'name',
            'properties': {
                'name': 'EPSG:4326'
            }
        }
    }

    result = parse_v32(
        etree.fromstring("""
            <gml:Point gml:id="ID"
                    xmlns:gml="http://www.opengis.net/gml/3.2"
                    srsName="EPSG:4326">
                <gml:coordinates>2.0 1.0</gml:coordinates>
            </gml:Point>
        """)
    )
    assert result == {
        'type': 'Point',
        'coordinates': (1.0, 2.0),
        'crs': {
            'type': 'name',
            'properties': {
                'name': 'EPSG:4326'
            }
        }
    }

    # conflicting srsName
    with pytest.raises(ValueError):
        parse_v32(
            etree.fromstring("""
                <gml:Point gml:id="ID"
                        xmlns:gml="http://www.opengis.net/gml/3.2"
                        srsName="EPSG:3875">
                    <gml:pos srsName="EPSG:4326">2.0 1.0</gml:pos>
                </gml:Point>
            """)
        )


def test_parse_multi_point():
    # using gml:pointMember
    result = parse_v32(
        etree.fromstring("""
            <gml:MultiPoint gml:id="ID"
                    xmlns:gml="http://www.opengis.net/gml/3.2">
                <gml:pointMember>
                    <gml:Point gml:id="ID">
                        <gml:pos>1.0 1.0</gml:pos>
                    </gml:Point>
                </gml:pointMember>
                <gml:pointMember>
                    <gml:Point gml:id="ID">
                        <gml:pos>2.0 2.0</gml:pos>
                    </gml:Point>
                </gml:pointMember>
            </gml:MultiPoint>
        """)
    )
    assert result == {
        'type': 'MultiPoint',
        'coordinates': [
            (1.0, 1.0),
            (2.0, 2.0),
        ]
    }

    # using gml:pointMembers
    result = parse_v32(
        etree.fromstring("""
            <gml:MultiPoint gml:id="ID"
                    xmlns:gml="http://www.opengis.net/gml/3.2">
                <gml:pointMembers>
                    <gml:Point gml:id="ID">
                        <gml:pos>1.0 1.0</gml:pos>
                    </gml:Point>
                    <gml:Point gml:id="ID">
                        <gml:pos>2.0 2.0</gml:pos>
                    </gml:Point>
                </gml:pointMembers>
            </gml:MultiPoint>
        """)
    )
    assert result == {
        'type': 'MultiPoint',
        'coordinates': [
            (1.0, 1.0),
            (2.0, 2.0),
        ]
    }

    # using gml:pointMember and gml:pointMembers
    result = parse_v32(
        etree.fromstring("""
            <gml:MultiPoint gml:id="ID"
                    xmlns:gml="http://www.opengis.net/gml/3.2">
                <gml:pointMembers>
                    <gml:Point gml:id="ID">
                        <gml:pos>1.0 1.0</gml:pos>
                    </gml:Point>
                    <gml:Point gml:id="ID">
                        <gml:pos>2.0 2.0</gml:pos>
                    </gml:Point>
                </gml:pointMembers>
                <gml:pointMember>
                    <gml:Point gml:id="ID">
                        <gml:pos>3.0 3.0</gml:pos>
                    </gml:Point>
                </gml:pointMember>
            </gml:MultiPoint>
        """)
    )
    assert result == {
        'type': 'MultiPoint',
        'coordinates': [
            (1.0, 1.0),
            (2.0, 2.0),
            (3.0, 3.0),
        ]
    }

    # conflicting srsName
    with pytest.raises(ValueError):
        parse_v32(
            etree.fromstring("""
                <gml:MultiPoint gml:id="ID"
                        xmlns:gml="http://www.opengis.net/gml/3.2"
                        srsName="EPSG:4326">
                    <gml:pointMembers>
                        <gml:Point gml:id="ID" srsName="EPSG:3857">
                            <gml:pos>1.0 1.0</gml:pos>
                        </gml:Point>
                        <gml:Point gml:id="ID">
                            <gml:pos>2.0 2.0</gml:pos>
                        </gml:Point>
                    </gml:pointMembers>
                </gml:MultiPoint>
            """)
        )


def test_parse_linestring():
    # from gml:posList
    result = parse_v32(
        etree.fromstring("""
            <gml:LineString xmlns:gml="http://www.opengis.net/gml/3.2">
                <gml:posList>1.0 1.0 2.0 2.0</gml:posList>
            </gml:LineString>
        """)
    )
    assert result == {
        'type': 'LineString',
        'coordinates': [
            (1.0, 1.0),
            (2.0, 2.0),
        ]
    }

    # from gml:pos elements
    result = parse_v32(
        etree.fromstring("""
            <gml:LineString xmlns:gml="http://www.opengis.net/gml/3.2">
                <gml:pos>1.0 1.0</gml:pos>
                <gml:pos>2.0 2.0</gml:pos>
            </gml:LineString>
        """)
    )
    assert result == {
        'type': 'LineString',
        'coordinates': [
            (1.0, 1.0),
            (2.0, 2.0),
        ]
    }

    # from gml:coordinates
    result = parse_v32(
        etree.fromstring("""
            <gml:LineString xmlns:gml="http://www.opengis.net/gml/3.2">
                <gml:coordinates>1.0 1.0,2.0 2.0</gml:coordinates>
            </gml:LineString>
        """)
    )
    assert result == {
        'type': 'LineString',
        'coordinates': [
            (1.0, 1.0),
            (2.0, 2.0),
        ]
    }

    # from gml:pos elements with srsName
    result = parse_v32(
        etree.fromstring("""
            <gml:LineString xmlns:gml="http://www.opengis.net/gml/3.2">
                <gml:pos srsName="EPSG:4326">1.0 1.0</gml:pos>
                <gml:pos>2.0 2.0</gml:pos>
            </gml:LineString>
        """)
    )
    assert result == {
        'type': 'LineString',
        'coordinates': [
            (1.0, 1.0),
            (2.0, 2.0),
        ],
        'crs': {
            'type': 'name',
            'properties': {
                'name': 'EPSG:4326'
            }
        }
    }

    # from gml:posList element with srsName
    result = parse_v32(
        etree.fromstring("""
            <gml:LineString xmlns:gml="http://www.opengis.net/gml/3.2">
                <gml:posList srsName="EPSG:4326">1.0 1.0 2.0 2.0</gml:posList>
            </gml:LineString>
        """)
    )
    assert result == {
        'type': 'LineString',
        'coordinates': [
            (1.0, 1.0),
            (2.0, 2.0),
        ],
        'crs': {
            'type': 'name',
            'properties': {
                'name': 'EPSG:4326'
            }
        }
    }

    # from gml:coordinates element with srsName
    result = parse_v32(
        etree.fromstring("""
            <gml:LineString xmlns:gml="http://www.opengis.net/gml/3.2"
                    srsName="EPSG:4326">
                <gml:coordinates>1.0 1.0,2.0 2.0</gml:coordinates>
            </gml:LineString>
        """)
    )
    assert result == {
        'type': 'LineString',
        'coordinates': [
            (1.0, 1.0),
            (2.0, 2.0),
        ],
        'crs': {
            'type': 'name',
            'properties': {
                'name': 'EPSG:4326'
            }
        }
    }

    # srsName conflict
    with pytest.raises(ValueError):
        parse_v32(
            etree.fromstring("""
                <gml:LineString xmlns:gml="http://www.opengis.net/gml/3.2"
                        srsName="EPSG:4326">
                    <gml:posList srsName="EPSG:3857">
                        1.0 1.0 2.0 2.0
                    </gml:posList>
                </gml:LineString>
            """)
        )


def test_parse_multi_curve():
    pass


def test_parse_polygon():
    # using gml:posList
    result = parse_v32(
        etree.fromstring("""
        <gml:Polygon xmlns:gml="http://www.opengis.net/gml/3.2">
            <gml:exterior>
                <gml:LinearRing>
                    <gml:posList>0.0 0.0 1.0 0.0 0.0 1.0 0.0 0.0</gml:posList>
                </gml:LinearRing>
            </gml:exterior>
            <gml:interior>
                <gml:LinearRing>
                    <gml:posList>0.2 0.2 0.5 0.2 0.2 0.5 0.2 0.2</gml:posList>
                </gml:LinearRing>
            </gml:interior>
        </gml:Polygon>
        """)
    )
    assert result == {
        'type': 'Polygon',
        'coordinates': [
            [
                (0.0, 0.0), (1.0, 0.0), (0.0, 1.0), (0.0, 0.0)
            ],
            [
                (0.2, 0.2), (0.5, 0.2), (0.2, 0.5), (0.2, 0.2)
            ],
        ]
    }

    # using gml:pos elements
    result = parse_v32(
        etree.fromstring("""
        <gml:Polygon xmlns:gml="http://www.opengis.net/gml/3.2">
            <gml:exterior>
                <gml:LinearRing>
                    <gml:pos>0.0 0.0</gml:pos>
                    <gml:pos>1.0 0.0</gml:pos>
                    <gml:pos>0.0 1.0</gml:pos>
                    <gml:pos>0.0 0.0</gml:pos>
                </gml:LinearRing>
            </gml:exterior>
            <gml:interior>
                <gml:LinearRing>
                    <gml:pos>0.2 0.2</gml:pos>
                    <gml:pos>0.5 0.2</gml:pos>
                    <gml:pos>0.2 0.5</gml:pos>
                    <gml:pos>0.2 0.2</gml:pos>
                </gml:LinearRing>
            </gml:interior>
        </gml:Polygon>
        """)
    )
    assert result == {
        'type': 'Polygon',
        'coordinates': [
            [
                (0.0, 0.0), (1.0, 0.0), (0.0, 1.0), (0.0, 0.0)
            ],
            [
                (0.2, 0.2), (0.5, 0.2), (0.2, 0.5), (0.2, 0.2)
            ],
        ]
    }

    # using gml:coordinates
    result = parse_v32(
        etree.fromstring("""
        <gml:Polygon xmlns:gml="http://www.opengis.net/gml/3.2">
            <gml:exterior>
                <gml:LinearRing>
                    <gml:coordinates>0.0 0.0,1.0 0.0,0.0 1.0,0.0 0.0
                    </gml:coordinates>
                </gml:LinearRing>
            </gml:exterior>
            <gml:interior>
                <gml:LinearRing>
                    <gml:coordinates>0.2 0.2,0.5 0.2,0.2 0.5,0.2 0.2
                    </gml:coordinates>
                </gml:LinearRing>
            </gml:interior>
        </gml:Polygon>
        """)
    )
    assert result == {
        'type': 'Polygon',
        'coordinates': [
            [
                (0.0, 0.0), (1.0, 0.0), (0.0, 1.0), (0.0, 0.0)
            ],
            [
                (0.2, 0.2), (0.5, 0.2), (0.2, 0.5), (0.2, 0.2)
            ],
        ]
    }

    # using gml:posList with srsName
    result = parse_v32(
        etree.fromstring("""
        <gml:Polygon xmlns:gml="http://www.opengis.net/gml/3.2">
            <gml:exterior>
                <gml:LinearRing>
                    <gml:posList
                        srsName="EPSG:4326">0.0 0.0 1.0 0.0 0.0 1.0 0.0 0.0
                    </gml:posList>
                </gml:LinearRing>
            </gml:exterior>
            <gml:interior>
                <gml:LinearRing>
                    <gml:posList
                        srsName="EPSG:4326">0.2 0.2 0.5 0.2 0.2 0.5 0.2 0.2
                    </gml:posList>
                </gml:LinearRing>
            </gml:interior>
        </gml:Polygon>
        """)
    )
    assert result == {
        'type': 'Polygon',
        'coordinates': [
            [
                (0.0, 0.0), (0.0, 1.0), (1.0, 0.0), (0.0, 0.0)
            ],
            [
                (0.2, 0.2), (0.2, 0.5), (0.5, 0.2), (0.2, 0.2)
            ],
        ],
        'crs': {
            'type': 'name',
            'properties': {
                'name': 'EPSG:4326'
            }
        }
    }


def test_parse_multi_polygon():
    pass


def test_parse_multi_geometry():
    # using geometryMembers
    result = parse_v32(
        etree.fromstring("""
        <gml:MultiGeometry gml:id="ID"
                xmlns:gml="http://www.opengis.net/gml/3.2">
            <gml:geometryMembers>
                <gml:Point gml:id="ID">
                    <gml:pos>1.0 1.0</gml:pos>
                </gml:Point>
                <gml:Polygon xmlns:gml="http://www.opengis.net/gml/3.2">
                    <gml:exterior>
                        <gml:LinearRing>
                            <gml:posList>1.0 1.0</gml:posList>
                        </gml:LinearRing>
                    </gml:exterior>
                    <gml:interior>
                        <gml:LinearRing>
                            <gml:posList>1.0 1.0</gml:posList>
                        </gml:LinearRing>
                    </gml:interior>
                </gml:Polygon>
            </gml:geometryMembers>
        </gml:MultiGeometry>
        """)
    )

    assert result == {
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
    }

    # using geometryMember
    result = parse_v32(
        etree.fromstring("""
        <gml:MultiGeometry gml:id="ID"
                xmlns:gml="http://www.opengis.net/gml/3.2">
            <gml:geometryMember>
                <gml:Point gml:id="ID">
                    <gml:pos>1.0 1.0</gml:pos>
                </gml:Point>
            </gml:geometryMember>
            <gml:geometryMember>
                <gml:Polygon xmlns:gml="http://www.opengis.net/gml/3.2">
                    <gml:exterior>
                        <gml:LinearRing>
                            <gml:posList>1.0 1.0</gml:posList>
                        </gml:LinearRing>
                    </gml:exterior>
                    <gml:interior>
                        <gml:LinearRing>
                            <gml:posList>1.0 1.0</gml:posList>
                        </gml:LinearRing>
                    </gml:interior>
                </gml:Polygon>
            </gml:geometryMember>
        </gml:MultiGeometry>
        """)
    )

    assert result == {
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
    }

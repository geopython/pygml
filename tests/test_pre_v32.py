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

from pygml.pre_v32 import encode_pre_v32, parse_pre_v32

from .util import compare_trees


def test_parse_point():
    # basic test
    result = parse_pre_v32(
        etree.fromstring("""
            <gml:Point gml:id="ID" xmlns:gml="http://www.opengis.net/gml">
                <gml:pos>1.0 1.0</gml:pos>
            </gml:Point>
        """)
    )
    assert result == {'type': 'Point', 'coordinates': (1.0, 1.0)}

    # using gml:coordinates instead
    result = parse_pre_v32(
        etree.fromstring("""
            <gml:Point gml:id="ID" xmlns:gml="http://www.opengis.net/gml">
                <gml:coordinates>1.0 1.0</gml:coordinates>
            </gml:Point>
        """)
    )
    assert result == {'type': 'Point', 'coordinates': (1.0, 1.0)}

    # axis order swapping with srsName in pos or Point
    result = parse_pre_v32(
        etree.fromstring("""
            <gml:Point gml:id="ID"
                    xmlns:gml="http://www.opengis.net/gml">
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

    result = parse_pre_v32(
        etree.fromstring("""
            <gml:Point gml:id="ID"
                    xmlns:gml="http://www.opengis.net/gml"
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
        parse_pre_v32(
            etree.fromstring("""
                <gml:Point gml:id="ID"
                        xmlns:gml="http://www.opengis.net/gml"
                        srsName="EPSG:3875">
                    <gml:pos srsName="EPSG:4326">2.0 1.0</gml:pos>
                </gml:Point>
            """)
        )


def test_parse_multi_point():
    # using gml:pointMember
    result = parse_pre_v32(
        etree.fromstring("""
            <gml:MultiPoint gml:id="ID"
                    xmlns:gml="http://www.opengis.net/gml">
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
    result = parse_pre_v32(
        etree.fromstring("""
            <gml:MultiPoint gml:id="ID"
                    xmlns:gml="http://www.opengis.net/gml">
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
    result = parse_pre_v32(
        etree.fromstring("""
            <gml:MultiPoint gml:id="ID"
                    xmlns:gml="http://www.opengis.net/gml">
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
        parse_pre_v32(
            etree.fromstring("""
                <gml:MultiPoint gml:id="ID"
                        xmlns:gml="http://www.opengis.net/gml"
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
    result = parse_pre_v32(
        etree.fromstring("""
            <gml:LineString xmlns:gml="http://www.opengis.net/gml">
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
    result = parse_pre_v32(
        etree.fromstring("""
            <gml:LineString xmlns:gml="http://www.opengis.net/gml">
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
    result = parse_pre_v32(
        etree.fromstring("""
            <gml:LineString xmlns:gml="http://www.opengis.net/gml">
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
    result = parse_pre_v32(
        etree.fromstring("""
            <gml:LineString xmlns:gml="http://www.opengis.net/gml">
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
    result = parse_pre_v32(
        etree.fromstring("""
            <gml:LineString xmlns:gml="http://www.opengis.net/gml">
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
    result = parse_pre_v32(
        etree.fromstring("""
            <gml:LineString xmlns:gml="http://www.opengis.net/gml"
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
        parse_pre_v32(
            etree.fromstring("""
                <gml:LineString xmlns:gml="http://www.opengis.net/gml"
                        srsName="EPSG:4326">
                    <gml:posList srsName="EPSG:3857">
                        1.0 1.0 2.0 2.0
                    </gml:posList>
                </gml:LineString>
            """)
        )


def test_parse_multi_curve():
    # using gml:curveMember elements
    result = parse_pre_v32(
        etree.fromstring("""
            <gml:MultiCurve xmlns:gml="http://www.opengis.net/gml">
                <gml:curveMember>
                    <gml:LineString>
                        <gml:posList>1.0 1.0 2.0 2.0</gml:posList>
                    </gml:LineString>
                </gml:curveMember>
                <gml:curveMember>
                    <gml:LineString>
                        <gml:posList>3.0 3.0 4.0 4.0</gml:posList>
                    </gml:LineString>
                </gml:curveMember>
            </gml:MultiCurve>
        """)
    )
    assert result == {
        'type': 'MultiLineString',
        'coordinates': [
            [(1.0, 1.0), (2.0, 2.0)],
            [(3.0, 3.0), (4.0, 4.0)],
        ]
    }

    # using gml:curveMembers element
    result = parse_pre_v32(
        etree.fromstring("""
            <gml:MultiCurve xmlns:gml="http://www.opengis.net/gml">
                <gml:curveMembers>
                    <gml:LineString>
                        <gml:posList>1.0 1.0 2.0 2.0</gml:posList>
                    </gml:LineString>
                    <gml:LineString>
                        <gml:posList>3.0 3.0 4.0 4.0</gml:posList>
                    </gml:LineString>
                </gml:curveMembers>
            </gml:MultiCurve>
        """)
    )
    assert result == {
        'type': 'MultiLineString',
        'coordinates': [
            [(1.0, 1.0), (2.0, 2.0)],
            [(3.0, 3.0), (4.0, 4.0)],
        ]
    }

    # determine srsName from MultiCurve
    result = parse_pre_v32(
        etree.fromstring("""
            <gml:MultiCurve xmlns:gml="http://www.opengis.net/gml"
                    srsName="EPSG:4326">
                <gml:curveMember>
                    <gml:LineString>
                        <gml:posList>1.0 1.0 2.0 2.0</gml:posList>
                    </gml:LineString>
                </gml:curveMember>
                <gml:curveMember>
                    <gml:LineString>
                        <gml:posList>3.0 3.0 4.0 4.0</gml:posList>
                    </gml:LineString>
                </gml:curveMember>
            </gml:MultiCurve>
        """)
    )
    assert result == {
        'type': 'MultiLineString',
        'coordinates': [
            [(1.0, 1.0), (2.0, 2.0)],
            [(3.0, 3.0), (4.0, 4.0)],
        ],
        'crs': {
            'type': 'name',
            'properties': {
                'name': 'EPSG:4326'
            }
        }
    }

    # determine srsName from first LineString
    result = parse_pre_v32(
        etree.fromstring("""
            <gml:MultiCurve xmlns:gml="http://www.opengis.net/gml">
                <gml:curveMember>
                    <gml:LineString srsName="EPSG:4326">
                        <gml:posList>1.0 1.0 2.0 2.0</gml:posList>
                    </gml:LineString>
                </gml:curveMember>
                <gml:curveMember>
                    <gml:LineString>
                        <gml:posList>3.0 3.0 4.0 4.0</gml:posList>
                    </gml:LineString>
                </gml:curveMember>
            </gml:MultiCurve>
        """)
    )
    assert result == {
        'type': 'MultiLineString',
        'coordinates': [
            [(1.0, 1.0), (2.0, 2.0)],
            [(3.0, 3.0), (4.0, 4.0)],
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
        parse_pre_v32(
            etree.fromstring("""
                <gml:MultiCurve xmlns:gml="http://www.opengis.net/gml">
                    <gml:curveMember>
                        <gml:LineString srsName="EPSG:4326">
                            <gml:posList>1.0 1.0 2.0 2.0</gml:posList>
                        </gml:LineString>
                    </gml:curveMember>
                    <gml:curveMember>
                        <gml:LineString srsName="EPSG:3857">
                            <gml:posList>3.0 3.0 4.0 4.0</gml:posList>
                        </gml:LineString>
                    </gml:curveMember>
                </gml:MultiCurve>
            """)
        )

    with pytest.raises(ValueError):
        parse_pre_v32(
            etree.fromstring("""
                <gml:MultiCurve xmlns:gml="http://www.opengis.net/gml"
                        srsName="EPSG:3857">
                    <gml:curveMember>
                        <gml:LineString srsName="EPSG:4326">
                            <gml:posList>1.0 1.0 2.0 2.0</gml:posList>
                        </gml:LineString>
                    </gml:curveMember>
                    <gml:curveMember>
                        <gml:LineString>
                            <gml:posList>3.0 3.0 4.0 4.0</gml:posList>
                        </gml:LineString>
                    </gml:curveMember>
                </gml:MultiCurve>
            """)
        )


def test_parse_polygon():
    # using gml:posList
    result = parse_pre_v32(
        etree.fromstring("""
        <gml:Polygon xmlns:gml="http://www.opengis.net/gml">
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
    result = parse_pre_v32(
        etree.fromstring("""
        <gml:Polygon xmlns:gml="http://www.opengis.net/gml">
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
    result = parse_pre_v32(
        etree.fromstring("""
        <gml:Polygon xmlns:gml="http://www.opengis.net/gml">
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
    result = parse_pre_v32(
        etree.fromstring("""
        <gml:Polygon xmlns:gml="http://www.opengis.net/gml">
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


def test_parse_envelope():
    # using gml:lowerCorner/gml:upperCorner
    result = parse_pre_v32(
        etree.fromstring("""
        <gml:Envelope xmlns:gml="http://www.opengis.net/gml">
            <gml:lowerCorner>0.0 1.0</gml:lowerCorner>
            <gml:upperCorner>2.0 3.0</gml:upperCorner>
        </gml:Envelope>
        """)
    )
    assert result == {
        'type': 'Polygon',
        'coordinates': [
            [
                (0.0, 1.0),
                (0.0, 3.0),
                (2.0, 3.0),
                (2.0, 1.0),
                (0.0, 1.0),
            ],
        ]
    }

    # using gml:pos elements
    result = parse_pre_v32(
        etree.fromstring("""
        <gml:Envelope xmlns:gml="http://www.opengis.net/gml">
            <gml:pos>0.0 1.0</gml:pos>
            <gml:pos>2.0 3.0</gml:pos>
        </gml:Envelope>
        """)
    )
    assert result == {
        'type': 'Polygon',
        'coordinates': [
            [
                (0.0, 1.0),
                (0.0, 3.0),
                (2.0, 3.0),
                (2.0, 1.0),
                (0.0, 1.0),
            ],
        ]
    }

    # using gml:coordinates
    result = parse_pre_v32(
        etree.fromstring("""
        <gml:Envelope xmlns:gml="http://www.opengis.net/gml">
            <gml:coordinates>0.0 1.0,2.0 3.0</gml:coordinates>
        </gml:Envelope>
        """)
    )
    assert result == {
        'type': 'Polygon',
        'coordinates': [
            [
                (0.0, 1.0),
                (0.0, 3.0),
                (2.0, 3.0),
                (2.0, 1.0),
                (0.0, 1.0),
            ],
        ]
    }

    # using gml:lowerCorner/gml:upperCorner with srsName
    result = parse_pre_v32(
        etree.fromstring("""
        <gml:Envelope xmlns:gml="http://www.opengis.net/gml">
            <gml:lowerCorner srsName="EPSG:4326">0.0 1.0</gml:lowerCorner>
            <gml:upperCorner srsName="EPSG:4326">2.0 3.0</gml:upperCorner>
        </gml:Envelope>
        """)
    )
    assert result == {
        'type': 'Polygon',
        'coordinates': [
            [
                (1.0, 0.0),
                (3.0, 0.0),
                (3.0, 2.0),
                (1.0, 2.0),
                (1.0, 0.0),
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
    # using gml:surfaceMember elements
    result = parse_pre_v32(
        etree.fromstring("""
        <gml:MultiSurface xmlns:gml="http://www.opengis.net/gml">
            <gml:surfaceMember>
                <gml:Polygon>
                    <gml:exterior>
                        <gml:LinearRing>
                            <gml:posList>0.0 0.0 1.0 0.0 0.0 1.0 0.0 0.0
                            </gml:posList>
                        </gml:LinearRing>
                    </gml:exterior>
                    <gml:interior>
                        <gml:LinearRing>
                            <gml:posList>0.2 0.2 0.5 0.2 0.2 0.5 0.2 0.2
                            </gml:posList>
                        </gml:LinearRing>
                    </gml:interior>
                </gml:Polygon>
            </gml:surfaceMember>
            <gml:surfaceMember>
                <gml:Polygon>
                    <gml:exterior>
                        <gml:LinearRing>
                            <gml:posList>
                                10.0 10.0 11.0 10.0 10.0 11.0 10.0 10.0
                            </gml:posList>
                        </gml:LinearRing>
                    </gml:exterior>
                    <gml:interior>
                        <gml:LinearRing>
                            <gml:posList>
                                10.2 10.2 10.5 10.2 10.2 10.5 10.2 10.2
                            </gml:posList>
                        </gml:LinearRing>
                    </gml:interior>
                </gml:Polygon>
            </gml:surfaceMember>
        </gml:MultiSurface>
        """)
    )
    assert result == {
        'type': 'MultiPolygon',
        'coordinates': [
            [
                [
                    (0.0, 0.0), (1.0, 0.0), (0.0, 1.0), (0.0, 0.0)
                ],
                [
                    (0.2, 0.2), (0.5, 0.2), (0.2, 0.5), (0.2, 0.2)
                ],
            ],
            [
                [
                    (10.0, 10.0), (11.0, 10.0), (10.0, 11.0), (10.0, 10.0)
                ],
                [
                    (10.2, 10.2), (10.5, 10.2), (10.2, 10.5), (10.2, 10.2)
                ],
            ]
        ]
    }

    # using gml:surfaceMembers
    result = parse_pre_v32(
        etree.fromstring("""
        <gml:MultiSurface xmlns:gml="http://www.opengis.net/gml">
            <gml:surfaceMembers>
                <gml:Polygon>
                    <gml:exterior>
                        <gml:LinearRing>
                            <gml:posList>0.0 0.0 1.0 0.0 0.0 1.0 0.0 0.0
                            </gml:posList>
                        </gml:LinearRing>
                    </gml:exterior>
                    <gml:interior>
                        <gml:LinearRing>
                            <gml:posList>0.2 0.2 0.5 0.2 0.2 0.5 0.2 0.2
                            </gml:posList>
                        </gml:LinearRing>
                    </gml:interior>
                </gml:Polygon>
                <gml:Polygon>
                    <gml:exterior>
                        <gml:LinearRing>
                            <gml:posList>
                                10.0 10.0 11.0 10.0 10.0 11.0 10.0 10.0
                            </gml:posList>
                        </gml:LinearRing>
                    </gml:exterior>
                    <gml:interior>
                        <gml:LinearRing>
                            <gml:posList>
                                10.2 10.2 10.5 10.2 10.2 10.5 10.2 10.2
                            </gml:posList>
                        </gml:LinearRing>
                    </gml:interior>
                </gml:Polygon>
            </gml:surfaceMembers>
        </gml:MultiSurface>
        """)
    )
    assert result == {
        'type': 'MultiPolygon',
        'coordinates': [
            [
                [
                    (0.0, 0.0), (1.0, 0.0), (0.0, 1.0), (0.0, 0.0)
                ],
                [
                    (0.2, 0.2), (0.5, 0.2), (0.2, 0.5), (0.2, 0.2)
                ],
            ],
            [
                [
                    (10.0, 10.0), (11.0, 10.0), (10.0, 11.0), (10.0, 10.0)
                ],
                [
                    (10.2, 10.2), (10.5, 10.2), (10.2, 10.5), (10.2, 10.2)
                ],
            ]
        ]
    }

    # using gml:surfaceMembers with srsName
    result = parse_pre_v32(
        etree.fromstring("""
        <gml:MultiSurface xmlns:gml="http://www.opengis.net/gml">
            <gml:surfaceMembers>
                <gml:Polygon srsName="EPSG:4326">
                    <gml:exterior>
                        <gml:LinearRing>
                            <gml:posList>0.0 0.0 1.0 0.0 0.0 1.0 0.0 0.0
                            </gml:posList>
                        </gml:LinearRing>
                    </gml:exterior>
                    <gml:interior>
                        <gml:LinearRing>
                            <gml:posList>0.2 0.2 0.5 0.2 0.2 0.5 0.2 0.2
                            </gml:posList>
                        </gml:LinearRing>
                    </gml:interior>
                </gml:Polygon>
                <gml:Polygon>
                    <gml:exterior>
                        <gml:LinearRing>
                            <gml:posList>
                                10.0 10.0 11.0 10.0 10.0 11.0 10.0 10.0
                            </gml:posList>
                        </gml:LinearRing>
                    </gml:exterior>
                    <gml:interior>
                        <gml:LinearRing>
                            <gml:posList>
                                10.2 10.2 10.5 10.2 10.2 10.5 10.2 10.2
                            </gml:posList>
                        </gml:LinearRing>
                    </gml:interior>
                </gml:Polygon>
            </gml:surfaceMembers>
        </gml:MultiSurface>
        """)
    )
    assert result == {
        'type': 'MultiPolygon',
        'coordinates': [
            [
                [
                    (0.0, 0.0), (0.0, 1.0), (1.0, 0.0), (0.0, 0.0)
                ],
                [
                    (0.2, 0.2), (0.2, 0.5), (0.5, 0.2), (0.2, 0.2)
                ],
            ],
            [
                [
                    (10.0, 10.0), (10.0, 11.0), (11.0, 10.0), (10.0, 10.0)
                ],
                [
                    (10.2, 10.2), (10.2, 10.5), (10.5, 10.2), (10.2, 10.2)
                ],
            ]
        ],
        'crs': {
            'type': 'name',
            'properties': {
                'name': 'EPSG:4326'
            }
        }
    }

    with pytest.raises(ValueError):
        parse_pre_v32(
            etree.fromstring("""
            <gml:MultiSurface xmlns:gml="http://www.opengis.net/gml">
                <gml:surfaceMembers>
                    <gml:Polygon srsName="EPSG:4326">
                        <gml:exterior>
                            <gml:LinearRing>
                                <gml:posList>0.0 0.0 1.0 0.0 0.0 1.0 0.0 0.0
                                </gml:posList>
                            </gml:LinearRing>
                        </gml:exterior>
                        <gml:interior>
                            <gml:LinearRing>
                                <gml:posList>0.2 0.2 0.5 0.2 0.2 0.5 0.2 0.2
                                </gml:posList>
                            </gml:LinearRing>
                        </gml:interior>
                    </gml:Polygon>
                    <gml:Polygon>
                        <gml:exterior>
                            <gml:LinearRing>
                                <gml:posList srsName="EPSG:3857">
                                    10.0 10.0 11.0 10.0 10.0 11.0 10.0 10.0
                                </gml:posList>
                            </gml:LinearRing>
                        </gml:exterior>
                        <gml:interior>
                            <gml:LinearRing>
                                <gml:posList>
                                    10.2 10.2 10.5 10.2 10.2 10.5 10.2 10.2
                                </gml:posList>
                            </gml:LinearRing>
                        </gml:interior>
                    </gml:Polygon>
                </gml:surfaceMembers>
            </gml:MultiSurface>
            """)
        )


def test_parse_multi_geometry():
    # using geometryMembers
    result = parse_pre_v32(
        etree.fromstring("""
        <gml:MultiGeometry gml:id="ID"
                xmlns:gml="http://www.opengis.net/gml">
            <gml:geometryMembers>
                <gml:Point gml:id="ID">
                    <gml:pos>1.0 1.0</gml:pos>
                </gml:Point>
                <gml:Polygon xmlns:gml="http://www.opengis.net/gml">
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
    result = parse_pre_v32(
        etree.fromstring("""
        <gml:MultiGeometry gml:id="ID"
                xmlns:gml="http://www.opengis.net/gml">
            <gml:geometryMember>
                <gml:Point gml:id="ID">
                    <gml:pos>1.0 1.0</gml:pos>
                </gml:Point>
            </gml:geometryMember>
            <gml:geometryMember>
                <gml:Polygon xmlns:gml="http://www.opengis.net/gml">
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

    # allow varying srsNames
    result = parse_pre_v32(
        etree.fromstring("""
        <gml:MultiGeometry gml:id="ID"
                xmlns:gml="http://www.opengis.net/gml">
            <gml:geometryMembers>
                <gml:Point srsName="EPSG:4326" gml:id="ID">
                    <gml:pos>1.0 1.0</gml:pos>
                </gml:Point>
                <gml:Polygon srsName="EPSG:3857"
                        xmlns:gml="http://www.opengis.net/gml">
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
                'coordinates': (1.0, 1.0),
                'crs': {
                    'type': 'name',
                    'properties': {
                        'name': 'EPSG:4326'
                    }
                }
            },
            {
                'type': 'Polygon',
                'coordinates': [
                    [(1.0, 1.0)],
                    [(1.0, 1.0)],
                ],
                'crs': {
                    'type': 'name',
                    'properties': {
                        'name': 'EPSG:3857'
                    }
                }
            },
        ]
    }


def test_encode_pre_v32_point():
    # encode Point
    result = encode_pre_v32({'type': 'Point', 'coordinates': (1.0, 2.0)}, 'ID')
    expected = etree.fromstring("""
        <gml:Point gml:id="ID" xmlns:gml="http://www.opengis.net/gml"
                srsName="urn:ogc:def:crs:OGC::CRS84">
            <gml:pos>1.0 2.0</gml:pos>
        </gml:Point>
    """)
    assert compare_trees(
        expected, result
    ), f'{etree.tostring(expected)} != {etree.tostring(result)}'

    # encode Point with EPSG:4326
    result = encode_pre_v32({
        'type': 'Point',
        'coordinates': (1.0, 2.0),
        'crs': {
            'type': 'name',
            'properties': {
                'name': 'EPSG:4326'
            }
        }
    }, 'ID')
    expected = etree.fromstring("""
        <gml:Point gml:id="ID" xmlns:gml="http://www.opengis.net/gml"
                srsName="EPSG:4326">
            <gml:pos>2.0 1.0</gml:pos>
        </gml:Point>
    """)
    assert compare_trees(
        expected, result
    ), f'{etree.tostring(expected)} != {etree.tostring(result)}'


def test_encode_pre_v32_multi_point():
    # encode MultiPoint
    result = encode_pre_v32({
        'type': 'MultiPoint',
        'coordinates': [
            (1.0, 2.0),
            (3.0, 4.0),
        ]
    }, 'ID')
    expected = etree.fromstring("""
        <gml:MultiPoint gml:id="ID" xmlns:gml="http://www.opengis.net/gml"
                srsName="urn:ogc:def:crs:OGC::CRS84">
            <gml:geometryMembers>
                <gml:Point gml:id="ID_0">
                    <gml:pos>1.0 2.0</gml:pos>
                </gml:Point>
                <gml:Point gml:id="ID_1">
                    <gml:pos>3.0 4.0</gml:pos>
                </gml:Point>
            </gml:geometryMembers>
        </gml:MultiPoint>
    """)
    assert compare_trees(
        expected, result
    ), f'{etree.tostring(expected)} != {etree.tostring(result)}'

    # encode MultiPoint with EPSG:4326
    result = encode_pre_v32({
        'type': 'MultiPoint',
        'coordinates': [
            (1.0, 2.0),
            (3.0, 4.0),
        ],
        'crs': {
            'type': 'name',
            'properties': {
                'name': 'EPSG:4326'
            }
        }
    }, 'ID')
    expected = etree.fromstring("""
        <gml:MultiPoint gml:id="ID" xmlns:gml="http://www.opengis.net/gml"
                srsName="EPSG:4326">
            <gml:geometryMembers>
                <gml:Point gml:id="ID_0">
                    <gml:pos>2.0 1.0</gml:pos>
                </gml:Point>
                <gml:Point gml:id="ID_1">
                    <gml:pos>4.0 3.0</gml:pos>
                </gml:Point>
            </gml:geometryMembers>
        </gml:MultiPoint>
    """)
    assert compare_trees(
        expected, result
    ), f'{etree.tostring(expected)} != {etree.tostring(result)}'


def test_encode_pre_v32_linestring():
    # encode LineString
    result = encode_pre_v32({
        'type': 'LineString',
        'coordinates': [
            (1.0, 2.0),
            (3.0, 4.0),
        ],
    }, 'ID')
    expected = etree.fromstring("""
        <gml:LineString gml:id="ID" xmlns:gml="http://www.opengis.net/gml"
                srsName="urn:ogc:def:crs:OGC::CRS84">
            <gml:posList>1.0 2.0 3.0 4.0</gml:posList>
        </gml:LineString>
    """)
    assert compare_trees(
        expected, result
    ), f'{etree.tostring(expected)} != {etree.tostring(result)}'

    # encode LineString with EPSG:4326
    result = encode_pre_v32({
        'type': 'LineString',
        'coordinates': [
            (1.0, 2.0),
            (3.0, 4.0),
        ],
        'crs': {
            'type': 'name',
            'properties': {
                'name': 'EPSG:4326'
            }
        }
    }, 'ID')
    expected = etree.fromstring("""
        <gml:LineString gml:id="ID" xmlns:gml="http://www.opengis.net/gml"
                srsName="EPSG:4326">
            <gml:posList>2.0 1.0 4.0 3.0</gml:posList>
        </gml:LineString>
    """)
    assert compare_trees(
        expected, result
    ), f'{etree.tostring(expected)} != {etree.tostring(result)}'


def test_encode_pre_v32_polygon():
    # encode Polygon
    result = encode_pre_v32({
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
    }, 'ID')
    expected = etree.fromstring("""
        <gml:Polygon gml:id="ID" xmlns:gml="http://www.opengis.net/gml"
                srsName="urn:ogc:def:crs:OGC::CRS84">
            <gml:exterior>
                <gml:LinearRing>
                    <gml:posList>
                        1.0 2.0 1.0 3.0 2.0 3.0 2.0 2.0 1.0 2.0
                    </gml:posList>
                </gml:LinearRing>
            </gml:exterior>
            <gml:interior>
                <gml:LinearRing>
                    <gml:posList>
                        1.4 2.4 1.4 2.6 1.6 2.6 1.6 2.4 1.4 2.4
                    </gml:posList>
                </gml:LinearRing>
            </gml:interior>
        </gml:Polygon>
    """)
    assert compare_trees(
        expected, result
    ), f'{etree.tostring(expected)} != {etree.tostring(result)}'

    # encode Polygon with EPSG:4326
    result = encode_pre_v32({
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
        'crs': {
            'type': 'name',
            'properties': {
                'name': 'EPSG:4326'
            }
        }
    }, 'ID')
    expected = etree.fromstring("""
        <gml:Polygon gml:id="ID" xmlns:gml="http://www.opengis.net/gml"
                srsName="EPSG:4326">
            <gml:exterior>
                <gml:LinearRing>
                    <gml:posList>
                        2.0 1.0 3.0 1.0 3.0 2.0 2.0 2.0 2.0 1.0
                    </gml:posList>
                </gml:LinearRing>
            </gml:exterior>
            <gml:interior>
                <gml:LinearRing>
                    <gml:posList>
                        2.4 1.4 2.6 1.4 2.6 1.6 2.4 1.6 2.4 1.4
                    </gml:posList>
                </gml:LinearRing>
            </gml:interior>
        </gml:Polygon>
    """)
    assert compare_trees(
        expected, result
    ), f'{etree.tostring(expected)} != {etree.tostring(result)}'


def test_encode_pre_v32_multi_polygon():
    # encode MultiPolygon
    result = encode_pre_v32({
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
    }, 'ID')
    expected = etree.fromstring("""
        <gml:MultiSurface gml:id="ID"
                xmlns:gml="http://www.opengis.net/gml"
                srsName="urn:ogc:def:crs:OGC::CRS84">
            <gml:surfaceMembers>
                <gml:Polygon gml:id="ID_0">
                    <gml:exterior>
                        <gml:LinearRing>
                            <gml:posList>
                                1.0 2.0 1.0 3.0 2.0 3.0 2.0 2.0 1.0 2.0
                            </gml:posList>
                        </gml:LinearRing>
                    </gml:exterior>
                    <gml:interior>
                        <gml:LinearRing>
                            <gml:posList>
                                1.4 2.4 1.4 2.6 1.6 2.6 1.6 2.4 1.4 2.4
                            </gml:posList>
                        </gml:LinearRing>
                    </gml:interior>
                </gml:Polygon>
                <gml:Polygon gml:id="ID_1">
                    <gml:exterior>
                        <gml:LinearRing>
                            <gml:posList>
                            11.0 12.0 11.0 13.0 12.0 13.0 12.0 12.0 11.0 12.0
                            </gml:posList>
                        </gml:LinearRing>
                    </gml:exterior>
                    <gml:interior>
                        <gml:LinearRing>
                            <gml:posList>
                            11.4 12.4 11.4 12.6 11.6 12.6 11.6 12.4 11.4 12.4
                            </gml:posList>
                        </gml:LinearRing>
                    </gml:interior>
                </gml:Polygon>
            </gml:surfaceMembers>
        </gml:MultiSurface>
    """)
    assert compare_trees(
        expected, result
    ), f'{etree.tostring(expected)} != {etree.tostring(result)}'

    # encode MultiPolygon with EPSG:4326
    result = encode_pre_v32({
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
        'crs': {
            'type': 'name',
            'properties': {
                'name': 'EPSG:4326'
            }
        }
    }, 'ID')
    expected = etree.fromstring("""
        <gml:MultiSurface gml:id="ID"
                xmlns:gml="http://www.opengis.net/gml"
                srsName="EPSG:4326">
            <gml:surfaceMembers>
                <gml:Polygon gml:id="ID_0">
                    <gml:exterior>
                        <gml:LinearRing>
                            <gml:posList>
                                2.0 1.0 3.0 1.0 3.0 2.0 2.0 2.0 2.0 1.0
                            </gml:posList>
                        </gml:LinearRing>
                    </gml:exterior>
                    <gml:interior>
                        <gml:LinearRing>
                            <gml:posList>
                                2.4 1.4 2.6 1.4 2.6 1.6 2.4 1.6 2.4 1.4
                            </gml:posList>
                        </gml:LinearRing>
                    </gml:interior>
                </gml:Polygon>
                <gml:Polygon gml:id="ID_1">
                    <gml:exterior>
                        <gml:LinearRing>
                            <gml:posList>
                            12.0 11.0 13.0 11.0 13.0 12.0 12.0 12.0 12.0 11.0
                            </gml:posList>
                        </gml:LinearRing>
                    </gml:exterior>
                    <gml:interior>
                        <gml:LinearRing>
                            <gml:posList>
                            12.4 11.4 12.6 11.4 12.6 11.6 12.4 11.6 12.4 11.4
                            </gml:posList>
                        </gml:LinearRing>
                    </gml:interior>
                </gml:Polygon>
            </gml:surfaceMembers>
        </gml:MultiSurface>
    """)
    assert compare_trees(
        expected, result
    ), f'{etree.tostring(expected)} != {etree.tostring(result)}'


def test_encode_pre_v32_geometry_collection():
    result = encode_pre_v32({
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
    }, 'ID')
    expected = etree.fromstring("""
        <gml:MultiGeometry gml:id="ID"
                xmlns:gml="http://www.opengis.net/gml">
            <gml:geometryMembers>
                <gml:Point gml:id="ID_0"
                        srsName="urn:ogc:def:crs:OGC::CRS84">
                    <gml:pos>1.0 2.0</gml:pos>
                </gml:Point>
                <gml:Polygon gml:id="ID_1"
                        srsName="urn:ogc:def:crs:OGC::CRS84">
                    <gml:exterior>
                        <gml:LinearRing>
                            <gml:posList>
                                1.0 2.0 1.0 3.0 2.0 3.0 2.0 2.0 1.0 2.0
                            </gml:posList>
                        </gml:LinearRing>
                    </gml:exterior>
                    <gml:interior>
                        <gml:LinearRing>
                            <gml:posList>
                                1.4 2.4 1.4 2.6 1.6 2.6 1.6 2.4 1.4 2.4
                            </gml:posList>
                        </gml:LinearRing>
                    </gml:interior>
                </gml:Polygon>
            </gml:geometryMembers>
        </gml:MultiGeometry>
    """)
    assert compare_trees(
        expected, result
    ), f'{etree.tostring(expected)} != {etree.tostring(result)}'

    result = encode_pre_v32({
        'type': 'GeometryCollection',
        'geometries': [
            {
                'type': 'Point',
                'coordinates': (1.0, 2.0),
                'crs': {
                    'type': 'name',
                    'properties': {
                        'name': 'EPSG:4326'
                    }
                }
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
                'crs': {
                    'type': 'name',
                    'properties': {
                        'name': 'EPSG:4326'
                    }
                }
            },
        ]
    }, 'ID')
    expected = etree.fromstring("""
        <gml:MultiGeometry gml:id="ID"
                xmlns:gml="http://www.opengis.net/gml">
            <gml:geometryMembers>
                <gml:Point gml:id="ID_0"
                        srsName="EPSG:4326">
                    <gml:pos>2.0 1.0</gml:pos>
                </gml:Point>
                <gml:Polygon gml:id="ID_1"
                        srsName="EPSG:4326">
                    <gml:exterior>
                        <gml:LinearRing>
                            <gml:posList>
                                2.0 1.0 3.0 1.0 3.0 2.0 2.0 2.0 2.0 1.0
                            </gml:posList>
                        </gml:LinearRing>
                    </gml:exterior>
                    <gml:interior>
                        <gml:LinearRing>
                            <gml:posList>
                                2.4 1.4 2.6 1.4 2.6 1.6 2.4 1.6 2.4 1.4
                            </gml:posList>
                        </gml:LinearRing>
                    </gml:interior>
                </gml:Polygon>
            </gml:geometryMembers>
        </gml:MultiGeometry>
    """)
    assert compare_trees(
        expected, result
    ), f'{etree.tostring(expected)} != {etree.tostring(result)}'

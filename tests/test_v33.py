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
# import pytest

from pygml.v33 import parse_v33_ce

# from .util import compare_trees


def test_parse_simple_triangle():
    # using gml:pos elements
    result = parse_v33_ce(
        etree.fromstring("""
            <gmlce:SimpleTriangle gml:id="ID"
                    xmlns:gml="http://www.opengis.net/gml/3.2"
                    xmlns:gmlce="http://www.opengis.net/gml/3.3/ce">
                <gml:pos>1.0 1.0</gml:pos>
                <gml:pos>1.0 2.0</gml:pos>
                <gml:pos>2.0 1.0</gml:pos>
            </gmlce:SimpleTriangle>
        """)
    )
    assert result == {
        'type': 'Polygon',
        'coordinates': [
            [
                (1.0, 1.0),
                (1.0, 2.0),
                (2.0, 1.0),
                (1.0, 1.0),
            ]
        ]
    }

    # using gml:posList element
    result = parse_v33_ce(
        etree.fromstring("""
            <gmlce:SimpleTriangle gml:id="ID"
                    xmlns:gml="http://www.opengis.net/gml/3.2"
                    xmlns:gmlce="http://www.opengis.net/gml/3.3/ce">
                <gml:posList>1.0 1.0 1.0 2.0 2.0 1.0</gml:posList>
            </gmlce:SimpleTriangle>
        """)
    )
    assert result == {
        'type': 'Polygon',
        'coordinates': [
            [
                (1.0, 1.0),
                (1.0, 2.0),
                (2.0, 1.0),
                (1.0, 1.0),
            ]
        ]
    }

    # swapped coordinates with EPSG:4326
    result = parse_v33_ce(
        etree.fromstring("""
            <gmlce:SimpleTriangle gml:id="ID"
                    xmlns:gml="http://www.opengis.net/gml/3.2"
                    xmlns:gmlce="http://www.opengis.net/gml/3.3/ce"
                    srsName="EPSG:4326">
                <gml:pos>0.0 1.0</gml:pos>
                <gml:pos>0.0 2.0</gml:pos>
                <gml:pos>1.0 1.0</gml:pos>
            </gmlce:SimpleTriangle>
        """)
    )
    assert result == {
        'type': 'Polygon',
        'coordinates': [
            [
                (1.0, 0.0),
                (2.0, 0.0),
                (1.0, 1.0),
                (1.0, 0.0),
            ]
        ],
        'crs': {
            'type': 'name',
            'properties': {
                'name': 'EPSG:4326'
            }
        }
    }


def test_parse_simple_rectangle():
    # using gml:pos elements
    result = parse_v33_ce(
        etree.fromstring("""
            <gmlce:SimpleRectangle gml:id="ID"
                    xmlns:gml="http://www.opengis.net/gml/3.2"
                    xmlns:gmlce="http://www.opengis.net/gml/3.3/ce">
                <gml:pos>1.0 1.0</gml:pos>
                <gml:pos>1.0 2.0</gml:pos>
                <gml:pos>2.0 2.0</gml:pos>
                <gml:pos>2.0 1.0</gml:pos>
            </gmlce:SimpleRectangle>
        """)
    )
    assert result == {
        'type': 'Polygon',
        'coordinates': [
            [
                (1.0, 1.0),
                (1.0, 2.0),
                (2.0, 2.0),
                (2.0, 1.0),
                (1.0, 1.0),
            ]
        ]
    }

    # using gml:posList element
    result = parse_v33_ce(
        etree.fromstring("""
            <gmlce:SimpleRectangle gml:id="ID"
                    xmlns:gml="http://www.opengis.net/gml/3.2"
                    xmlns:gmlce="http://www.opengis.net/gml/3.3/ce">
                <gml:posList>1.0 1.0 1.0 2.0 2.0 2.0 2.0 1.0</gml:posList>
            </gmlce:SimpleRectangle>
        """)
    )
    assert result == {
        'type': 'Polygon',
        'coordinates': [
            [
                (1.0, 1.0),
                (1.0, 2.0),
                (2.0, 2.0),
                (2.0, 1.0),
                (1.0, 1.0),
            ]
        ]
    }

    # swapped coordinates with EPSG:4326
    result = parse_v33_ce(
        etree.fromstring("""
            <gmlce:SimpleRectangle gml:id="ID"
                    xmlns:gml="http://www.opengis.net/gml/3.2"
                    xmlns:gmlce="http://www.opengis.net/gml/3.3/ce"
                    srsName="EPSG:4326">
                <gml:pos>0.0 1.0</gml:pos>
                <gml:pos>0.0 2.0</gml:pos>
                <gml:pos>1.0 2.0</gml:pos>
                <gml:pos>1.0 1.0</gml:pos>
            </gmlce:SimpleRectangle>
        """)
    )
    assert result == {
        'type': 'Polygon',
        'coordinates': [
            [
                (1.0, 0.0),
                (2.0, 0.0),
                (2.0, 1.0),
                (1.0, 1.0),
                (1.0, 0.0),
            ]
        ],
        'crs': {
            'type': 'name',
            'properties': {
                'name': 'EPSG:4326'
            }
        }
    }


def test_parse_simple_polygon():
    # using gml:pos elements
    result = parse_v33_ce(
        etree.fromstring("""
            <gmlce:SimplePolygon gml:id="ID"
                    xmlns:gml="http://www.opengis.net/gml/3.2"
                    xmlns:gmlce="http://www.opengis.net/gml/3.3/ce">
                <gml:pos>1.0 1.0</gml:pos>
                <gml:pos>1.0 2.0</gml:pos>
                <gml:pos>2.0 2.0</gml:pos>
                <gml:pos>2.0 1.0</gml:pos>
            </gmlce:SimplePolygon>
        """)
    )
    assert result == {
        'type': 'Polygon',
        'coordinates': [
            [
                (1.0, 1.0),
                (1.0, 2.0),
                (2.0, 2.0),
                (2.0, 1.0),
                (1.0, 1.0),
            ]
        ]
    }

    # using gml:posList element
    result = parse_v33_ce(
        etree.fromstring("""
            <gmlce:SimplePolygon gml:id="ID"
                    xmlns:gml="http://www.opengis.net/gml/3.2"
                    xmlns:gmlce="http://www.opengis.net/gml/3.3/ce">
                <gml:posList>1.0 1.0 1.0 2.0 2.0 2.0 2.0 1.0</gml:posList>
            </gmlce:SimplePolygon>
        """)
    )
    assert result == {
        'type': 'Polygon',
        'coordinates': [
            [
                (1.0, 1.0),
                (1.0, 2.0),
                (2.0, 2.0),
                (2.0, 1.0),
                (1.0, 1.0),
            ]
        ]
    }

    # swapped coordinates with EPSG:4326
    result = parse_v33_ce(
        etree.fromstring("""
            <gmlce:SimplePolygon gml:id="ID"
                    xmlns:gml="http://www.opengis.net/gml/3.2"
                    xmlns:gmlce="http://www.opengis.net/gml/3.3/ce"
                    srsName="EPSG:4326">
                <gml:pos>0.0 1.0</gml:pos>
                <gml:pos>0.0 2.0</gml:pos>
                <gml:pos>1.0 2.0</gml:pos>
                <gml:pos>1.0 1.0</gml:pos>
            </gmlce:SimplePolygon>
        """)
    )
    assert result == {
        'type': 'Polygon',
        'coordinates': [
            [
                (1.0, 0.0),
                (2.0, 0.0),
                (2.0, 1.0),
                (1.0, 1.0),
                (1.0, 0.0),
            ]
        ],
        'crs': {
            'type': 'name',
            'properties': {
                'name': 'EPSG:4326'
            }
        }
    }

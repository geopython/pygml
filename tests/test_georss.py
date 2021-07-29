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

from pygml.georss import parse_georss


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

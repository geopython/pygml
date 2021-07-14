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

from typing import List, Dict

from lxml import etree

from .basics import parse_coordinates, parse_pos


NAMESPACE = 'http://www.opengis.net/gml/3.2'
NSMAP = {'gml': NAMESPACE}


def _get_positions(element: etree._Element, nsmap: Dict[str, str]) -> List[etree._Element]:
    return element.xpath('gml:pos', namespaces=nsmap)


def _get_coordinates(element: etree._Element, nsmap: Dict[str, str]) -> List[etree._Element]:
    return element.xpath('gml:coordinates', namespaces=nsmap)


def parse_v32(element: etree._Element) -> dict:
    qname = etree.QName(element.tag)
    assert qname.namespace == NAMESPACE

    if qname.localname == 'Point':
        positions = _get_positions(element, NSMAP)
        if positions:
            assert len(positions) == 1, 'Too many gml:pos elements'
            coords = parse_pos(positions[0].text)
        else:
            coordinates = _get_coordinates(element, NSMAP)
            if not coordinates:
                raise AssertionError(
                    'Neither gml:pos nor gml:coordinates found'
                )
            assert len(coordinates) == 1, 'Too many gml:coordinates elements'
            coordinates0 = coordinates[0]
            coords = parse_coordinates(
                coordinates0.text,
                cs=coordinates0.attrib.get('cs', ','),
                ts=coordinates0.attrib.get('ts', ' '),
                decimal=coordinates0.attrib.get('decimal', '.'),
            )[0]

        geometry = {
            'type': 'Point',
            'coordinates': coords
        }

    elif qname.localname == 'MultiPoint':
        pass

    return geometry

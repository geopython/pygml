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

from typing import List

from lxml import etree

from .basics import (
    parse_pos, parse_poslist, swap_coordinate_xy, swap_coordinates_xy
)
from .types import GeomDict
from .pre_v32 import NAMESPACE as NAMESPACE_PRE32, parse_pre_v32
from .v32 import NAMESPACE as NAMESPACE_32, parse_v32
from .v33 import NAMESPACE as NAMESPACE_33_CE, parse_v33_ce


NAMESPACE = 'http://www.georss.org/georss'
NSMAP = {'georss': NAMESPACE}


Element = etree._Element
Elements = List[Element]


def parse_georss(element: Element) -> GeomDict:
    """ Parses the GeoRSS basic elements to their respective GeoJSON
        representation. As all coordinates in GeoRSS are expressed in
        WGS84 and in Latitude/Longitude order, the coordinates are
        swapped to XY order.

        In case of georss:where, it is expected that it contains a
        single GML element which is parsed as either GML 3.1.1, GML 3.2
        or GML 3.3 CE.
    """
    qname = etree.QName(element.tag)
    if qname.namespace != NAMESPACE:
        raise ValueError(f'Unsupported namespace {qname.namespace}')

    bbox = None
    localname = qname.localname

    if localname == 'point':
        type_ = 'Point'
        coordinates = swap_coordinate_xy(parse_pos(element.text))
    elif localname == 'line':
        type_ = 'LineString'
        coordinates = swap_coordinates_xy(parse_poslist(element.text))
    elif localname == 'box':
        # boxes are expanded to Polygons, but store the 'bbox' value
        type_ = 'Polygon'
        low, high = swap_coordinates_xy(parse_poslist(element.text))
        lx, ly = low
        hx, hy = high
        coordinates = [
            [
                (lx, ly),
                (lx, hy),
                (hx, hy),
                (hx, ly),
                (lx, ly),
            ]
        ]
        bbox = (lx, ly, hx, hy)
    elif localname == 'polygon':
        type_ = 'Polygon'
        coordinates = [swap_coordinates_xy(parse_poslist(element.text))]

    elif localname == 'where':
        # special handling here: defer to the gml definition. Although,
        # only GML 3.1.1 is officially supported, we also allow GML 3.2 and 3.3
        if not len(element) == 1:
            raise ValueError(
                'Invalid number of child elements in georss:where'
            )
        child = element[0]
        child_namespace = etree.QName(child.tag).namespace

        if child_namespace == NAMESPACE_PRE32:
            return parse_pre_v32(child)
        elif child_namespace == NAMESPACE_32:
            return parse_v32(child)
        elif child_namespace == NAMESPACE_33_CE:
            return parse_v33_ce(child)
        else:
            raise ValueError(
                f'Unsupported child element in georss:where: {child.tag}'
            )
    else:
        raise ValueError(f'Unsupported georss element: {localname}')

    result = {
        'type': type_,
        'coordinates': coordinates,
    }
    if bbox:
        result['bbox'] = bbox

    return result

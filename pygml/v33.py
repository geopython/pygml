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

from .types import GeomDict
from .v3_common import (
    GML3Parser, determine_srs,
    parse_envelope, parse_point, parse_multi_point,
    parse_linestring_or_linear_ring, parse_multi_curve, parse_polygon,
    parse_multi_surface, parse_multi_geometry,
    NameSpaceMap, Element, ParseResult
)
from .v32 import NAMESPACE as NAMESPACE_32


NAMESPACE = 'http://www.opengis.net/gml/3.3/ce'
NSMAP: NameSpaceMap = {
    'gmlce': NAMESPACE,
    'gml': NAMESPACE_32
}


def parse_simple_triangle_or_rectangle(element: Element,
                                       nsmap: NameSpaceMap) -> ParseResult:
    exterior, srs = parse_linestring_or_linear_ring(
        element, nsmap
    )
    exterior = exterior['coordinates']
    exterior.append(exterior[0])
    return {
        'type': 'Polygon',
        'coordinates': [exterior]
    }, srs


def parse_simple_polygon(element: Element, nsmap: NameSpaceMap) -> ParseResult:
    exterior, srs = parse_linestring_or_linear_ring(
        element, nsmap
    )
    exterior = exterior['coordinates']
    exterior.append(exterior[0])
    return {
        'type': 'Polygon',
        'coordinates': [exterior]
    }, srs


def parse_simple_multi_point(element: Element,
                             nsmap: NameSpaceMap) -> ParseResult:
    sub_elements = element.xpath(
        'gml:MultiPoint|gmlce:SimpleMultiPoint', namespaces=nsmap
    )

    multi_points, srss = zip(*(
        parse_multi_point(sub_elem) if etree.QName().localname == 'MultiPoint'
        else parse_simple_multi_point(sub_elem)
        for sub_elem in sub_elements
    ))

    srs = determine_srs(*srss)

    # merge the possibly nested multi points into a single list of coordinates
    coordinates = [
        coord
        for multi_point in multi_points
        for coord in multi_point['coordinates']
    ]

    return {
        'type': 'MultiPoint',
        'coordinates': coordinates
    }, srs


GML33_CE_PARSER = GML3Parser([NAMESPACE, NAMESPACE_32], NSMAP, {
    'Point': parse_point,
    'MultiPoint': parse_multi_point,
    'LineString': parse_linestring_or_linear_ring,
    'MultiCurve': parse_multi_curve,
    'Polygon': parse_polygon,
    'Envelope': parse_envelope,
    'MultiSurface': parse_multi_surface,
    'MultiGeometry': parse_multi_geometry,
    'SimpleTriangle': parse_simple_triangle_or_rectangle,
    'SimpleRectangle': parse_simple_triangle_or_rectangle,
    'SimplePolygon': parse_simple_polygon,
    'SimpleMultiPoint': parse_simple_multi_point,
})


def parse_v33_ce(element: Element) -> GeomDict:
    """ Main parsing function for GML 3.3 CE XML structures.

        The following XML tags can be parsed to their respective GeoJSON
        counterpart:

          - gmlce:SimpleTriangle -> Polygon
          - gmlce:SimpleRectangel -> Polygon
          - gmlce:SimplePolygon -> Polygon
          - TODO: gmlce:SimpleMultiPoint -> MultiPoint
          - gml:Point -> Point
          - gml:MultiPoint -> MultiPoint
          - gml:LineString -> LineString
          - gml:MultiCurve (with only gml:LineString curve members)
            -> MultiLineString
          - gml:Polygon -> Polygon
          - gml:MultiSurface (with only gml:Polygon surface members)
            -> MultiPolygon
          - gml:MultiGeometry (with any of the aforementioned types as
            geometry members) -> GeometryCollection

        The SRS of the geometry is determined and the coordinates are
        flipped to XY order in GeoJSON when they are in YX order in GML.

        Returns:
            the parsed GeoJSON geometry as a dict. Contains a 'type'
            field, a 'coordinates' field and potentially a 'crs' field
            when the geometries SRS could be determined. This field
            follows the structure laid out in the
            `draft for GeoJSON <https://gist.github.com/sgillies/1233327>`_.
    """
    return GML33_CE_PARSER.parse(element)

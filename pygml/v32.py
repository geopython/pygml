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

from .types import GeomDict
from .v3_common import (
    GML3Encoder, GML3Parser, parse_envelope, parse_point, parse_multi_point,
    parse_linestring_or_linear_ring,
    parse_multi_curve, parse_polygon, parse_multi_surface,
    parse_multi_geometry
)

NAMESPACE = 'http://www.opengis.net/gml/3.2'
NSMAP = {'gml': NAMESPACE}


Element = etree._Element
Elements = List[Element]

# set up a parser
GML32_PARSER = GML3Parser([NAMESPACE], NSMAP, {
    'Point': parse_point,
    'MultiPoint': parse_multi_point,
    'LineString': parse_linestring_or_linear_ring,
    'MultiCurve': parse_multi_curve,
    'Polygon': parse_polygon,
    'Envelope': parse_envelope,
    'MultiSurface': parse_multi_surface,
    'MultiGeometry': parse_multi_geometry,
})


def parse_v32(element: Element) -> GeomDict:
    """ Main parsing function for GML 3.2 XML structures.

        The following XML tags can be parsed to their respective GeoJSON
        counterpart:

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

    return GML32_PARSER.parse(element)


GML32_ENCODER = GML3Encoder(NAMESPACE, NSMAP, True)


def encode_v32(geometry: GeomDict, identifier: str) -> Element:
    """ Encodes the given GeoJSON dict to its most simple GML 3.2
        representation. As in GML 3.2 the gml:id attribute is mandatory,
        the identifier must be passed as well.

        In preparation of the encoding, the coordinates may have to be
        swapped from XY order to YX order, depending on the used CRS.
        This includes the case when no CRS is specified, as this means
        the default WGS84 in GeoJSON, which in turn uses
        latitude/longitude ordering GML.

        This function returns an ``lxml.etree._Element`` which can be
        altered or serialized.

        >>> from pygml.v32 import encode_v32
        >>> from lxml import etree
        >>> tree = encode_v32({
        ...     'type': 'Point',
        ...     'coordinates': (1.0, 1.0)
        ... }, 'ID')
        >>> print(etree.tostring(tree, pretty_print=True).decode())
        <gml:Point xmlns:gml="http://www.opengis.net/gml/3.2"
            srsName="urn:ogc:def:crs:OGC::CRS84" gml:id="ID">
          <gml:pos>1.0 1.0</gml:pos>
        </gml:Point>
    """

    return GML32_ENCODER.encode(geometry, identifier)

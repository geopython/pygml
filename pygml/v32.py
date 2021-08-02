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
from lxml.builder import ElementMaker

from .basics import swap_coordinates_xy
from .axisorder import is_crs_yx
from .types import Coordinates, GeomDict
from .v3_common import (
    parse_envelope, parse_point, parse_multi_point, parse_linestring_or_linear_ring,
    parse_multi_curve, parse_polygon, parse_multi_surface,
    parse_multi_geometry
)

NAMESPACE = 'http://www.opengis.net/gml/3.2'
NSMAP = {'gml': NAMESPACE}


Element = etree._Element
Elements = List[Element]

# set up a map from tag name to parsing function
_HANDLERS = {
    'Point': parse_point,
    'MultiPoint': parse_multi_point,
    'LineString': parse_linestring_or_linear_ring,
    'MultiCurve': parse_multi_curve,
    'Polygon': parse_polygon,
    'Envelope': parse_envelope,
    'MultiSurface': parse_multi_surface,
    'MultiGeometry': parse_multi_geometry,
}


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
    qname = etree.QName(element.tag)
    if qname.namespace != NAMESPACE:
        raise ValueError(f'Namespace {qname.namespace} is not supported')

    # get a registered handler function
    handler = _HANDLERS.get(qname.localname)
    if not handler:
        raise ValueError(
            f'XML nodes of type {qname.localname} are not supported.'
        )

    # parse the geometry
    if qname.localname == 'MultiGeometry':
        geometry, srs = handler(element, NSMAP, parse_v32)
    else:
        geometry, srs = handler(element, NSMAP)

    # handle SRS: maybe swap YX ordered coordinates to XY
    # and store the SRS as a crs field in the geometry
    if srs:
        geometry = maybe_swap_coordinates(geometry, srs)
        geometry['crs'] = {
            'type': 'name',
            'properties': {
                'name': srs
            }
        }

    return geometry


def maybe_swap_coordinates(geometry: GeomDict, srs: str) -> GeomDict:
    if is_crs_yx(srs):
        type_ = geometry['type']
        coordinates = geometry['coordinates']

        if type_ == 'Point':
            coordinates = (coordinates[1], coordinates[0], *coordinates[2:])
        elif type_ in ('MultiPoint', 'LineString'):
            coordinates = swap_coordinates_xy(coordinates)
        elif type_ in ('MultiLineString', 'Polygon'):
            coordinates = [
                swap_coordinates_xy(line)
                for line in coordinates
            ]
        elif type_ == 'MultiPolygon':
            coordinates = [
                [
                    swap_coordinates_xy(line)
                    for line in polygon
                ] for polygon in coordinates
            ]

        geometry['coordinates'] = coordinates
        return geometry
    else:
        return geometry


GML = ElementMaker(namespace=NAMESPACE, nsmap=NSMAP)


def _encode_pos_list(coordinates: Coordinates) -> Element:
    return GML(
        'posList',
        ' '.join(
            ' '.join(str(c) for c in coordinate)
            for coordinate in coordinates
        )
    )


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
    crs = geometry.get('crs')
    srs = None
    id_attr = {f'{{{NAMESPACE}}}id': identifier}
    if crs:
        srs = crs.get('properties', {}).get('name')
    else:
        # GeoJSON is by default in CRS84
        srs = 'urn:ogc:def:crs:OGC::CRS84'
    attrs = {
        'srsName': srs,
        **id_attr
    }
    geometry = maybe_swap_coordinates(geometry, srs)

    type_ = geometry['type']
    # GeometryCollections have no coordinates
    coordinates = geometry.get('coordinates')
    if type_ == 'Point':
        return GML(
            'Point',
            GML('pos', ' '.join(str(c) for c in coordinates)),
            **attrs
        )

    elif type_ == 'MultiPoint':
        return GML(
            'MultiPoint',
            GML('geometryMembers', *[
                GML(
                    'Point',
                    GML('pos', ' '.join(str(c) for c in coordinate)),
                    **{f'{{{NAMESPACE}}}id': f'{identifier}_{i}'}
                )
                for i, coordinate in enumerate(coordinates)
            ]),
            **attrs
        )

    elif type_ == 'LineString':
        return GML(
            'LineString',
            _encode_pos_list(coordinates),
            **attrs
        )

    elif type_ == 'MultiLineString':
        return GML(
            'MultiCurve',
            GML(
                'curveMembers', *[
                    GML(
                        'LineString',
                        _encode_pos_list(linestring),
                        **{f'{{{NAMESPACE}}}id': f'{identifier}_{i}'}
                    )
                    for i, linestring in enumerate(coordinates)
                ]
            ),
            **attrs
        )

    elif type_ == 'Polygon':
        return GML(
            'Polygon',
            GML(
                'exterior',
                GML(
                    'LinearRing',
                    _encode_pos_list(coordinates[0]),
                )
            ), *[
                GML(
                    'interior',
                    GML(
                        'LinearRing',
                        _encode_pos_list(linear_ring),
                    )
                )
                for linear_ring in coordinates[1:]
            ],
            **attrs
        )

    elif type_ == 'MultiPolygon':
        return GML(
            'MultiSurface',
            GML(
                'surfaceMembers', *[
                    GML(
                        'Polygon',
                        GML(
                            'exterior',
                            GML(
                                'LinearRing',
                                _encode_pos_list(polygon[0]),
                            )
                        ), *[
                            GML(
                                'interior',
                                GML(
                                    'LinearRing',
                                    _encode_pos_list(linear_ring),
                                )
                            )
                            for linear_ring in polygon[1:]
                        ],
                        **{f'{{{NAMESPACE}}}id': f'{identifier}_{i}'}
                    )
                    for i, polygon in enumerate(coordinates)
                ]
            ),
            **attrs
        )

    elif type_ == 'GeometryCollection':
        return GML(
            'MultiGeometry',
            GML(
                'geometryMembers', *[
                    encode_v32(sub_geometry, f'{identifier}_{i}')
                    for i, sub_geometry in enumerate(geometry['geometries'])
                ]
            ),
            **id_attr
        )

    raise ValueError(f'Unable to encode geometry of type {type_}')

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

from typing import Callable, List, Optional, Tuple

from lxml import etree
from lxml.builder import ElementMaker

from .basics import (
    parse_coordinates, parse_pos, parse_poslist,
    swap_coordinates_xy
)
from .axisorder import is_crs_yx
from .types import Coordinates, GeomDict


NAMESPACE = 'http://www.opengis.net/gml/3.2'
NSMAP = {'gml': NAMESPACE}


Element = etree._Element
Elements = List[Element]


def _determine_srs(*srss: List[Optional[str]]) -> Optional[str]:
    srss = set(srss)
    if None in srss:
        srss.remove(None)

    if len(srss) > 1:
        raise ValueError(f'Conflicting SRS definitions: {", ".join(srss)}')
    try:
        return srss.pop()
    except KeyError:
        return None


_HANDLERS = {}


def handle_element(tag_localname: str) -> Callable:
    """ Decorator to register a handler function for an XML tag localname """
    def inner(func: Callable[[Element], Tuple[GeomDict, str]]):
        _HANDLERS[tag_localname] = func
        return func

    return inner


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
    geometry, srs = handler(element)

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


@handle_element('Point')
def _parse_point(element: Element) -> Tuple[GeomDict, str]:
    positions = element.xpath('gml:pos', namespaces=NSMAP)
    coordinates = element.xpath('gml:coordinates', namespaces=NSMAP)
    srs = None
    if positions:
        if len(positions) > 1:
            raise ValueError('Too many gml:pos elements')
        coords = parse_pos(positions[0].text)
        srs = positions[0].attrib.get('srsName')
    elif coordinates:
        if len(coordinates) > 1:
            raise ValueError('Too many gml:coordinates elements')

        coordinates0 = coordinates[0]
        coords = parse_coordinates(
            coordinates0.text,
            cs=coordinates0.attrib.get('cs', ','),
            ts=coordinates0.attrib.get('ts', ' '),
            decimal=coordinates0.attrib.get('decimal', '.'),
        )[0]
    else:
        raise ValueError(
            'Neither gml:pos nor gml:coordinates found'
        )

    srs = _determine_srs(element.attrib.get('srsName'), srs)
    return {
        'type': 'Point',
        'coordinates': coords
    }, srs


@handle_element('MultiPoint')
def _parse_multi_point(element: Element) -> Tuple[GeomDict, str]:
    points, srss = zip(*(
        _parse_point(point_elem)
        for point_elem in element.xpath(
            '(gml:pointMember|gml:pointMembers)/*', namespaces=NSMAP
        )
    ))

    srs = _determine_srs(element.attrib.get('srsName'), *srss)

    return {
        'type': 'MultiPoint',
        'coordinates': [
            point['coordinates']
            for point in points
        ]
    }, srs


@handle_element('LineString')
def _parse_linestring_or_linear_ring(element: Element) -> Tuple[GeomDict, str]:
    pos_lists = element.xpath('gml:posList', namespaces=NSMAP)
    poss = element.xpath('gml:pos', namespaces=NSMAP)
    coordinates_elems = element.xpath('gml:coordinates', namespaces=NSMAP)

    if pos_lists:
        if len(pos_lists) > 1:
            raise ValueError('Too many gml:posList elements')

        pos_list0 = pos_lists[0]
        coordinates = parse_poslist(
            pos_list0.text,
            int(pos_list0.attrib.get('srsDimension', 2))
        )
        srs = pos_list0.attrib.get('srsName')
    elif poss:
        coordinates = [
            parse_pos(pos.text)
            for pos in poss
        ]
        srs = _determine_srs(
            *element.xpath('gml:pos/@srsName', namespaces=NSMAP)
        )
    elif coordinates_elems:
        if not coordinates_elems:
            raise ValueError(
                'Neither gml:pos nor gml:coordinates found'
            )
        elif len(coordinates_elems) > 1:
            raise ValueError('Too many gml:coordinates elements')

        coordinates0 = coordinates_elems[0]
        coordinates = parse_coordinates(
            coordinates0.text,
            cs=coordinates0.attrib.get('cs', ','),
            ts=coordinates0.attrib.get('ts', ' '),
            decimal=coordinates0.attrib.get('decimal', '.'),
        )
        srs = None
    else:
        raise ValueError('No gml:posList, gml:pos or gml:coordinates found')

    srs = _determine_srs(element.attrib.get('srsName'), srs)

    return {
        'type': 'LineString',
        'coordinates': coordinates
    }, srs


@handle_element('MultiCurve')
def _parse_multi_curve(element: Element) -> Tuple[GeomDict, str]:
    linestring_elements = element.xpath(
        '(gml:curveMember|gml:curveMembers)/gml:LineString',
        namespaces=NSMAP
    )
    are_not_linestrings = (
        etree.QName(e.tag).localname != 'LineString'
        for e in linestring_elements
    )
    if any(are_not_linestrings):
        raise ValueError(
            'Only gml:LineString elements are supported for gml:MultiCurves'
        )

    linestrings, srss = zip(*(
        _parse_linestring_or_linear_ring(linestring_element)
        for linestring_element in linestring_elements
    ))

    srs = _determine_srs(element.attrib.get('srsName'), *srss)

    return {
        'type': 'MultiLineString',
        'coordinates': [
            linestring['coordinates']
            for linestring in linestrings
        ]
    }, srs


@handle_element('Polygon')
def _parse_polygon(element: Element) -> Tuple[GeomDict, str]:
    exterior_rings = element.xpath(
        'gml:exterior/gml:LinearRing', namespaces=NSMAP
    )
    if not exterior_rings:
        raise ValueError('No gml:exterior/gml:LinearRing')
    elif len(exterior_rings) > 1:
        raise ValueError('Too many gml:exterior/gml:LinearRing elements')

    exterior, ext_srs = _parse_linestring_or_linear_ring(exterior_rings[0])
    exterior = exterior['coordinates']

    interior_rings, int_srss = zip(*(
        _parse_linestring_or_linear_ring(linear_ring)
        for linear_ring in element.xpath(
            'gml:interior/gml:LinearRing', namespaces=NSMAP
        )
    ))
    interiors = [
        ring['coordinates']
        for ring in interior_rings
    ]

    srs = _determine_srs(element.attrib.get('srsName'), ext_srs, *int_srss)

    return {
        'type': 'Polygon',
        'coordinates': [exterior, *interiors]
    }, srs


@handle_element('MultiSurface')
def _parse_multi_surface(element: Element) -> Tuple[GeomDict, str]:
    polygon_elements = element.xpath(
        '(gml:surfaceMember|gml:surfaceMembers)/gml:Polygon',
        namespaces=NSMAP
    )
    are_not_polygons = (
        etree.QName(e.tag).localname != 'Polygon' for e in polygon_elements
    )
    if any(are_not_polygons):
        raise ValueError(
            'Only gml:Polygon elements are supported for gml:MultiSurfaces'
        )

    polygons, srss = zip(*(
        _parse_polygon(polygon_element)
        for polygon_element in polygon_elements
    ))

    srs = _determine_srs(element.attrib.get('srsName'), *srss)

    return {
        'type': 'MultiPolygon',
        'coordinates': [
            polygon['coordinates']
            for polygon in polygons
        ]
    }, srs


@handle_element('MultiGeometry')
def _parse_multi_geometry(element: Element) -> Tuple[GeomDict, str]:
    sub_elements = element.xpath(
        '(gml:geometryMember|gml:geometryMembers)/*', namespaces=NSMAP
    )

    return {
        'type': 'GeometryCollection',
        'geometries': [parse_v32(sub_element) for sub_element in sub_elements]
    }, element.attrib.get('srsName')


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

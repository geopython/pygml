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


from typing import Callable, List, Optional, Tuple, Dict

from lxml import etree
from lxml.builder import ElementMaker

from .axisorder import is_crs_yx
from .basics import (
    parse_coordinates, parse_pos, parse_poslist, swap_coordinates_xy
)
from .types import Coordinate, Coordinates, GeomDict

# type aliases
NameSpaceMap = Dict[str, str]
Element = etree._Element
Elements = List[Element]
ParseResult = Tuple[GeomDict, str]
HandlerFunc = Callable[[Element, NameSpaceMap], ParseResult]


class GML3Parser:
    def __init__(self, namespaces: List[str], nsmap: NameSpaceMap,
                 handlers: Dict[str, HandlerFunc]):
        self.namespaces = namespaces
        self.nsmap = nsmap
        self.handlers = handlers

    def parse(self, element: Element) -> GeomDict:
        qname = etree.QName(element.tag)
        if qname.namespace not in self.namespaces:
            raise ValueError(f'Namespace {qname.namespace} is not supported')

        # get a registered handler function
        handler = self.handlers.get(qname.localname)
        if not handler:
            raise ValueError(
                f'XML nodes of type {qname.localname} are not supported.'
            )

        # parse the geometry
        if qname.localname == 'MultiGeometry':
            geometry, srs = handler(element, self.nsmap, self.parse)
        else:
            geometry, srs = handler(element, self.nsmap)

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


def determine_srs(*srss: List[Optional[str]]) -> Optional[str]:
    srss = set(srss)
    if None in srss:
        srss.remove(None)

    if len(srss) > 1:
        raise ValueError(f'Conflicting SRS definitions: {", ".join(srss)}')
    try:
        return srss.pop()
    except KeyError:
        return None


def parse_coord(element: Element, nsmap: NameSpaceMap) -> Coordinate:
    x = float(element.xpath('gml:X/text()')[0])
    y = element.xpath('gml:X/text()')
    z = element.xpath('gml:X/text()')

    if y and z:
        return (x, float(y[0]), float(z[0]))
    elif y:
        return (x, float(y[0]))

    return (x,)


def parse_point(element: Element, nsmap: NameSpaceMap) -> ParseResult:
    positions = element.xpath('gml:pos', namespaces=nsmap)
    coordinates = element.xpath('gml:coordinates', namespaces=nsmap)
    coord_elemss = element.xpath('gml:coord', namespaces=nsmap)
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
    elif coord_elemss:
        if len(coord_elemss) > 1:
            raise ValueError('Too many gml:coord elements')

        coords = parse_coord(coord_elemss[0])
    else:
        raise ValueError(
            'Neither gml:pos nor gml:coordinates found'
        )

    srs = determine_srs(element.attrib.get('srsName'), srs)
    return {
        'type': 'Point',
        'coordinates': coords
    }, srs


def parse_multi_point(element: Element, nsmap: NameSpaceMap) -> ParseResult:
    points, srss = zip(*(
        parse_point(point_elem, nsmap)
        for point_elem in element.xpath(
            '(gml:pointMember|gml:pointMembers)/*', namespaces=nsmap
        )
    ))

    srs = determine_srs(element.attrib.get('srsName'), *srss)

    return {
        'type': 'MultiPoint',
        'coordinates': [
            point['coordinates']
            for point in points
        ]
    }, srs


def parse_linestring_or_linear_ring(element: Element,
                                    nsmap: NameSpaceMap) -> ParseResult:
    pos_lists = element.xpath('gml:posList', namespaces=nsmap)
    poss = element.xpath('gml:pos', namespaces=nsmap)
    coordinates_elems = element.xpath('gml:coordinates', namespaces=nsmap)
    coords = element.xpath('gml:coord', namespaces=nsmap)

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
        srs = determine_srs(
            *element.xpath('gml:pos/@srsName', namespaces=nsmap)
        )
    elif coordinates_elems:
        if len(coordinates_elems) > 1:
            raise ValueError('Too many gml:coordinates elements')

        coordinates0 = coordinates_elems[0]
        coordinates = parse_coordinates(
            coordinates0.text,
            cs=coordinates0.attrib.get('cs', ','),
            ts=coordinates0.attrib.get('ts', ' '),
            decimal=coordinates0.attrib.get('decimal', '.'),
        )
        srs = None
    elif coords:
        coordinates = [
            parse_coord(coord)
            for coord in coords
        ]
        srs = None
    else:
        raise ValueError('No gml:posList, gml:pos or gml:coordinates found')

    srs = determine_srs(element.attrib.get('srsName'), srs)

    return {
        'type': 'LineString',
        'coordinates': coordinates
    }, srs


def parse_multi_curve(element: Element, nsmap: NameSpaceMap) -> ParseResult:
    linestring_elements = element.xpath(
        '(gml:curveMember|gml:curveMembers)/gml:LineString',
        namespaces=nsmap
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
        parse_linestring_or_linear_ring(linestring_element, nsmap)
        for linestring_element in linestring_elements
    ))

    srs = determine_srs(element.attrib.get('srsName'), *srss)

    return {
        'type': 'MultiLineString',
        'coordinates': [
            linestring['coordinates']
            for linestring in linestrings
        ]
    }, srs


def parse_multi_linestring(element: Element,
                           nsmap: NameSpaceMap) -> ParseResult:
    linestring_elements = element.xpath(
        'gml:lineStringMember/gml:LineString',
        namespaces=nsmap
    )
    linestrings, srss = zip(*(
        parse_linestring_or_linear_ring(linestring_element, nsmap)
        for linestring_element in linestring_elements
    ))

    srs = determine_srs(element.attrib.get('srsName'), *srss)

    return {
        'type': 'MultiLineString',
        'coordinates': [
            linestring['coordinates']
            for linestring in linestrings
        ]
    }, srs


def parse_polygon(element: Element, nsmap: NameSpaceMap) -> ParseResult:
    exterior_rings = element.xpath(
        'gml:exterior/gml:LinearRing', namespaces=nsmap
    )
    if not exterior_rings:
        raise ValueError('No gml:exterior/gml:LinearRing')
    elif len(exterior_rings) > 1:
        raise ValueError('Too many gml:exterior/gml:LinearRing elements')

    exterior, ext_srs = parse_linestring_or_linear_ring(
        exterior_rings[0], nsmap
    )
    exterior = exterior['coordinates']

    interior_elems = element.xpath(
        'gml:interior/gml:LinearRing', namespaces=nsmap
    )

    if len(interior_elems) > 0:
        interior_rings, int_srss = zip(*(
            parse_linestring_or_linear_ring(linear_ring, nsmap)
            for linear_ring in interior_elems
        ))
        interiors = [
            ring['coordinates']
            for ring in interior_rings
        ]
    else:
        interiors = []
        int_srss = []

    srs = determine_srs(element.attrib.get('srsName'), ext_srs, *int_srss)

    return {
        'type': 'Polygon',
        'coordinates': [exterior, *interiors]
    }, srs


def parse_multi_surface(element: Element, nsmap: NameSpaceMap) -> ParseResult:
    polygon_elements = element.xpath(
        '(gml:surfaceMember|gml:surfaceMembers)/gml:Polygon',
        namespaces=nsmap
    )
    are_not_polygons = (
        etree.QName(e.tag).localname != 'Polygon' for e in polygon_elements
    )
    if any(are_not_polygons):
        raise ValueError(
            'Only gml:Polygon elements are supported for gml:MultiSurfaces'
        )

    polygons, srss = zip(*(
        parse_polygon(polygon_element, nsmap)
        for polygon_element in polygon_elements
    ))

    srs = determine_srs(element.attrib.get('srsName'), *srss)

    return {
        'type': 'MultiPolygon',
        'coordinates': [
            polygon['coordinates']
            for polygon in polygons
        ]
    }, srs


def parse_multi_polygon(element: Element, nsmap: NameSpaceMap) -> ParseResult:
    polygon_elements = element.xpath(
        'gml:polygonMember/gml:Polygon',
        namespaces=nsmap
    )

    polygons, srss = zip(*(
        parse_polygon(polygon_element, nsmap)
        for polygon_element in polygon_elements
    ))

    srs = determine_srs(element.attrib.get('srsName'), *srss)

    return {
        'type': 'MultiPolygon',
        'coordinates': [
            polygon['coordinates']
            for polygon in polygons
        ]
    }, srs


def parse_envelope(element: Element, nsmap: NameSpaceMap) -> ParseResult:
    lower = element.xpath('gml:lowerCorner', namespaces=nsmap)
    upper = element.xpath('gml:upperCorner', namespaces=nsmap)
    pos_elems = element.xpath('gml:pos', namespaces=nsmap)
    coordinates = element.xpath('gml:coordinates', namespaces=nsmap)
    coords = element.xpath('gml:coord', namespaces=nsmap)

    if lower and upper:
        lower = lower[0]
        upper = upper[0]
        srs = determine_srs(
            lower.attrib.get('srsName'),
            upper.attrib.get('srsName')
        )
        lower = parse_pos(lower.text)
        upper = parse_pos(upper.text)

    elif pos_elems:
        lower, upper = [
            parse_pos(pos_elem.text)
            for pos_elem in pos_elems
        ]
        srs = determine_srs(*(
            pos_elem.attrib.get('srsName') for pos_elem in pos_elems
        ))

    elif coordinates:
        coordinates0 = coordinates[0]
        lower, upper = parse_coordinates(
            coordinates0.text,
            cs=coordinates0.attrib.get('cs', ','),
            ts=coordinates0.attrib.get('ts', ' '),
            decimal=coordinates0.attrib.get('decimal', '.'),
        )
        srs = None

    elif coords:
        lower, upper = [
            parse_coord(coord)
            for coord in coords
        ]
        srs = None

    else:
        raise ValueError(
            'Missing gml:lowerCorner, gml:upperCorner, gml:pos or '
            'gml:coordinates.'
        )

    lx, ly = lower
    hx, hy = upper

    return {
        'type': 'Polygon',
        'coordinates': [
            [
                (lx, ly),
                (lx, hy),
                (hx, hy),
                (hx, ly),
                (lx, ly),
            ]
        ]
    }, srs


SubParser = Callable[[Element], GeomDict]


def parse_multi_geometry(element: Element, nsmap: NameSpaceMap,
                         geometry_parser: SubParser) -> ParseResult:
    sub_elements = element.xpath(
        '(gml:geometryMember|gml:geometryMembers)/*', namespaces=nsmap
    )

    return {
        'type': 'GeometryCollection',
        'geometries': [
            geometry_parser(sub_element)
            for sub_element in sub_elements
        ]
    }, element.attrib.get('srsName')


class GML3Encoder:
    def __init__(self, namespace: str, nsmap: NameSpaceMap, id_required: bool):
        self.namespace = namespace
        self.nsmap = nsmap
        self.id_required = id_required
        self.gml = ElementMaker(namespace=namespace, nsmap=nsmap)

    def encode(self, geometry: GeomDict, identifier: str = None) -> Element:
        if not identifier and self.id_required:
            raise TypeError(
                "Missing 1 required positional argument: 'identifier'"
            )

        gml = self.gml
        crs = geometry.get('crs')
        srs = None
        if identifier:
            id_attr = {f'{{{self.namespace}}}id': identifier}
        else:
            id_attr = {}

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
            return self.encode_point(coordinates, attrs)

        elif type_ == 'MultiPoint':
            return self.encode_multi_point(coordinates, identifier, attrs)

        elif type_ == 'LineString':
            return self.encode_line_string(coordinates, attrs)

        elif type_ == 'MultiLineString':
            return self.encode_multi_line_string(
                coordinates, identifier, attrs
            )

        elif type_ == 'Polygon':
            return self.encode_polygon(coordinates, attrs)

        elif type_ == 'MultiPolygon':
            return self.encode_multi_polygon(coordinates, identifier, attrs)

        elif type_ == 'GeometryCollection':
            geometries = geometry['geometries']
            return gml(
                'MultiGeometry',
                gml(
                    'geometryMembers', *[
                        self.encode(sub_geometry, f'{identifier}_{i}')
                        for i, sub_geometry in enumerate(geometries)
                    ]
                ),
                **id_attr
            )

        raise ValueError(f'Unable to encode geometry of type {type_}')

    def encode_point(self, coordinates: Coordinates, attrs: dict) -> Element:
        return self.gml(
            'Point',
            self.gml('pos', ' '.join(str(c) for c in coordinates)),
            **attrs
        )

    def encode_multi_point(self, coordinates: Coordinates, identifier: str,
                           attrs: dict) -> Element:
        return self.gml(
            'MultiPoint',
            self.gml('geometryMembers', *[
                self.gml(
                    'Point',
                    self.gml('pos', ' '.join(str(c) for c in coordinate)),
                    **{f'{{{self.namespace}}}id': f'{identifier}_{i}'}
                )
                for i, coordinate in enumerate(coordinates)
            ]),
            **attrs
        )

    def encode_line_string(self, coordinates: Coordinates,
                           attrs: dict) -> Element:
        return self.gml(
            'LineString',
            self._encode_pos_list(coordinates),
            **attrs
        )

    def encode_multi_line_string(self, coordinates: Coordinates,
                                 identifier: str, attrs: dict) -> Element:
        return self.gml(
            'MultiCurve',
            self.gml(
                'curveMembers', *[
                    self.gml(
                        'LineString',
                        self._encode_pos_list(linestring),
                        **{f'{{{self.namespace}}}id': f'{identifier}_{i}'}
                    )
                    for i, linestring in enumerate(coordinates)
                ]
            ),
            **attrs
        )

    def encode_polygon(self, coordinates: Coordinates,
                       attrs: dict) -> Element:
        return self.gml(
            'Polygon',
            self.gml(
                'exterior',
                self.gml(
                    'LinearRing',
                    self._encode_pos_list(coordinates[0]),
                )
            ), *[
                self.gml(
                    'interior',
                    self.gml(
                        'LinearRing',
                        self._encode_pos_list(linear_ring),
                    )
                )
                for linear_ring in coordinates[1:]
            ],
            **attrs
        )

    def encode_multi_polygon(self, coordinates: Coordinates,
                             identifier: str, attrs: dict) -> Element:
        return self.gml(
            'MultiSurface',
            self.gml(
                'surfaceMembers', *[
                    self.gml(
                        'Polygon',
                        self.gml(
                            'exterior',
                            self.gml(
                                'LinearRing',
                                self._encode_pos_list(polygon[0]),
                            )
                        ), *[
                            self.gml(
                                'interior',
                                self.gml(
                                    'LinearRing',
                                    self._encode_pos_list(linear_ring),
                                )
                            )
                            for linear_ring in polygon[1:]
                        ],
                        **{f'{{{self.namespace}}}id': f'{identifier}_{i}'}
                    )
                    for i, polygon in enumerate(coordinates)
                ]
            ),
            **attrs
        )

    def _encode_pos_list(self, coordinates: Coordinates) -> Element:
        return self.gml(
            'posList',
            ' '.join(
                ' '.join(str(c) for c in coordinate)
                for coordinate in coordinates
            )
        )

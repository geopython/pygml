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

from .basics import (
    parse_coordinates, parse_pos, parse_poslist,
)
from .types import Coordinate, GeomDict

# type aliases
NameSpaceMap = Dict[str, str]
Element = etree._Element
Elements = List[Element]
ParseResult = Tuple[GeomDict, str]


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

    interior_rings, int_srss = zip(*(
        parse_linestring_or_linear_ring(linear_ring, nsmap)
        for linear_ring in element.xpath(
            'gml:interior/gml:LinearRing', namespaces=nsmap
        )
    ))
    interiors = [
        ring['coordinates']
        for ring in interior_rings
    ]

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

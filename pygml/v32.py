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

from .basics import (
    parse_coordinates, parse_pos, parse_poslist,
    swap_coordinates_xy
)
from .axisorder import is_crs_yx
from .types import GeomDict


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
            [draft for GeoJSON](https://gist.github.com/sgillies/1233327).
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
        # GeometryCollection are
        geometry['coordinates'] = coordinates
        return geometry
    else:
        return geometry


@handle_element('Point')
def _parse_point(element: Element) -> Tuple[GeomDict, str]:
    positions = element.xpath('gml:pos', namespaces=NSMAP)
    coordinates = element.xpath('gml:coordinates', namespaces=NSMAP)
    if positions:
        assert len(positions) == 1, 'Too many gml:pos elements'
        coords = parse_pos(positions[0].text)
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

    return {
        'type': 'Point',
        'coordinates': coords
    }, element.attrib.get('srsName')


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
            parse_pos(pos)
            for pos in poss
        ]
        srs = _determine_srs(
            *element.xpath('gml:pos@srsName', namespaces=NSMAP)
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

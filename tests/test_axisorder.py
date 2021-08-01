import pytest

from pygml.axisorder import is_crs_yx, get_crs_code


def test_get_crs_code():
    # test with a reversed code
    assert get_crs_code('EPSG:4326') == 4326
    assert get_crs_code('http://www.opengis.net/def/crs/EPSG/0/4326') == 4326
    assert get_crs_code('http://www.opengis.net/gml/srs/epsg.xml#4326') == 4326
    assert get_crs_code('urn:EPSG:geographicCRS:4326') == 4326
    assert get_crs_code('urn:ogc:def:crs:EPSG::4326') == 4326
    assert get_crs_code('urn:ogc:def:crs:EPSG:4326') == 4326
    assert get_crs_code('urn:ogc:def:crs:OGC::CRS84') == 'CRS84'

    # test with some garbage format
    with pytest.raises(ValueError):
        get_crs_code('abcd:4326')


def test_is_crs_yx():
    # test with a reversed code
    assert is_crs_yx('EPSG:4326')
    assert is_crs_yx('http://www.opengis.net/def/crs/EPSG/0/4326')
    assert is_crs_yx('http://www.opengis.net/gml/srs/epsg.xml#4326')
    assert is_crs_yx('urn:EPSG:geographicCRS:4326')
    assert is_crs_yx('urn:ogc:def:crs:EPSG::4326')
    assert is_crs_yx('urn:ogc:def:crs:EPSG:4326')

    # test with a non-reversed code
    assert is_crs_yx('EPSG:3857') is False
    assert is_crs_yx('http://www.opengis.net/def/crs/EPSG/0/3857') is False
    assert is_crs_yx('http://www.opengis.net/gml/srs/epsg.xml#3857') is False
    assert is_crs_yx('urn:EPSG:geographicCRS:3857') is False
    assert is_crs_yx('urn:ogc:def:crs:EPSG::3857') is False
    assert is_crs_yx('urn:ogc:def:crs:EPSG:3857') is False

    # test with some garbage format
    with pytest.raises(ValueError):
        is_crs_yx('abcd:4326')

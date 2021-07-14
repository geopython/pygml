import pytest

from pygml.axisorder import is_crs_yx


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

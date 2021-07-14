

from lxml import etree

from pygml.v32 import parse_v32
from pygml.geometry import Geometry


def test_parse_point():
    # basic test
    result = parse_v32(
        etree.fromstring("""
            <gml:Point gml:id="ID" xmlns:gml="http://www.opengis.net/gml/3.2">
                <gml:metaDataProperty>
                    <gml:GenericMetaData>Any text, intermingled with:
                        <!--any element-->
                    </gml:GenericMetaData>
                </gml:metaDataProperty>
                <gml:description>string</gml:description>
                <gml:descriptionReference/>
                <gml:identifier codeSpace="http://www.example.com/">string</gml:identifier>
                <gml:name>string</gml:name>
                <gml:pos>1.0 1.0</gml:pos>
            </gml:Point>
        """)
    )
    assert result == Geometry({'type': 'Point', 'coordinates': [1.0, 1.0]})

    #
    result = parse_v32(
        etree.fromstring("""
            <gml:Point gml:id="ID" xmlns:gml="http://www.opengis.net/gml/3.2">
                <gml:metaDataProperty>
                    <gml:GenericMetaData>Any text, intermingled with:
                        <!--any element-->
                    </gml:GenericMetaData>
                </gml:metaDataProperty>
                <gml:description>string</gml:description>
                <gml:descriptionReference/>
                <gml:identifier codeSpace="http://www.example.com/">string</gml:identifier>
                <gml:name>string</gml:name>
                <gml:coordinates>1.0 1.0</gml:coordinates>
            </gml:Point>
        """)
    )
    assert result == Geometry({'type': 'Point', 'coordinates': [1.0, 1.0]})

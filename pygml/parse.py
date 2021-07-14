from typing import Union
from lxml import etree

from .pre_v32 import parse_pre_v32
from .v32 import parse_v32
from .v33 import parse_v33_ce
from .geometry import Geometry


def parse(source: Union[etree._Element, str]) -> Geometry:
    """
    """

    if etree.iselement(source):
        element = source
    else:
        element = etree.fromstring(source)

    namespace = etree.QName(element.tag).namespace
    if namespace == 'http://www.opengis.net/gml':
        result = parse_pre_v32
    elif namespace == 'http://www.opengis.net/gml/3.2':
        result = parse_v32
    elif namespace == 'http://www.opengis.net/gml/3.3/ce':
        result = parse_v33_ce

    return Geometry(result)

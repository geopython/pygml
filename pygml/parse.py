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


from typing import Union
from lxml import etree

from .pre_v32 import parse_pre_v32
from .v32 import parse_v32
from .v33 import parse_v33_ce
from .types import Geometry


def parse(source: Union[etree._Element, str]) -> Geometry:
    """
    """

    if etree.iselement(source):
        element = source
    else:
        element = etree.fromstring(source)

    namespace = etree.QName(element.tag).namespace
    if namespace == 'http://www.opengis.net/gml':
        result = parse_pre_v32(element)
    elif namespace == 'http://www.opengis.net/gml/3.2':
        result = parse_v32(element)
    elif namespace == 'http://www.opengis.net/gml/3.3/ce':
        result = parse_v33_ce(element)

    return Geometry(result)

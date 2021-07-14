# pygml

A pure python parser for OGC GML Geometries.

[![PyPI version](https://badge.fury.io/py/pygml.svg)](https://badge.fury.io/py/pygml)
[![CI](https://github.com/geopython/pygml/actions/workflows/test.yaml/badge.svg)](https://github.com/geopython/pygml/actions/workflows/test.yaml)
[![Documentation Status](https://readthedocs.org/projects/pygml/badge/?version=latest)](https://pygml.readthedocs.io/en/latest/?badge=latest)

## Installation

```bash
$ pip install pygml
```

## Features

Parse GML 3.1, 3.2 and compact encoded GML 3.3 geometries to a [`__geo_interface__`](https://gist.github.com/sgillies/2217756) compliant class.


```python
>>> import pygml
>>> geom = pygml.parse("""
... <gml:Point gml:id="ID" xmlns:gml="http://www.opengis.net/gml/3.2">
...    <gml:pos>1.0 1.0</gml:pos>
... </gml:Point>
... """)
>>> print(geom)
Geometry(geometry={'type': 'Point', 'coordinates': [1.0, 1.0]})
>>> print(geom.__geo_interface__)
{'type': 'Point', 'coordinates': [1.0, 1.0]}
```

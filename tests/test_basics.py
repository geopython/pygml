import pytest

from pygml.basics import (
    parse_coordinates, parse_poslist, parse_pos, swap_coordinate_xy,
    swap_coordinates_xy
)


def test_parse_coordinates():
    # basic test
    result = parse_coordinates('12.34 56.7,89.10 11.12')
    assert result == [(12.34, 56.7), (89.10, 11.12)]

    # ignore some whitespace
    result = parse_coordinates('12.34 56.7,  89.10 11.12')
    assert result == [(12.34, 56.7), (89.10, 11.12)]

    # custom cs
    result = parse_coordinates('12.34 56.7;89.10 11.12', cs=';')
    assert result == [(12.34, 56.7), (89.10, 11.12)]

    # custom ts
    result = parse_coordinates('12.34:56.7,89.10:11.12', ts=':')
    assert result == [(12.34, 56.7), (89.10, 11.12)]

    # custom cs/ts
    result = parse_coordinates('12.34:56.7;89.10:11.12', cs=';', ts=':')
    assert result == [(12.34, 56.7), (89.10, 11.12)]

    # custom cs/ts and decimal
    result = parse_coordinates(
        '12,34:56,7;89,10:11,12', cs=';', ts=':', decimal=','
    )
    assert result == [(12.34, 56.7), (89.10, 11.12)]


def test_parse_poslist():
    # basic test
    result = parse_poslist('12.34 56.7 89.10 11.12')
    assert result == [(12.34, 56.7), (89.10, 11.12)]

    # 3D coordinates
    result = parse_poslist('12.34 56.7 89.10 11.12 13.14 15.16', dimensions=3)
    assert result == [(12.34, 56.7, 89.10), (11.12, 13.14, 15.16)]

    # exception on wrong dimensionality
    with pytest.raises(ValueError):
        parse_poslist('12.34 56.7 89.10 11.12', dimensions=3)


def test_parse_pos():
    # basic test
    result = parse_pos('12.34 56.7')
    assert result == (12.34, 56.7)

    # 3D pos
    result = parse_pos('12.34 56.7 89.10')
    assert result == (12.34, 56.7, 89.10)


def test_swap_coordinate_xy():
    # basic test
    swapped = swap_coordinate_xy((12.34, 56.7))
    assert swapped == (56.7, 12.34)

    # 3D coords, only X/Y are to be swapped
    swapped = swap_coordinate_xy((12.34, 56.7, 89.10))
    assert swapped == (56.7, 12.34, 89.10)


def test_swap_coordinates_xy():
    # basic test
    swapped = swap_coordinates_xy(
        [(12.34, 56.7), (89.10, 11.12)]
    )
    assert swapped == [(56.7, 12.34), (11.12, 89.10)]

    # 3D coords, only X/Y are to be swapped
    swapped = swap_coordinates_xy(
        [(12.34, 56.7, 89.10), (11.12, 13.14, 15.16)]
    )
    assert swapped == [(56.7, 12.34, 89.10), (13.14, 11.12, 15.16)]

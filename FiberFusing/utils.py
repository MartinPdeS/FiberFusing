#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Built-in imports
import numpy
from collections.abc import Iterable
from itertools import combinations

# Other imports
from FiberFusing import buffer
from shapely.ops import unary_union
from shapely.ops import nearest_points
import shapely.geometry as geo
from matplotlib.path import Path


def get_silica_index(wavelength: float):
    # From https://refractiveindex.info/?shelf=main&book=SiO2&page=Malitson

    wavelength *= 1e6  # Put into micro-meter scale

    A_numerator = 0.6961663
    A_denominator = 0.0684043

    B_numerator = 0.4079426
    B_denominator = 0.1162414

    C_numerator = 0.8974794
    C_denominator = 9.896161

    index = (A_numerator * wavelength**2) / (wavelength**2 - A_denominator**2)
    index += (B_numerator * wavelength**2) / (wavelength**2 - B_denominator**2)
    index += (C_numerator * wavelength**2) / (wavelength**2 - C_denominator**2)
    index += 1
    index = numpy.sqrt(index)

    return index


def NearestPoints(Object0, Object1):
    if hasattr(Object0, '_shapely_object'):
        Object0 = Object0._shapely_object

    if hasattr(Object0, '_shapely_object'):
        Object1 = Object1._shapely_object

    P = nearest_points(Object0.exterior, Object1.exterior)

    return buffer.Point(position=(P[0].x, P[0].y))


def Union(*Objects):
    if len(Objects) == 0:
        return buffer.Polygon(instance=geo.Polygon())

    Objects = [o._shapely_object if hasattr(o, '_shapely_object') else o for o in Objects]
    output = unary_union(Objects)

    return buffer.Polygon(instance=output)


def Intersection(*Objects):
    if len(Objects) == 0:
        return buffer.Polygon(instance=geo.Polygon())

    Objects = [o._shapely_object if hasattr(o, '_shapely_object') else o for o in Objects]

    intersection = unary_union(
        [a.intersection(b) for a, b in combinations(Objects, 2)]
    )

    return buffer.Polygon(instance=intersection)


def interpret_to_tuple(*args):
    args = tuple(arg if isinstance(arg, Iterable) else tuple(arg.x, arg.y) for arg in args)

    if len(args) == 1:
        return args[0]
    return args


def interpret_to_point(*args):
    args = tuple(arg if isinstance(arg, buffer.Point) else buffer.Point(position=arg) for arg in args)

    if len(args) == 1:
        return args[0]
    return args


def ring_coding(ob) -> numpy.ndarray:
    n = len(ob.coords)
    codes = numpy.ones(n, dtype=Path.code_type) * Path.LINETO
    codes[0] = Path.MOVETO
    return codes


def pathify(polygon) -> Path:
    """
    Return path of a polygone that may have holes in it

    :param      polygon:         The polygon
    :type       polygon:         { type_description }

    :returns:   The path of the polygon
    :rtype:     Path

    :raises     AssertionError:  { exception_description }
    """
    vertices = numpy.concatenate(
        [numpy.asarray(polygon.exterior)] + [numpy.asarray(r) for r in polygon.interiors])

    codes = numpy.concatenate(
        [ring_coding(polygon.exterior)] + [ring_coding(r) for r in polygon.interiors])

    return Path(vertices, codes)

# -

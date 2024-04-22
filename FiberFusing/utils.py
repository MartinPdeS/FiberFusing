#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy
from collections.abc import Iterable
from itertools import combinations

import FiberFusing as ff
from shapely.ops import unary_union
from shapely.ops import nearest_points
import shapely.geometry as geo
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from matplotlib.collections import PatchCollection


def get_silica_index(wavelength: float) -> float:
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


def NearestPoints(object0, object1) -> ff.Point:
    """
    Finds the nearest points between two geometric objects' exteriors.

    If the objects have a '_shapely_object' attribute, that is used as the shapely representation.

    :param object0: The first geometric object or an object with a '_shapely_object' attribute.
    :param object1: The second geometric object or an object with a '_shapely_object' attribute.
    :return: A ff.Point containing the coordinates of the nearest point on the first object to the second object.
    """
    if hasattr(object0, '_shapely_object'):
        object0 = object0._shapely_object
    if hasattr(object1, '_shapely_object'):
        object1 = object1._shapely_object

    # Calculate nearest points on the exterior of the objects
    p = nearest_points(object0.exterior, object1.exterior)[0]

    return ff.Point(position=(p.x, p.y))


def Union(*objects) -> ff.Polygon:
    """
    Computes the union of multiple geometric objects using the unary union operation.

    :param objects: A variable number of shapely geometric objects or objects with a '_shapely_object' attribute.
    :return: A ff.Polygon containing the union of all provided objects.
    """
    if not objects:
        return ff.Polygon(instance=geo.Polygon())

    # Ensure all objects are shapely objects, falling back to '_shapely_object' attribute if present
    shapely_objects = [o._shapely_object if hasattr(o, '_shapely_object') else o for o in objects]
    result = unary_union(shapely_objects)

    return ff.Polygon(instance=result)


def Intersection(*objects) -> ff.Polygon:
    """
    Computes the intersection of multiple geometric objects, specifically the pairwise intersection across all objects.

    :param objects: A variable number of shapely geometric objects or custom objects with a '_shapely_object' attribute.
    :return: A ff.Polygon containing the intersection of all provided objects.
    """
    if not objects:
        return ff.Polygon()

    # Ensure all objects are shapely objects, falling back to '_shapely_object' attribute if present
    shapely_objects = [o._shapely_object if hasattr(o, '_shapely_object') else o for o in objects]

    # Compute pairwise intersections
    intersection_result = unary_union(
        [a.intersection(b) for a, b in combinations(shapely_objects, 2)]
    )

    return ff.Polygon(instance=intersection_result)


def interpret_to_tuple(*args):
    """
    Converts a sequence of arguments to a tuple, interpreting non-iterable items as (x, y) tuples if they have 'x' and 'y' attributes.

    :param args: A variable number of arguments that may be iterables or objects with 'x' and 'y' attributes.
    :return: A tuple of tuples, each corresponding to an input argument.
    """
    result = tuple(arg if isinstance(arg, Iterable) else (arg.x, arg.y) for arg in args)
    return result[0] if len(result) == 1 else result


def interpret_to_point(*args):
    """
    Converts a sequence of arguments to ff.Point objects, interpreting each as a point.

    :param args: A variable number of arguments that may be either ff.Point instances or tuples for positions.
    :return: A tuple of ff.Point instances, each corresponding to an input argument.
    """
    result = tuple(arg if isinstance(arg, ff.Point) else ff.Point(position=arg) for arg in args)
    return result[0] if len(result) == 1 else result


def ring_coding(ob) -> numpy.ndarray:
    """
    Generates the coding for vertices in a path representation of a geometric object.

    :param ob: A geometric object with coordinates.
    :return: An array of matplotlib path codes for the object's vertices.
    """
    n = len(ob.coords)
    codes = numpy.ones(n, dtype=Path.code_type) * Path.LINETO
    codes[0] = Path.MOVETO
    return codes


def pathify(polygon) -> Path:
    """
    Constructs a Matplotlib Path object from a polygon with potential holes.

    This function takes a polygon that may include holes and converts it into a Path object
    that can be used for plotting or geometric analysis. The path includes both exterior boundaries
    and any interior boundaries (holes).

    :param polygon: The polygon to convert, expected to have 'exterior' and 'interiors' attributes.
    :type polygon: a type with attributes 'exterior' and 'interiors' that return sequences of coordinates

    :returns: A Path object representing the polygon with its holes.
    :rtype: matplotlib.path.Path

    :raises AssertionError: If the input polygon does not have the expected attributes.
    """
    # Validate the polygon input for the necessary attributes
    assert hasattr(polygon, 'exterior') and hasattr(polygon, 'interiors'), "Input must be a polygon-like object with 'exterior' and 'interiors'."

    # Prepare vertices and codes for the Path
    vertices = numpy.concatenate(
        [numpy.asarray(polygon.exterior)] + [numpy.asarray(hole) for hole in polygon.interiors])
    codes = numpy.concatenate(
        [ring_coding(polygon.exterior)] + [ring_coding(hole) for hole in polygon.interiors])

    return Path(vertices, codes)


def plot_polygon(ax, poly, **kwargs):
    path = Path.make_compound_path(
        Path(numpy.asarray(poly.exterior.coords)[:, :2]),
        *[Path(numpy.asarray(ring.coords)[:, :2]) for ring in poly.interiors])

    patch = PathPatch(path, **kwargs)
    collection = PatchCollection([patch], **kwargs)

    ax.add_collection(collection, autolim=True)
    ax.autoscale_view()
    return collection

# -

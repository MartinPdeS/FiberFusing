#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Iterable, Union, List
import shapely.geometry as geo
from shapely.ops import unary_union

from FiberFusing import geometries


def get_polygon_union(*objects) -> geometries.Polygon:
    """
    Computes the union of multiple geometric objects and returns the resulting Polygon.

    Args:
        objects: Variable length argument list of geometric objects.
                 Each object can be a shapely geometry object or an instance with a `_shapely_object` attribute.

    Returns:
        Polygon: A new Polygon instance representing the union of the input objects.
                 If no objects are provided, an empty Polygon is returned.
    """
    if len(objects) == 0:
        return geometries.Polygon(instance=geo.Polygon())

    objects = [o._shapely_object if hasattr(o, '_shapely_object') else o for o in objects]
    output = unary_union(objects)

    return geometries.Polygon(instance=output)


def interpret_to_point(*args: Union[geometries.Point, Iterable, geo.Point]) -> Union[geometries.Point, List[geometries.Point]]:
    """
    Converts various input formats to Point instances.

    Args:
        args: Variable length argument list of inputs to be interpreted as Points.
              Each argument can be an instance of Point, an Iterable representing coordinates, or a shapely.geometry.Point.

    Returns:
        Union[Point, List[Point]]: A single Point instance if only one argument is provided,
                                   otherwise a list of Point instances.
    """
    output = []

    for arg in args:
        if isinstance(arg, geometries.Point):
            output.append(arg)
        elif isinstance(arg, Iterable):
            output.append(geometries.Point(position=arg))
        elif isinstance(arg, geo.Point):
            output.append(geometries.Point(instance=arg))

    if len(output) == 1:
        return output[0]

    return output

# -

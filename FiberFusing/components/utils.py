#!/usr/bin/env python
# -*- coding: utf-8 -*-

from FiberFusing.components.point import Point
from FiberFusing.components.polygon import Polygon
import shapely.geometry as geo
from shapely.ops import unary_union


def get_polygon_union(*objects):
    if len(objects) == 0:
        return Polygon(instance=geo.Polygon())

    objects = [o._shapely_object if hasattr(o, '_shapely_object') else o for o in objects]
    output = unary_union(objects)

    return Polygon(instance=output)


def interpret_to_point(*args):
    args = tuple(
        arg if isinstance(arg, Point) else Point(position=arg) for arg in args
    )

    if len(args) == 1:
        return args[0]

    return args

# -

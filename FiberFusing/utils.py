from collections.abc import Iterable
from itertools import combinations
import FiberFusing as ff
from shapely.ops import unary_union, nearest_points
import shapely.geometry as geo


def nearest_points_exterior(object0, object1) -> ff.Point:
    """
    Find the nearest points between the exteriors of two geometric objects.

    Parameters
    ----------
    object0 : shapely.geometry or object
        The first geometric object or an object with a '_shapely_object' attribute.
    object1 : shapely.geometry or object
        The second geometric object or an object with a '_shapely_object' attribute.

    Returns
    -------
    ff.Point
        A Point containing the coordinates of the nearest point on the first object to the second.
    """
    object0 = object0._shapely_object if hasattr(object0, '_shapely_object') else object0
    object1 = object1._shapely_object if hasattr(object1, '_shapely_object') else object1

    nearest_point = nearest_points(object0.exterior, object1.exterior)[0]
    return ff.Point(position=(nearest_point.x, nearest_point.y))


def union_geometries(*objects) -> ff.Polygon:
    """
    Compute the union of multiple geometric objects.

    Parameters
    ----------
    objects : shapely.geometry or object
        A variable number of shapely geometric objects or objects with a '_shapely_object' attribute.

    Returns
    -------
    ff.Polygon
        A Polygon containing the union of all provided objects.
    """
    if not objects:
        return ff.Polygon(instance=geo.Polygon())

    shapely_objects = [o._shapely_object if hasattr(o, '_shapely_object') else o for o in objects]
    union_result = unary_union(shapely_objects)
    return ff.Polygon(instance=union_result)


def intersection_geometries(*objects) -> ff.Polygon:
    """
    Compute the intersection of multiple geometric objects.

    Parameters
    ----------
    objects : shapely.geometry or object
        A variable number of shapely geometric objects or objects with a '_shapely_object' attribute.

    Returns
    -------
    ff.Polygon
        A Polygon containing the intersection of all provided objects.
    """
    if not objects:
        return ff.Polygon()

    shapely_objects = [o._shapely_object if hasattr(o, '_shapely_object') else o for o in objects]
    intersection_result = unary_union([a.intersection(b) for a, b in combinations(shapely_objects, 2)])
    return ff.Polygon(instance=intersection_result)


def interpret_to_tuple(*args):
    """
    Convert arguments to tuples, interpreting non-iterable items with 'x' and 'y' attributes as (x, y) tuples.

    Parameters
    ----------
    args : variable
        Arguments that may be iterables or objects with 'x' and 'y' attributes.

    Returns
    -------
    tuple
        A tuple of tuples, each corresponding to an input argument.
    """
    result = tuple(arg if isinstance(arg, Iterable) else (arg.x, arg.y) for arg in args)
    return result[0] if len(result) == 1 else result


def interpret_to_point(*args):
    """
    Convert arguments to ff.Point objects.

    Parameters
    ----------
    args : variable
        Arguments that may be either ff.Point instances or tuples for positions.

    Returns
    -------
    tuple or ff.Point
        A tuple of ff.Point instances or a single ff.Point if only one argument is provided.
    """
    result = tuple(arg if isinstance(arg, ff.Point) else ff.Point(position=arg) for arg in args)
    return result[0] if len(result) == 1 else result

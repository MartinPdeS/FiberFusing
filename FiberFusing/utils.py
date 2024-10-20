import numpy as np
from collections.abc import Iterable
from itertools import combinations
import FiberFusing as ff
from shapely.ops import unary_union, nearest_points
import shapely.geometry as geo
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from matplotlib.collections import PatchCollection


def get_silica_index(wavelength: float) -> float:
    """
    Calculate the refractive index of silica using the Sellmeier equation.

    Parameters
    ----------
    wavelength : float
        The wavelength in meters.

    Returns
    -------
    float
        The refractive index of silica at the given wavelength.
    """
    wavelength_um = wavelength * 1e6  # Convert to micrometers

    A_numerator, A_denominator = 0.6961663, 0.0684043
    B_numerator, B_denominator = 0.4079426, 0.1162414
    C_numerator, C_denominator = 0.8974794, 9.896161

    index = (
        (A_numerator * wavelength_um**2) / (wavelength_um**2 - A_denominator**2) +
        (B_numerator * wavelength_um**2) / (wavelength_um**2 - B_denominator**2) +
        (C_numerator * wavelength_um**2) / (wavelength_um**2 - C_denominator**2) + 1
    )
    return np.sqrt(index)


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


def ring_coding(geometry) -> np.ndarray:
    """
    Generate coding for vertices in a path representation of a geometric object.

    Parameters
    ----------
    geometry : shapely.geometry
        A geometric object with coordinates.

    Returns
    -------
    np.ndarray
        An array of matplotlib path codes for the object's vertices.
    """
    n_coords = len(geometry.coords)
    codes = np.full(n_coords, Path.LINETO, dtype=Path.code_type)
    codes[0] = Path.MOVETO
    return codes


def pathify(polygon) -> Path:
    """
    Construct a Matplotlib Path object from a polygon with potential holes.

    Parameters
    ----------
    polygon : shapely.geometry.Polygon
        The polygon to convert, expected to have 'exterior' and 'interiors' attributes.

    Returns
    -------
    Path
        A Path object representing the polygon with its holes.

    Raises
    ------
    AssertionError
        If the input polygon does not have the expected attributes.
    """
    assert hasattr(polygon, 'exterior') and hasattr(polygon, 'interiors'), \
        "Input must be a polygon-like object with 'exterior' and 'interiors'."

    vertices = np.concatenate([np.asarray(polygon.exterior)] + [np.asarray(hole) for hole in polygon.interiors])
    codes = np.concatenate([ring_coding(polygon.exterior)] + [ring_coding(hole) for hole in polygon.interiors])

    return Path(vertices, codes)


def plot_polygon(ax, poly, **kwargs):
    """
    Plot a polygon on a given matplotlib axis.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axis on which to plot the polygon.
    poly : shapely.geometry.Polygon
        The polygon object containing the exterior and interior coordinates.
    **kwargs : dict
        Additional keyword arguments passed to `PathPatch` and `PatchCollection`.

    Returns
    -------
    PatchCollection
        The collection of patches added to the axis.
    """
    exterior_path = Path(np.asarray(poly.exterior.coords)[:, :2])
    interior_paths = [Path(np.asarray(ring.coords)[:, :2]) for ring in poly.interiors]
    compound_path = Path.make_compound_path(exterior_path, *interior_paths)

    patch = PathPatch(compound_path, **kwargs)
    collection = PatchCollection([patch], **kwargs)

    ax.add_collection(collection, autolim=True)
    ax.autoscale_view()
    return collection

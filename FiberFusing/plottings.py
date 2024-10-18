import numpy as np
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from matplotlib.collections import PatchCollection


def plot_polygon(ax, poly, alpha=0.3, **kwargs):
    """
    Plots a polygon on a given matplotlib axis.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axis on which to plot the polygon.
    poly : shapely.geometry.Polygon
        The polygon object containing the exterior and interior coordinates.
    alpha : float, optional
        The transparency level of the polygon fill. Default is 0.3.
    **kwargs : dict, optional
        Additional keyword arguments passed to `PathPatch` and `PatchCollection`.

    Returns
    -------
    PatchCollection
        The collection of patches added to the axis.
    """
    # Create the exterior path
    exterior_path = Path(np.asarray(poly.exterior.coords)[:, :2])

    # Create paths for each interior ring
    interior_paths = [Path(np.asarray(ring.coords)[:, :2]) for ring in poly.interiors]

    # Combine the exterior and interior paths into a compound path
    compound_path = Path.make_compound_path(exterior_path, *interior_paths)

    # Create the path patch and patch collection
    patch = PathPatch(compound_path, **kwargs)
    collection = PatchCollection([patch], alpha=alpha, **kwargs)

    # Add the patch collection to the axis and update the view
    ax.add_collection(collection, autolim=True)
    ax.autoscale_view()

    return collection

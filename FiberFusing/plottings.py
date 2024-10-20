import numpy as np
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from matplotlib.collections import PatchCollection


def plot_polygon(ax, poly, alpha=0.3, scale_factor=1, **kwargs):
    """
    Plots a polygon on a given matplotlib axis with x and y axes scaled by a factor.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        The axis on which to plot the polygon.
    poly : shapely.geometry.Polygon
        The polygon object containing the exterior and interior coordinates.
    alpha : float, optional
        The transparency level of the polygon fill. Default is 0.3.
    scale_factor : float, optional
        The factor by which to scale the x and y coordinates. Default is 100.
    **kwargs : dict, optional
        Additional keyword arguments passed to `PathPatch` and `PatchCollection`.

    Returns
    -------
    PatchCollection
        The collection of patches added to the axis.
    """
    # Scale the exterior coordinates
    exterior_coords = np.asarray(poly.exterior.coords)[:, :2] * scale_factor
    exterior_path = Path(exterior_coords)

    # Scale each interior ring's coordinates
    interior_paths = [Path(np.asarray(ring.coords)[:, :2] * scale_factor) for ring in poly.interiors]

    # Combine the exterior and interior paths into a compound path
    compound_path = Path.make_compound_path(exterior_path, *interior_paths)

    # Create the path patch and patch collection
    patch = PathPatch(compound_path, **kwargs)
    collection = PatchCollection([patch], alpha=alpha, **kwargs)

    # Add the patch collection to the axis and update the view
    ax.add_collection(collection, autolim=True)
    ax.autoscale_view()

    return collection

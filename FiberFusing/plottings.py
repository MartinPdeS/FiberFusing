import numpy as np
import matplotlib.pyplot as plt
import shapely.geometry as geo
from matplotlib.patches import Polygon as MplPolygon


def plot_polygon(ax: plt.Axes, polygon: geo.base.BaseGeometry, facecolor: str = 'lightblue', alpha: float = 0.5, **kwargs):
    """
    Plots a filled polygon or multipolygon, handling any holes on the given Matplotlib axis.

    Parameters
    ----------
    polygon : geo.base.BaseGeometry
        The polygon or multipolygon to plot.
    ax : plt.Axes, optional
        The Matplotlib axis where the polygon should be plotted. If None, a new figure and axis will be created.
    **kwargs
        Additional keyword arguments passed to the plot function (e.g., facecolor, edgecolor, alpha).
    """
    # Function to add a single polygon to the axis
    def add_polygon_to_ax(polygon_obj):
        # Plot the exterior as a filled polygon
        exterior_coords = np.array(polygon_obj.exterior.coords)
        exterior_patch = MplPolygon(exterior_coords, facecolor=facecolor, edgecolor='black', alpha=alpha, **kwargs)
        ax.add_patch(exterior_patch)

        # Plot each hole (interior) as another polygon with the background color (transparent effect)
        for interior in polygon_obj.interiors:
            hole_coords = np.array(interior.coords)
            hole_patch = MplPolygon(hole_coords, facecolor='white', edgecolor='black', alpha=1)
            ax.add_patch(hole_patch)

    # Check if the geometry is a MultiPolygon or a single Polygon
    if isinstance(polygon, geo.MultiPolygon):
        for poly in polygon.geoms:
            add_polygon_to_ax(poly)
    elif isinstance(polygon, geo.Polygon):
        add_polygon_to_ax(polygon)
    else:
        raise TypeError("Input geometry must be a Polygon or MultiPolygon.")

    ax.autoscale_view()
    ax.set_aspect('equal', 'box')

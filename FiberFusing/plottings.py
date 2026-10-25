import numpy as np
import matplotlib.pyplot as plt
import shapely.geometry as geo
from matplotlib.patches import Polygon as MplPolygon


def plot_polygon(
    ax: plt.Axes,
    polygon: geo.base.BaseGeometry,
    facecolor: str = "lightblue",
    alpha: float = 0.5,
    **kwargs,
):
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
        exterior_patch = MplPolygon(
            exterior_coords, facecolor=facecolor, edgecolor="black", alpha=alpha, **kwargs
        )
        ax.add_patch(exterior_patch)

        # Plot each hole (interior) as another polygon with the background color (transparent effect)
        for interior in polygon_obj.interiors:
            hole_coords = np.array(interior.coords)
            hole_patch = MplPolygon(hole_coords, facecolor="white", edgecolor="black", alpha=1)
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
    ax.set_aspect("equal", "box")


def plotting(nrows=1, ncols=1, *, subplot_kw=None, gridspec_kw=None, sharex=False, sharey=False):
    """Give a plotting method Matplotlib axes and return its figure.

    Parameters
    ----------
    nrows, ncols : int, optional
        Required subplot layout. Methods receive one Axes or a flat axes array.
    subplot_kw, gridspec_kw : dict, optional
        Arguments used only when creating new axes.
    sharex, sharey : bool, optional
        Axis sharing passed to Matplotlib when creating new axes.

    Returns
    -------
    callable
        Decorator accepting ``axes``, ``show``, ``save_as``, ``figure_size``,
        ``tight_layout``, ``style``, ``xscale``, ``yscale``, ``xlim``, and ``ylim``.
        Existing show-by-default behavior is preserved; use ``show=False`` in
        scripts. Styles are scoped to the call, with no external style package.
    """
    from functools import wraps

    def decorate(function):
        @wraps(function)
        def wrapped(
            *args,
            axes=None,
            show=True,
            save_as=None,
            figure_size=None,
            tight_layout=True,
            style=None,
            xscale=None,
            yscale=None,
            xlim=None,
            ylim=None,
            **kwargs,
        ):
            with plt.style.context(style) if style is not None else plt.rc_context():
                created = axes is None
                if created:
                    figure, axes = plt.subplots(
                        nrows=nrows,
                        ncols=ncols,
                        squeeze=False,
                        figsize=figure_size,
                        subplot_kw=subplot_kw,
                        gridspec_kw=gridspec_kw,
                        sharex=sharex,
                        sharey=sharey,
                    )
                axis_list = np.asarray(axes, dtype=object).reshape(-1)
                if len(axis_list) != nrows * ncols:
                    if created:
                        plt.close(figure)
                    raise ValueError(f"Expected {nrows * ncols} axes, received {len(axis_list)}")
                if not all(isinstance(axis, plt.Axes) for axis in axis_list):
                    raise TypeError("axes must contain Matplotlib Axes objects")
                figure = axis_list[0].get_figure()
                if any(axis.get_figure() is not figure for axis in axis_list):
                    raise ValueError("All axes must belong to the same figure")
                try:
                    function(
                        *args, axes=axis_list[0] if len(axis_list) == 1 else axis_list, **kwargs
                    )
                    for axis in axis_list:
                        if xscale is not None:
                            axis.set_xscale(xscale)
                        if yscale is not None:
                            axis.set_yscale(yscale)
                        if xlim is not None:
                            axis.set_xlim(xlim)
                        if ylim is not None:
                            axis.set_ylim(ylim)
                    if figure_size is not None:
                        figure.set_size_inches(*figure_size)
                    if tight_layout:
                        figure.tight_layout()
                    if save_as is not None:
                        figure.savefig(save_as, dpi=300)
                    if show:
                        plt.show()
                    return figure
                except Exception:
                    if created:
                        plt.close(figure)
                    raise

        return wrapped

    return decorate

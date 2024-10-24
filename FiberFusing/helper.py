import numpy
from MPSPlots.styles import mps
import matplotlib.pyplot as plt


def _plot_helper(function):
    def wrapper(self, ax: plt.Axes = None, show: bool = True, **kwargs):
        if ax is None:
            with plt.style.context(mps):
                _, ax = plt.subplots(1, 1)
                ax.set_aspect('equal')
                ax.set(title='Fiber structure', xlabel=r'x-distance [m]', ylabel=r'y-distance [m]')
                ax.ticklabel_format(axis='both', style='sci')  # , scilimits=(-6, -6), useOffset=False)

        function(self, ax=ax, **kwargs)

        _, labels = ax.get_legend_handles_labels()

        # Only add a legend if there are labels
        if labels:
            ax.legend()

        if show:
            plt.show()

    return wrapper


class OverlayStructureBaseClass:
    def _overlay_structure_on_mesh_(self, structure_list: dict, mesh: numpy.ndarray, coordinate_system: object) -> numpy.ndarray:
        """
        Return a mesh overlaying all the structures in the order they were defined.

        :param      coordinate_system:  The coordinates axis
        :type       coordinate_system:  Axis

        :returns:   The raster mesh of the structures.
        :rtype:     numpy.ndarray
        """
        for structure in structure_list:
            polygon = structure.polygon
            raster = polygon.get_rasterized_mesh(coordinate_system=coordinate_system)
            mesh[numpy.where(raster != 0)] = 0
            index = structure.index

            if hasattr(structure, 'graded_index_factor'):
                index += self.get_graded_index_mesh(
                    coordinate_system=coordinate_system,
                    polygon=polygon,
                    delta_n=structure.graded_index_factor
                )

            raster *= index

            mesh += raster

        return mesh

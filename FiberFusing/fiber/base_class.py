#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy
from dataclasses import dataclass
from FiberFusing import Circle
from FiberFusing.tools import plot_style
from FiberFusing.coordinate_system import CoordinateSystem
from FiberFusing.utils import get_silica_index
from MPSTools.tools.mathematics import get_rho_gradient
from FiberFusing import CircleOpticalStructure
import pprint
from copy import deepcopy

# MPSPlots imports
from matplotlib import colors
from MPSPlots import colormaps
from MPSPlots.render2D import SceneList, Axis, Polygon

pp = pprint.PrettyPrinter(indent=4, sort_dicts=False, compact=True, width=1)


class BaseStructureCollection():
    @property
    def full_structure(self):
        return self.structure_list

    @property
    def fiber_structure(self):
        return [s for s in self.structure_list if s.name not in ['air']]

    @property
    def refractive_index_list(self) -> list:
        return [struct.index for struct in self.fiber_structure]

    @property
    def inner_structure(self):
        return [s for s in self.structure_list if s.name not in ['air', 'outer_clad']]

    def __getitem__(self, idx: int) -> CircleOpticalStructure:
        return self.structure_list[idx]

    def scale(self, factor: float) -> None:
        """
        Return a scaled version of the fiber.

        :param      factor:  The scaling factor
        :type       factor:  float

        :returns:   No return
        :rtype:     None
        """
        fiber_copy = deepcopy(self)
        for structure in fiber_copy.structure_list:
            if structure.radius is None:
                continue

            structure.radius *= factor

            new_polygon = Circle(
                position=structure.position,
                radius=structure.radius,
                index=structure.index
            )

            structure.polygon = new_polygon

        return fiber_copy

    def create_and_add_new_structure(self, index: float = None, NA: float = None, **kwargs) -> None:
        """
        Add a new circular structure following the previously defined.
        This structure is defined with a name, numerical aperture, and radius.

        :param      name:    The name of the structure
        :type       name:    str
        :param      NA:      The numerical aperture of the structure
        :type       NA:      float
        :param      radius:  The radius of the circular structure
        :type       radius:  float

        :returns:   No returns
        :rtype:     None
        """
        index = self._interpret_index_or_NA_to_index(index=index, NA=NA)

        new_structure = CircleOpticalStructure(
            **kwargs,
            index=index,
            position=self.position
        )

        setattr(self, new_structure.name, new_structure)

        self.structure_list.append(new_structure)

    def _interpret_index_or_NA_to_index(self, index: float, NA: float) -> float:
        assert (index is None) ^ (NA is None), 'Only NA or index can be defined'

        if index is not None:
            return index

        if (NA is not None) and len(self.structure_list) == 0:
            raise ValueError('Cannot initialize layer from NA if no previous layer is defined')

        index = self.compute_index_from_NA(
            exterior_index=self.structure_list[-1].index,
            NA=NA
        )

        return index

    def compute_index_from_NA(self, exterior_index: float, NA: float) -> float:
        index = numpy.sqrt(NA**2 + exterior_index**2)

        return index

    def _overlay_structure_on_mesh_(self, structure_list: list, mesh: numpy.ndarray, coordinate_system: CoordinateSystem) -> numpy.ndarray:
        """
        Return a mesh overlaying all the structures in the order they were defined.

        :param      coordinate_system:  The coordinates axis
        :type       coordinate_system:  CoordinateSystem

        :returns:   The raster mesh of the structures.
        :rtype:     numpy.ndarray
        """
        for structure in structure_list:
            raster = structure.polygon.get_rasterized_mesh(coordinate_system=coordinate_system)
            mesh[numpy.where(raster != 0)] = 0

            if structure.is_graded:
                index = self.get_graded_index_mesh(
                    coordinate_system=coordinate_system,
                    polygon=structure.polygon,
                    min_index=structure.index,
                    max_index=structure.index + structure.delta_n
                )

            else:
                index = structure.index

            mesh += raster * index

        return mesh


@dataclass
class GenericFiber(BaseStructureCollection):
    wavelength: float
    """ Wavelenght at which evaluate the computation """
    position: tuple = (0, 0)
    """ Position of the fiber """

    def __post_init__(self):
        self.structure_list = []
        self.add_air()

    @property
    def pure_silica_index(self):
        return get_silica_index(wavelength=self.wavelength)

    def set_position(self, position: tuple) -> None:
        for structure in self.structure_list:
            if structure.radius is None:
                continue

            structure.position = position

            new_polygon = Circle(
                position=structure.position,
                radius=structure.radius,
                index=structure.index
            )

            structure.polygon = new_polygon

    def update_wavelength(self, new_value: float) -> None:
        """
        Update the value of the wavelength for that specific fiber class

        :param      new_value:  The new wavelength value
        :type       new_value:  float

        :returns:   No returns
        :rtype:     None
        """
        self.wavelength = new_value
        self.__init__()

    def update_position(self, new_value: tuple) -> None:
        """
        Update the value of the position for that specific fiber class

        :param      new_value:  The new position value
        :type       new_value:  tuple

        :returns:   No returns
        :rtype:     None
        """
        self.position = new_value
        self.__init__()

    def NA_to_core_index(self, NA: float, index_clad: float) -> float:
        core_index = numpy.sqrt(NA**2 + index_clad**2)

        return core_index

    def core_index_to_NA(self, interior_index: float, exterior_index: float):
        NA = numpy.sqrt(interior_index**2 - exterior_index**2)

        return NA

    @property
    def polygones(self):
        if not self._polygones:
            self.initialize_polygones()
        return self._polygones

    def add_air(self, radius: float = 1e3):
        self.create_and_add_new_structure(
            name='air',
            index=1.0,
            radius=1.0,
        )

    def add_silica_pure_cladding(self, radius: float = 62.5e-6, name: str = 'outer_clad'):
        self.create_and_add_new_structure(
            name='outer_clad',
            index=self.pure_silica_index,
            radius=radius,
        )

    def render_patch_on_ax(self, ax: Axis) -> None:
        """
        Add the patch representation of the geometry into the given ax.

        :param      ax:   The ax to which append the representation.
        :type       ax:   Axis
        """
        for structure in self.fiber_structure:
            artist = Polygon(
                instance=structure.polygon._shapely_object
            )

            ax.add_artist(artist)

        ax.set_style(**plot_style.geometry, title='Fiber structure')

    def render_raster_on_ax(self, ax: Axis, structure, coordinate_system: CoordinateSystem) -> None:
        boolean_raster = structure.polygon.get_rasterized_mesh(coordinate_system=coordinate_system)

        ax.add_mesh(
            x=coordinate_system.x_vector,
            y=coordinate_system.y_vector,
            scalar=boolean_raster,
            colormap='Blues'
        )

    def render_mesh_on_ax(self, ax: Axis, coordinate_system: CoordinateSystem):
        """
        Add the rasterized representation of the geometry into the given ax.

        :param      ax:   The ax to which append the representation.
        :type       ax:   Axis
        """

        ax.add_colorbar(
            discreet=False,
            position='right',
            numeric_format='%.4f'
        )

        raster = self.overlay_structures(coordinate_system=coordinate_system, structures_type='fiber_structure')

        artist = ax.add_mesh(
            x=coordinate_system.x_vector,
            y=coordinate_system.y_vector,
            scalar=raster,
        )

        ax.add_colorbar(
            artist=artist,
            colormap='Blues',
            norm=colors.LogNorm()
        )

        ax.set_style(**plot_style.geometry, title='Rasterized mesh')

    def render_gradient_on_ax(self, ax: Axis, coordinate_system: CoordinateSystem) -> None:
        """
        Add the rasterized representation of the gradient of the geometrys into the give ax.

        :param      ax:   The ax to which append the representation.
        :type       ax:   Axis
        """
        raster = self.overlay_structures(coordinate_system=coordinate_system, structures_type='fiber_structure')

        rho_gradient = get_rho_gradient(mesh=raster, coordinate_system=coordinate_system)

        artist = ax.add_mesh(
            x=coordinate_system.x_vector,
            y=coordinate_system.y_vector,
            scalar=rho_gradient,
        )

        ax.add_colorbar(
            artist=artist,
            colormap=colormaps.blue_white_red,
            norm=colors.SymLogNorm(linthresh=1e-10)
        )

        ax.set_style(**plot_style.geometry, title='Refractive index gradient')

    def shift_coordinates(self, coordinate_system: CoordinateSystem, x_shift: float, y_shift: float) -> numpy.ndarray:
        """
        Return the same coordinate system but x-y shifted

        :param      coordinates:  The coordinates
        :type       coordinates:  numpy.ndarray
        :param      x_shift:      The x shift
        :type       x_shift:      float
        :param      y_shift:      The y shift
        :type       y_shift:      float

        :returns:   The shifted coordinate
        :rtype:     numpy.ndarray
        """
        shifted_coordinate = coordinate_system.to_unstructured_coordinate()
        shifted_coordinate[:, 0] -= x_shift
        shifted_coordinate[:, 1] -= y_shift

        return shifted_coordinate

    def get_shifted_distance_mesh(self, coordinate_system: Axis, x_position: float, y_position: float, into_mesh: bool = True) -> numpy.ndarray:
        """
        Returns a mesh representing the distance from a specific point.

        :param      coordinate_system:  The coordinate axis
        :type       coordinate_system:  Axis
        :param      x_postition:      The x shift
        :type       x_position:       float
        :param      y_position:       The y shift
        :type       y_position:       float
        :param      into_mesh:        Into mesh
        :type       into_mesh:        bool

        :returns:   The shifted distance mesh.
        :rtype:     { return_type_description }
        """
        shifted_coordinate = self.shift_coordinates(
            coordinate_system=coordinate_system,
            x_shift=x_position,
            y_shift=y_position
        )

        distance = numpy.sqrt(shifted_coordinate[:, 0]**2 + shifted_coordinate[:, 1]**2)

        if into_mesh:
            distance = distance.reshape(coordinate_system.shape)

        return distance

    def get_graded_index_mesh(self, coordinate_system: numpy.ndarray, polygon, min_index: float, max_index: float) -> numpy.ndarray:
        """
        Gets the graded index mesh.

        :param      coordinate_system:  The coordinate axis
        :type       coordinate_system:  numpy.ndarray
        :param      polygon:          The polygon
        :type       polygon:          Polygon object
        :param      min_index:        The minimum index value for the graded mesh
        :type       min_index:        float
        :param      max_index:        The maximum index value for the graded mesh
        :type       max_index:        float

        :returns:   The graded index mesh.
        :rtype:     numpy.ndarray
        """
        shifted_distance_mesh = self.get_shifted_distance_mesh(
            coordinate_system=coordinate_system,
            x_position=polygon.center.x,
            y_position=polygon.center.y,
            into_mesh=True
        )

        boolean_raster = polygon.get_rasterized_mesh(coordinate_system=coordinate_system)

        if numpy.all(boolean_raster == 0):
            return boolean_raster

        shifted_distance_mesh = -boolean_raster * shifted_distance_mesh**2

        shifted_distance_mesh -= shifted_distance_mesh.min()

        normalized_distance_mesh = shifted_distance_mesh / shifted_distance_mesh.max()

        delta_n = max_index - min_index

        normalized_distance_mesh *= delta_n
        normalized_distance_mesh += min_index

        return normalized_distance_mesh

    def overlay_structures(self, coordinate_system: Axis, structures_type: str = 'inner_structure') -> numpy.ndarray:
        """
        Return a mesh overlaying all the structures in the order they were defined.

        :param      coordinate_system:  The coordinates axis
        :type       coordinate_system:  Axis

        :returns:   The raster mesh of the structures.
        :rtype:     numpy.ndarray
        """
        mesh = numpy.zeros(coordinate_system.shape)

        return self.overlay_structures_on_mesh(
            mesh=mesh,
            coordinate_system=coordinate_system,
            structures_type=structures_type
        )

    def overlay_structures_on_mesh(self, mesh: numpy.ndarray, coordinate_system: Axis, structures_type: str = 'inner_structure') -> numpy.ndarray:
        """
        Return a mesh overlaying all the structures in the order they were defined.

        :param      coordinate_system:  The coordinates axis
        :type       coordinate_system:  Axis

        :returns:   The raster mesh of the structures.
        :rtype:     numpy.ndarray
        """
        return self._overlay_structure_on_mesh_(
            structure_list=getattr(self, structures_type),
            mesh=mesh,
            coordinate_system=coordinate_system
        )

    def plot(self, resolution: int = 300) -> None:
        """
        Plot the different representations [patch, raster-mesh, raster-gradient]
        of the geometry.

        :param      resolution:  The resolution to raster the structures
        :type       resolution:  int
        """
        min_x, min_y, max_x, max_y = self.get_structure_max_min_boundaries()

        coordinate_system = CoordinateSystem(
            min_x=min_x,
            max_x=max_x,
            min_y=min_y,
            max_y=max_y,
            nx=resolution,
            ny=resolution
        )

        coordinate_system.add_padding(padding_factor=1.2)

        figure = SceneList(unit_size=(4, 4), tight_layout=True, ax_orientation='horizontal')

        ax0 = figure.append_ax()
        ax1 = figure.append_ax()
        ax2 = figure.append_ax()

        self.render_patch_on_ax(ax=ax0)
        self.render_mesh_on_ax(ax=ax1, coordinate_system=coordinate_system)
        self.render_gradient_on_ax(ax=ax2, coordinate_system=coordinate_system)

        return figure

    def get_structures_boundaries(self) -> numpy.ndarray:
        """
        Returns array representing the boundaries of each of the existing structures

        :returns:   The structures boundaries.
        :rtype:     numpy.ndarray
        """
        boundaries = []
        for structure in self.structure_list:
            if structure.name == 'air':
                continue

            boundaries.append(structure.polygon.bounds)

        boundaries = numpy.array(boundaries)

        return boundaries

    def get_structure_max_min_boundaries(self) -> numpy.ndarray:
        """
        Returns array representing max and min x and y [4 points] boundaries
        of the total structures except for air.

        :returns:   The structures max/min boundaries.
        :rtype:     numpy.ndarray
        """
        boundaries = self.get_structures_boundaries()

        min_x, min_y, max_x, max_y = boundaries.T

        min_x = min_x.min()
        max_x = max_x.max()
        min_y = min_y.min()
        max_y = max_y.max()

        return min_x, min_y, max_x, max_y

    @property
    def boundaries(self):
        return self.get_structure_max_min_boundaries()


# -

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Tuple, Optional
from pydantic.dataclasses import dataclass
from pydantic import ConfigDict

import numpy
from FiberFusing import Circle
from FiberFusing.coordinate_system import CoordinateSystem
from FiberFusing.utils import get_silica_index
from FiberFusing.fiber.structure_collection import BaseClass
import pprint

from matplotlib import colors
from MPSPlots.render2D import SceneList, Axis, Polygon

pp = pprint.PrettyPrinter(indent=4, sort_dicts=False, compact=True, width=1)


@dataclass(config=ConfigDict(extra='forbid'), kw_only=True)
class GenericFiber(BaseClass):
    """
    Represents a generic fiber with specific wavelength and position attributes.

    Attributes:
        wavelength (float): The wavelength at which to evaluate the computation.
        position (Optional[Tuple[float, float]]): The position of the fiber, default is (0, 0).
    """
    wavelength: float
    position: Optional[Tuple[float, float]] = (0, 0)

    def __post_init__(self):
        self.structure_list = []
        self.add_air()

    @property
    def pure_silica_index(self) -> float:
        """
        Returns the refractive index of pure silica at the given wavelength.

        Returns:
            float: The refractive index of pure silica.
        """
        return get_silica_index(wavelength=self.wavelength)

    def set_position(self, position: Tuple[float, float]) -> None:
        """
        Sets the position for all structures in the fiber.

        Args:
            position (Tuple[float, float]): The new position.
        """
        for structure in self.structure_list:
            if structure.radius is None:
                continue

            structure.position = position
            structure.polygon = Circle(
                position=structure.position,
                radius=structure.radius,
                index=structure.index
            )

    def update_wavelength(self, new_value: float) -> None:
        """
        Updates the wavelength for the fiber class.

        Args:
            new_value (float): The new wavelength value.
        """
        self.wavelength = new_value
        self.__init__()

    def update_position(self, new_value: Tuple[float, float]) -> None:
        """
        Updates the position for the fiber class.

        Args:
            new_value (Tuple[float, float]): The new position value.
        """
        self.position = new_value
        self.__init__()

    def NA_to_core_index(self, NA: float, index_clad: float) -> float:
        """
        Converts numerical aperture (NA) to core index.

        Args:
            NA (float): Numerical aperture.
            index_clad (float): Cladding refractive index.

        Returns:
            float: Core refractive index.
        """
        return numpy.sqrt(NA**2 + index_clad**2)

    def core_index_to_NA(self, interior_index: float, exterior_index: float) -> float:
        """
        Converts core index to numerical aperture (NA).

        Args:
            interior_index (float): Interior refractive index.
            exterior_index (float): Exterior refractive index.

        Returns:
            float: Numerical aperture.
        """
        return numpy.sqrt(interior_index**2 - exterior_index**2)

    @property
    def polygones(self):
        """
        Returns the polygons representing the fiber structures.

        Returns:
            list: List of polygons.
        """
        if not self._polygones:
            self.initialize_polygones()
        return self._polygones

    def add_air(self, radius: float = 1e3) -> None:
        """
        Adds an air structure to the fiber.

        Args:
            radius (float): The radius of the air structure, default is 1e3.
        """
        self.create_and_add_new_structure(name='air', index=1.0, radius=radius)

    def add_silica_pure_cladding(self, radius: float = 62.5e-6, name: str = 'outer_clad') -> None:
        """
        Adds a pure silica cladding to the fiber.

        Args:
            radius (float): The radius of the cladding, default is 62.5e-6.
            name (str): The name of the cladding, default is 'outer_clad'.
        """
        self.create_and_add_new_structure(
            name=name,
            index=self.pure_silica_index,
            radius=radius
        )

    def render_patch_on_ax(self, ax: Axis) -> None:
        """
        Renders the patch representation of the fiber geometry on the given axis.

        Args:
            ax (Axis): The axis to render on.
        """
        for structure in self.fiber_structure:
            artist = Polygon(instance=structure.polygon._shapely_object)
            ax.add_artist(artist)

        ax.set_style(
            title='Fiber structure',
            x_label=r'x-distance [$\mu$m]',
            y_label=r'y-distance [$\mu$m]',
            x_scale_factor=1e6,
            y_scale_factor=1e6,
            equal_limits=True,
        )

    def render_raster_on_ax(self, ax: Axis, structure, coordinate_system: CoordinateSystem) -> None:
        """
        Renders the raster representation of a structure on the given axis.

        Args:
            ax (Axis): The axis to render on.
            structure: The structure to rasterize.
            coordinate_system (CoordinateSystem): The coordinate system to use.
        """
        boolean_raster = structure.polygon.get_rasterized_mesh(coordinate_system=coordinate_system)
        ax.add_mesh(
            x=coordinate_system.x_vector,
            y=coordinate_system.y_vector,
            scalar=boolean_raster,
            colormap='Blues'
        )

    def render_mesh_on_ax(self, ax: Axis, coordinate_system: CoordinateSystem) -> None:
        """
        Renders the rasterized representation of the fiber geometry on the given axis.

        Args:
            ax (Axis): The axis to render on.
            coordinate_system (CoordinateSystem): The coordinate system to use.
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

        ax.set_style(
            title='Rasterized mesh',
            x_label=r'x-distance [$\mu$m]',
            y_label=r'y-distance [$\mu$m]',
            x_scale_factor=1e6,
            y_scale_factor=1e6,
            equal_limits=True,
        )

    def shift_coordinates(self, coordinate_system: CoordinateSystem, x_shift: float, y_shift: float) -> numpy.ndarray:
        """
        Shifts the coordinates of the coordinate system by specified x and y shifts.

        Args:
            coordinate_system (CoordinateSystem): The coordinate system to shift.
            x_shift (float): The x shift value.
            y_shift (float): The y shift value.

        Returns:
            numpy.ndarray: The shifted coordinates.
        """
        shifted_coordinate = coordinate_system.to_unstructured_coordinate()
        shifted_coordinate[:, 0] -= x_shift
        shifted_coordinate[:, 1] -= y_shift

        return shifted_coordinate

    def get_shifted_distance_mesh(self, coordinate_system: CoordinateSystem, x_position: float, y_position: float, into_mesh: bool = True) -> numpy.ndarray:
        """
        Returns a mesh representing the distance from a specific point.

        Args:
            coordinate_system (CoordinateSystem): The coordinate system to use.
            x_position (float): The x position.
            y_position (float): The y position.
            into_mesh (bool): Whether to convert the distance into a mesh. Default is True.

        Returns:
            numpy.ndarray: The shifted distance mesh.
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

    def get_graded_index_mesh(self, coordinate_system: CoordinateSystem, polygon, min_index: float, max_index: float) -> numpy.ndarray:
        """
        Gets the graded index mesh for a polygon.

        Args:
            coordinate_system (CoordinateSystem): The coordinate system to use.
            polygon (Polygon): The polygon for which to get the graded index mesh.
            min_index (float): The minimum index value for the graded mesh.
            max_index (float): The maximum index value for the graded mesh.

        Returns:
            numpy.ndarray: The graded index mesh.
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

    def overlay_structures(self, coordinate_system: CoordinateSystem, structures_type: str = 'inner_structure') -> numpy.ndarray:
        """
        Overlays all the structures in the order they were defined on a mesh.

        Args:
            coordinate_system (CoordinateSystem): The coordinate system to use.
            structures_type (str): The type of structures to overlay. Default is 'inner_structure'.

        Returns:
            numpy.ndarray: The raster mesh of the structures.
        """
        mesh = numpy.zeros(coordinate_system.shape)
        return self.overlay_structures_on_mesh(
            mesh=mesh,
            coordinate_system=coordinate_system,
            structures_type=structures_type
        )

    def overlay_structures_on_mesh(self, mesh: numpy.ndarray, coordinate_system: CoordinateSystem, structures_type: str = 'inner_structure') -> numpy.ndarray:
        """
        Overlays all the structures in the order they were defined on a mesh.

        Args:
            mesh (numpy.ndarray): The mesh to overlay the structures on.
            coordinate_system (CoordinateSystem): The coordinate system to use.
            structures_type (str): The type of structures to overlay. Default is 'inner_structure'.

        Returns:
            numpy.ndarray: The raster mesh of the structures.
        """
        return self._overlay_structure_on_mesh_(
            structure_list=getattr(self, structures_type),
            mesh=mesh,
            coordinate_system=coordinate_system
        )

    def plot(self, resolution: int = 300) -> SceneList:
        """
        Plots the different representations [patch, raster-mesh] of the fiber geometry.

        Args:
            resolution (int): The resolution to raster the structures. Default is 300.

        Returns:
            SceneList: The scene list with the plotted representations.
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

        self.render_patch_on_ax(ax=ax0)
        self.render_mesh_on_ax(ax=ax1, coordinate_system=coordinate_system)

        return figure

    def get_structures_boundaries(self) -> numpy.ndarray:
        """
        Returns an array representing the boundaries of each of the existing structures.

        Returns:
        numpy.ndarray: The structures boundaries.
        """
        boundaries = []
        for structure in self.structure_list:
            if structure.name == 'air':
                continue

        boundaries.append(structure.polygon.bounds)

        return numpy.array(boundaries)

    def get_structure_max_min_boundaries(self) -> Tuple[float, float, float, float]:
        """
        Returns the max and min x and y boundaries of the total structures except for air.

        Returns:
            Tuple[float, float, float, float]: The structures max/min boundaries.
        """
        boundaries = self.get_structures_boundaries()

        min_x, min_y, max_x, max_y = boundaries.T
        return min_x.min(), min_y.min(), max_x.max(), max_y.max()

    @property
    def boundaries(self):
        """
        Returns the boundaries of the structures.

        Returns:
            Tuple[float, float, float, float]: The structures max/min boundaries.
        """
        return self.get_structure_max_min_boundaries()


# -

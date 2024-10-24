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
import matplotlib.pyplot as plt
from FiberFusing.plottings import plot_polygon
from FiberFusing.helper import _plot_helper

pp = pprint.PrettyPrinter(indent=4, sort_dicts=False, compact=True, width=1)


@dataclass(config=ConfigDict(extra='forbid', kw_only=True))
class GenericFiber(BaseClass):
    """
    Represents a generic fiber with wavelength and position attributes.

    Attributes
    ----------
    wavelength : float
        The wavelength at which to evaluate the computation.
    position : Optional[Tuple[float, float]]
        The position of the fiber. Defaults to (0, 0).
    """

    wavelength: float
    position: Optional[Tuple[float, float]] = (0, 0)

    def __post_init__(self):
        self.structure_list = []
        self.add_air()

    @property
    def pure_silica_index(self) -> float:
        """
        Calculate the refractive index of pure silica for the given wavelength.

        Returns
        -------
        float
            The refractive index of pure silica.
        """
        return get_silica_index(wavelength=self.wavelength)

    def set_position(self, position: Tuple[float, float]) -> None:
        """
        Update the position for all structures in the fiber.

        Parameters
        ----------
        position : Tuple[float, float]
            The new position coordinates as (x, y).

        Notes
        -----
        - Only updates structures that have a defined radius.
        - Recomputes polygons based on the new positions.
        """
        if not isinstance(position, tuple) or len(position) != 2:
            raise ValueError("Position must be a tuple with two float values (x, y).")

        for structure in self.structure_list:
            if structure.radius is not None:
                structure.position = position
                structure.polygon = Circle(
                    position=structure.position,
                    radius=structure.radius,
                    index=structure.index
                )

    def update_wavelength(self, new_value: float) -> None:
        """
        Update the wavelength of the fiber and recalculate dependent properties.

        Parameters
        ----------
        new_value : float
            The new wavelength value.

        Notes
        -----
        - Updates wavelength and recalculates relevant structures.
        """
        if new_value <= 0:
            raise ValueError("Wavelength must be a positive value.")

        self.wavelength = new_value
        for structure in self.structure_list:
            structure.refractive_index = self.pure_silica_index

    def update_position(self, new_value: Tuple[float, float]) -> None:
        """
        Update the position of the fiber.

        Parameters
        ----------
        new_value : Tuple[float, float]
            The new position coordinates.
        """
        self.position = new_value
        self.__init__()

    def NA_to_core_index(self, NA: float, index_clad: float) -> float:
        """
        Calculate the core refractive index given the numerical aperture (NA) and cladding index.

        Parameters
        ----------
        NA : float
            The numerical aperture.
        index_clad : float
            The refractive index of the cladding.

        Returns
        -------
        float
            The core refractive index.

        Raises
        ------
        ValueError
            If NA or index_clad are non-positive.
        """
        if NA <= 0 or index_clad <= 0:
            raise ValueError("NA and index_clad must be positive values.")

        return numpy.sqrt(NA**2 + index_clad**2)

    def core_index_to_NA(self, interior_index: float, exterior_index: float) -> float:
        """
        Calculate the numerical aperture (NA) given the core and cladding refractive indices.

        Parameters
        ----------
        interior_index : float
            The refractive index of the core.
        exterior_index : float
            The refractive index of the cladding.

        Returns
        -------
        float
            The numerical aperture.

        Raises
        ------
        ValueError
            If the interior index is less than or equal to the exterior index.
        """
        if interior_index <= exterior_index:
            raise ValueError("Interior index must be greater than exterior index.")

        return numpy.sqrt(interior_index**2 - exterior_index**2)

    @property
    def polygones(self):
        """
        Get the polygons representing the fiber structures.

        Returns
        -------
        list
            A list of polygons.
        """
        if not self._polygones:
            self.initialize_polygones()
        return self._polygones

    def add_air(self, radius: float = 1e3) -> None:
        """
        Add an air structure to the fiber.

        Parameters
        ----------
        radius : float, optional
            The radius of the air structure. Defaults to 1e3.
        """
        self.create_and_add_new_structure(name='air', index=1.0, radius=radius)

    def add_silica_pure_cladding(self, radius: float = 62.5e-6, name: str = 'outer_clad') -> None:
        """
        Add a pure silica cladding to the fiber.

        Parameters
        ----------
        radius : float, optional
            The radius of the cladding. Defaults to 62.5e-6.
        name : str, optional
            The name of the cladding. Defaults to 'outer_clad'.
        """
        self.create_and_add_new_structure(
            name=name,
            index=self.pure_silica_index,
            radius=radius
        )

    def shift_coordinates(self, coordinate_system: CoordinateSystem, x_shift: float, y_shift: float) -> numpy.ndarray:
        """
        Shift the coordinates of the given coordinate system.

        Parameters
        ----------
        coordinate_system : CoordinateSystem
            The coordinate system to shift.
        x_shift : float
            The shift value along the x-axis.
        y_shift : float
            The shift value along the y-axis.

        Returns
        -------
        numpy.ndarray
            The shifted coordinates.
        """
        shifted_coordinate = coordinate_system.to_unstructured_coordinate()
        shifted_coordinate[:, 0] -= x_shift
        shifted_coordinate[:, 1] -= y_shift

        return shifted_coordinate

    def get_shifted_distance_mesh(self, coordinate_system: CoordinateSystem, x_position: float, y_position: float, into_mesh: bool = True) -> numpy.ndarray:
        """
        Calculate a mesh representing the distance from a specified point.

        Parameters
        ----------
        coordinate_system : CoordinateSystem
            The coordinate system used for the calculation.
        x_position : float
            The x-coordinate of the point.
        y_position : float
            The y-coordinate of the point.
        into_mesh : bool, optional
            Whether to reshape the distance values into a mesh grid. Default is True.

        Returns
        -------
        numpy.ndarray
            The mesh of distances.

        Raises
        ------
        ValueError
            If the coordinate system shape is inconsistent.
        """
        shifted_coordinate = self.shift_coordinates(
            coordinate_system=coordinate_system,
            x_shift=x_position,
            y_shift=y_position
        )

        if shifted_coordinate.ndim != 2:
            raise ValueError("Shifted coordinates should have two dimensions.")

        distance = numpy.sqrt(shifted_coordinate[:, 0]**2 + shifted_coordinate[:, 1]**2)

        if into_mesh:
            try:
                distance = distance.reshape(coordinate_system.shape)
            except ValueError:
                raise ValueError("The distance array shape does not match the coordinate system's shape.")

        return distance

    def get_graded_index_mesh(self, coordinate_system: CoordinateSystem, polygon, min_index: float, max_index: float) -> numpy.ndarray:
        """
        Compute the graded index mesh for a given polygon within the coordinate system.

        This method calculates a graded index profile based on the distance from the
        polygon's center. The resulting mesh varies smoothly between the minimum and
        maximum refractive index values within the bounds of the polygon.

        Parameters
        ----------
        coordinate_system : CoordinateSystem
            The coordinate system defining the spatial grid where the index profile will be computed.
        polygon : Polygon
            The polygon object representing the area for which the graded index mesh is computed.
        min_index : float
            The minimum refractive index value, typically at the outer boundary of the polygon.
        max_index : float
            The maximum refractive index value, typically at the center of the polygon.

        Returns
        -------
        numpy.ndarray
            A 2D array representing the graded index mesh where values range between
            `min_index` and `max_index` based on the distance from the center of the polygon.

        Notes
        -----
        - If the polygon does not intersect with the coordinate system, a zero-filled
        mesh is returned.
        - The index profile is normalized based on the distance from the polygon's center
        and scaled between `min_index` and `max_index`.
        """
        # Get the distance mesh centered around the polygon
        shifted_distance_mesh = self.get_shifted_distance_mesh(
            coordinate_system=coordinate_system,
            x_position=polygon.center.x,
            y_position=polygon.center.y,
            into_mesh=True
        )

        # Generate a boolean raster mesh of the polygon within the coordinate system
        boolean_raster = polygon.get_rasterized_mesh(coordinate_system=coordinate_system)

        # If the polygon does not intersect with the coordinate system, return a zero mesh
        if numpy.all(boolean_raster == 0):
            return numpy.zeros(coordinate_system.shape)

        # Apply the boolean mask to the distance mesh
        masked_distance_mesh = boolean_raster * shifted_distance_mesh**2
        masked_distance_mesh -= masked_distance_mesh.min()  # Normalize minimum value to zero
        if masked_distance_mesh.max() != 0:
            normalized_distance_mesh = masked_distance_mesh / masked_distance_mesh.max()
        else:
            normalized_distance_mesh = masked_distance_mesh

        # Scale the normalized mesh to the index range [min_index, max_index]
        delta_n = max_index - min_index
        graded_index_mesh = normalized_distance_mesh * delta_n + min_index

        return graded_index_mesh

    def overlay_structures(self, coordinate_system: CoordinateSystem, structures_type: str = 'inner_structure') -> numpy.ndarray:
        """
        Overlay the structures on a mesh.

        Parameters
        ----------
        coordinate_system : CoordinateSystem
            The coordinate system used for the mesh.
        structures_type : str, optional
            Type of structures to overlay. Default is 'inner_structure'.

        Returns
        -------
        numpy.ndarray
            The raster mesh of the overlaid structures.
        """
        mesh = numpy.zeros(coordinate_system.shape)
        return self.overlay_structures_on_mesh(
            mesh=mesh,
            coordinate_system=coordinate_system,
            structures_type=structures_type
        )

    def overlay_structures_on_mesh(self, mesh: numpy.ndarray, coordinate_system: CoordinateSystem, structures_type: str = 'inner_structure') -> numpy.ndarray:
        """
        Overlay structures on the given mesh.

        Parameters
        ----------
        mesh : numpy.ndarray
            The mesh on which to overlay structures.
        coordinate_system : CoordinateSystem
            The coordinate system used for the overlay.
        structures_type : str, optional
            Type of structures to overlay. Default is 'inner_structure'.

        Returns
        -------
        numpy.ndarray
            The raster mesh with the overlaid structures.
        """
        return self._overlay_structure_on_mesh_(
            structure_list=getattr(self, structures_type),
            mesh=mesh,
            coordinate_system=coordinate_system
        )

    @_plot_helper
    def plot(self, ax: plt.Axes = None, show_center: bool = False, show_core: bool = True) -> None:
        """
        Plot the fiber geometry representation including patch and raster-mesh.

        Parameters
        ----------
        resolution : int, optional
            Resolution for rasterizing structures. Default is 300.
        """
        for structure in self.fiber_structure:
            plot_polygon(ax=ax, polygon=structure.polygon._shapely_object)

    def get_structures_boundaries(self) -> numpy.ndarray:
        """
        Get the boundaries of each structure in the fiber.

        Returns
        -------
        numpy.ndarray
            An array representing the boundaries of each structure.
        """
        boundaries = []
        for structure in self.structure_list:
            if structure.name == 'air':
                continue

        boundaries.append(structure.polygon.bounds)

        return numpy.array(boundaries)

    def get_structure_max_min_boundaries(self) -> Tuple[float, float, float, float]:
        """
        Get the maximum and minimum boundaries for the structures, excluding air.

        Returns
        -------
        Tuple[float, float, float, float]
            The max and min x and y boundaries.
        """
        boundaries = self.get_structures_boundaries()

        min_x, min_y, max_x, max_y = boundaries.T
        return min_x.min(), min_y.min(), max_x.max(), max_y.max()

    @property
    def boundaries(self):
        """
        Get the max and min boundaries for the structures.

        Returns
        -------
        Tuple[float, float, float, float]
            The max and min x and y boundaries.
        """
        return self.get_structure_max_min_boundaries()

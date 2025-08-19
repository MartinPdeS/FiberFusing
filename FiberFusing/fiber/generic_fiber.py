#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Tuple, Optional
import numpy
import pprint
from copy import deepcopy
import matplotlib.pyplot as plt

from FiberFusing import Circle, CircleOpticalStructure
from FiberFusing.geometries.point import Point
from FiberFusing.coordinate_system import CoordinateSystem
from FiberFusing.plottings import plot_polygon
from FiberFusing.helper import _plot_helper
from FiberFusing.graded_index import GradedIndex

pp = pprint.PrettyPrinter(indent=4, sort_dicts=False, compact=True, width=1)


class GenericFiber():
    """
    Represents a generic fiber with wavelength and position attributes.

    Attributes
    ----------
    wavelength : float
        The wavelength at which to evaluate the computation.
    position : Optional[Tuple[float, float]]
        The position of the fiber. Defaults to (0, 0).

    References
    ----------
    For gradient core fibers, see:
    .. [1] Nature, "Fiber with gradient core index", https://www.nature.com/articles/s41598-018-27072-2
    """

    def __init__(self, position: Optional[Tuple[float, float]] = (0, 0)):

        if isinstance(position, Point):
            position = (position.x, position.y)

        self.position = position
        self.structure_list = []
        self.add_air()

    def randomize_refractive_index(self, factor: float) -> None:
        """
        Randomizes the refractive index of each structure in the fiber by a given factor.

        Parameters
        ----------
        factor : float
            The factor by which to randomize the refractive index.
        """
        for structure in self.structure_list:
            structure.refractive_index += factor * numpy.random.uniform(0, 1)

    @property
    def full_structure(self) -> list:
        """Returns the list of all structures."""
        return self.structure_list

    @property
    def fiber_structure(self) -> list:
        """Returns the list of structures excluding 'air'."""
        return [s for s in self.structure_list if s.name not in ['air']]

    @property
    def refractive_index_list(self) -> list:
        """Returns a list of refractive indices of the fiber structures."""
        return [struct.index for struct in self.fiber_structure]

    @property
    def inner_structure(self) -> list:
        """Returns the list of structures excluding 'air' and 'outer_clad'."""
        return [s for s in self.structure_list if s.name not in ['air', 'outer_clad']]

    def __getitem__(self, idx: int):
        """
        Allows indexing to access specific structures.

        Args:
            idx (int): Index of the structure.

        Returns:
            CircleOpticalStructure: The structure at the specified index.
        """
        return self.structure_list[idx]

    def scale(self, factor: float):
        """
        Scales the radius of each structure by a given factor.

        Args:
            factor (float): The scaling factor.

        Returns:
            BaseStructureCollection: A new scaled version of the collection.
        """
        fiber_copy = deepcopy(self)
        for structure in fiber_copy.structure_list:
            if structure.radius is not None:
                structure.radius *= factor
                new_polygon = Circle(
                    position=structure.position,
                    radius=structure.radius,
                    index=structure.index
                )
                structure.polygon = new_polygon

        return fiber_copy

    def create_and_add_new_structure(self, refractive_index: float | GradedIndex = None, NA: float = None, **kwargs) -> None:
        """
        Adds a new circular structure to the collection.

        Parameters
        ----------
        refractive_index : float, optional
            The refractive index of the new structure. If provided, NA should be None.
        NA : float, optional
            The numerical aperture of the new structure. If provided, refractive_index should be None.

        Raises
        ------
        ValueError
            If both refractive_index and NA are provided or if neither is provided.
        """
        refractive_index = self._interpret_index_or_NA_to_index(refractive_index=refractive_index, NA=NA)

        new_structure = CircleOpticalStructure(
            **kwargs,
            refractive_index=refractive_index,
            position=self.position
        )
        setattr(self, new_structure.name, new_structure)
        self.structure_list.append(new_structure)

    def _interpret_index_or_NA_to_index(self, refractive_index: float, NA: float) -> float:
        """
        Interprets and converts NA or index to a refractive index.

        Parameters
        ----------
        refractive_index : float, optional
            The refractive index of the structure. If provided, NA should be None.
        NA : float, optional
            The numerical aperture of the structure. If provided, refractive_index should be None.

        Returns
        -------
        float
            The refractive index of the structure.
        """
        if (refractive_index is not None) == (NA is not None):
            raise ValueError('Only one of NA or refractive_index can be defined')

        if refractive_index is not None:
            return refractive_index

        if len(self.structure_list) == 0:
            raise ValueError('Cannot initialize layer from NA if no previous layer is defined')

        return self.compute_index_from_NA(
            exterior_index=self.structure_list[-1].refractive_index,
            NA=NA
        )

    def compute_index_from_NA(self, exterior_index: float, NA: float) -> float:
        """
        Computes refractive index from NA and exterior index.

        Parameters
        ----------
        exterior_index : float
            The refractive index of the exterior medium.
        NA : float
            The numerical aperture of the structure.

        Returns
        -------
        float
            The computed refractive index.
        """
        return numpy.sqrt(NA**2 + exterior_index**2)

    def _overlay_structure_on_mesh_(self, structure_list: list, mesh: numpy.ndarray, coordinate_system) -> numpy.ndarray:
        """
        Overlays the structures on a mesh grid based on the coordinate system.

        Parameters
        ----------
        structure_list : list
            A list of structures to overlay on the mesh.
        mesh : numpy.ndarray
            The mesh grid on which the structures will be overlayed.
        coordinate_system : CoordinateSystem
            The coordinate system used for overlaying the structures.

        Returns
        -------
        numpy.ndarray
            A numpy ndarray with the structures overlayed onto the original mesh.
        """
        for structure in structure_list:
            raster = structure.polygon.get_rasterized_mesh(coordinate_system=coordinate_system)
            mesh[numpy.where(raster != 0)] = 0

            if isinstance(structure.refractive_index, GradedIndex):
                refractive_index = self.get_graded_index_mesh(
                    coordinate_system=coordinate_system,
                    polygon=structure.polygon,
                    refractive_index=structure.refractive_index,
                )
            else:
                refractive_index = structure.refractive_index

            mesh += raster * refractive_index

        return mesh

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
                    refractive_index=structure.refractive_index
                )

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
        self.create_and_add_new_structure(name='air', refractive_index=1.0, radius=radius)

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
        shifted_coordinate = coordinate_system.get_coordinates_flattened()
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

    def get_graded_index_mesh(self, coordinate_system: CoordinateSystem, polygon, refractive_index: GradedIndex) -> numpy.ndarray:
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
        refractive_index : GradedIndex
            The graded index object containing the minimum and maximum refractive index values.

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
        delta_n = refractive_index.outside - refractive_index.inside
        graded_index_mesh = normalized_distance_mesh * delta_n + refractive_index.inside

        return graded_index_mesh

    def get_raster_mesh(self, coordinate_system: CoordinateSystem, structures_type: str = 'inner_structure') -> numpy.ndarray:
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
    def plot(self, ax: plt.Axes = None) -> None:
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

        x_min, y_min, x_max, y_max = boundaries.T
        return x_min.min(), y_min.min(), x_max.max(), y_max.max()

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

    @_plot_helper
    def plot_raster(self, coordinate_system, ax: plt.Axes = None) -> None:
        """
        Render the rasterized representation of the geometry onto a given matplotlib axis.

        Parameters
        ----------
        ax : plt.Axes, optional
            The matplotlib axis on which the rasterized representation will be plotted. If not provided, a new axis is created.
        show : bool, optional
            Whether to display the plot immediately. Default is True.

        Returns
        -------
        None
        """
        mesh = self.get_raster_mesh(coordinate_system=coordinate_system)
        ax.pcolormesh(coordinate_system.x_vector, coordinate_system.y_vector, mesh, cmap='Blues')

        ax.set(title='Fiber structure', xlabel=r'x-distance [m]', ylabel=r'y-distance [m]')
        ax.ticklabel_format(axis='both', style='sci', scilimits=(-6, -6), useOffset=False)

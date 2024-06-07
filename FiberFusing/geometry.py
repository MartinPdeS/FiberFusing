#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import List, Optional, Tuple, Union
import numpy
from dataclasses import field
from scipy.ndimage import gaussian_filter
from pydantic.dataclasses import dataclass
from pydantic import ConfigDict

from MPSPlots.render2D import SceneList, Axis
from matplotlib import colors

from FiberFusing.coordinate_system import CoordinateSystem
import FiberFusing


@dataclass(config=ConfigDict(extra='forbid'), kw_only=True)
class Geometry(object):
    """
    Represents the refractive index (RI) geometric profile including background and fiber structures.

    Attributes:
        background (object): Geometric object representing the background (usually air).
        additional_structure_list (List[object]): List of geometric objects representing additional structures.
        fiber_list (List[object]): List of fiber structures.
        x_bounds (Union[List[float], str]): X boundaries for rendering the structure. Can be a list of bounds or a keyword from ['auto', 'left', 'right', 'centering'].
        y_bounds (Union[List[float], str]): Y boundaries for rendering the structure. Can be a list of bounds or a keyword from ['auto', 'top', 'bottom', 'centering'].
        resolution (int): Number of points in x and y directions for evaluating the rendering.
        index_scrambling (float): Index scrambling for degeneracy lifting.
        gaussian_filter (Optional[int]): Standard deviation of the Gaussian blurring for the mesh.
        boundary_pad_factor (float): Factor multiplying the boundary value to keep padding between mesh and boundary.
    """
    background: object
    additional_structure_list: Optional[List[object]] = field(default_factory=list)
    fiber_list: Optional[List[object]] = (field(default_factory=list))
    x_bounds: Optional[Union[Tuple[float, float], str]] = 'centering'
    y_bounds: Optional[Union[Tuple[float, float], str]] = 'centering'
    resolution: Optional[int] = 100
    index_scrambling: Optional[float] = 0.0
    gaussian_filter: Optional[int] = None
    boundary_pad_factor: Optional[float] = 1.3

    def generate_coordinate_system(self) -> None:
        """
        Generates the coordinate system for the mesh construction.
        """
        min_x, min_y, max_x, max_y = self.get_boundaries()
        self.coordinate_system = CoordinateSystem(
            min_x=min_x, max_x=max_x, min_y=min_y, max_y=max_y, nx=self.resolution, ny=self.resolution
        )
        self.coordinate_system.centering(factor=self.boundary_pad_factor)
        self.interpret_y_boundary()
        self.interpret_x_boundary()

    def add_fiber(self, *fibers: object) -> None:
        """
        Adds fiber structures to the geometry.

        Args:
            fibers (object): Fiber structures to be added, defined using the generic_fiber class in fiber_catalogue.py.
        """
        self.fiber_list.extend(fibers)

    def add_structure(self, *structures: object) -> None:
        """
        Adds custom structures to the geometry.

        Args:
            structures (object): Custom structures to be added.
        """
        self.additional_structure_list.extend(structures)

    @property
    def structure_list(self) -> List[object]:
        """
        Returns a list of all optical structures considered for the mesh construction.

        Returns:
            List[object]: List of the optical structures.
        """
        return [self.background, *self.additional_structure_list, *self.fiber_list]

    def interpret_x_boundary(self) -> None:
        """
        Interprets the x_bounds parameter and applies the appropriate boundary setting to the coordinate system.
        """
        if isinstance(self.x_bounds, list | tuple):
            self.coordinate_system.set_x_boundary(self.x_bounds)
        else:
            match self.x_bounds:
                case 'right':
                    self.coordinate_system.set_right()
                case 'left':
                    self.coordinate_system.set_left()
                case 'centering':
                    self.coordinate_system.x_centering()
                case _:
                    raise ValueError(f"Invalid x_bounds input: {self.x_bounds}. Valid inputs are a list of bounds or one of ['right', 'left', 'centering'].")

    def interpret_y_boundary(self) -> None:
        """
        Interprets the y_bounds parameter and applies the appropriate boundary setting to the coordinate system.
        """
        if isinstance(self.y_bounds, list | tuple):
            self.coordinate_system.set_y_boundary(self.y_bounds)
        else:
            match self.y_bounds:
                case 'top':
                    self.coordinate_system.set_top()
                case 'bottom':
                    self.coordinate_system.set_bottom()
                case 'centering':
                    self.coordinate_system.y_centering()
                case _:
                    raise ValueError(f"Invalid y_bounds input: {self.y_bounds}. Valid inputs are a list of bounds or one of ['top', 'bottom', 'centering'].")

    def get_boundaries(self) -> Tuple[float, float, float, float]:
        """
        Calculates the boundaries from the collection of defined structures.

        Returns:
            Tuple[float, float, float, float]: The boundaries as (min_x, min_y, max_x, max_y).

        Raises:
            ValueError: If no structures are provided for computing the mesh.
        """
        if not self.additional_structure_list and not self.fiber_list:
            raise ValueError('No internal structures provided for computation of the mesh.')

        # Collect all min and max boundaries from each structure
        min_x, min_y, max_x, max_y = zip(
            *(obj.get_structure_max_min_boundaries() for obj in self.additional_structure_list + self.fiber_list)
        )

        # Calculate the overall min and max boundaries
        return (numpy.min(min_x), numpy.min(min_y), numpy.max(max_x), numpy.max(max_y))

    @property
    def refractive_index_maximum(self) -> float:
        """
        Calculates the maximum refractive index across all structures.

        Returns:
            float: Maximum refractive index.
        """
        return max(index for obj in self.structure_list for index in obj.refractive_index_list)

    @property
    def refractive_index_minimum(self) -> float:
        """
        Calculates the minimum refractive index across all non-background structures.

        Returns:
            float: Minimum refractive index.
        """
        return min(index for obj in self.structure_list if not isinstance(obj, FiberFusing.background.BackGround) for index in obj.refractive_index_list)

    def get_index_range(self) -> List[float]:
        """
        Returns a list of all refractive indices associated with the elements of the geometry.

        Returns:
            List[float]: List of refractive indices.
        """
        return [float(obj.index) for obj in self.structure_list]

    def rotate(self, angle: float) -> None:
        """
        Rotates all structures within the geometry by a given angle.

        Args:
            angle (float): Angle to rotate the geometry, in degrees.
        """
        for structure in self.structure_list:
            structure = structure.rotate(angle=angle)

    def generate_coordinate_mesh(self) -> None:
        """
        Generates a coordinate system and then creates a mesh based on this system.
        """
        self.generate_coordinate_system()
        self.mesh = self.generate_mesh()

    def randomize_fiber_structures_index(self, random_factor: float) -> None:
        """
        Randomizes the refractive index of fiber structures by a specified factor.

        Args:
            random_factor (float): Factor to randomize the refractive index.
        """
        for fiber in self.fiber_list:
            for structure in fiber.inner_structure:
                adjustment = structure.index * self.index_scrambling * numpy.random.rand() * random_factor
                structure.index += adjustment

    def rasterize_polygons(self, coordinates: numpy.ndarray) -> numpy.ndarray:
        """
        Rasterizes the polygons defined in the geometry onto a mesh.

        Args:
            coordinates (numpy.ndarray): The coordinates at which to evaluate the mesh.

        Returns:
            numpy.ndarray: The rasterized mesh.
        """
        mesh = numpy.zeros(self.coordinate_system.shape)

        self.background.overlay_structures_on_mesh(mesh=mesh, coordinate_system=self.coordinate_system)

        for structure in self.additional_structure_list:
            structure.overlay_structures_on_mesh(mesh=mesh, coordinate_system=self.coordinate_system)

        if self.index_scrambling != 0:
            self.randomize_fiber_structures_index(random_factor=self.index_scrambling)

        for fiber in self.fiber_list:
            fiber.overlay_structures_on_mesh(mesh=mesh, coordinate_system=self.coordinate_system)

        return mesh

    def add_background_to_mesh(self, mesh: numpy.ndarray) -> None:
        """
        Adds the rasterized background to the provided mesh.

        Args:
            mesh (numpy.ndarray): The mesh to which the background is added.
        """
        raster = self.background.get_rasterized_mesh(coordinate_system=self.coordinate_system)
        mask = raster != 0
        mesh[mask] = 0
        raster *= self.background.index
        mesh += raster

    def generate_mesh(self) -> numpy.ndarray:
        """
        Generates the full mesh for the geometry using the defined coordinate system.

        Returns:
            numpy.ndarray: The fully generated mesh.
        """
        # Convert coordinate system mesh grids to a single array of coordinates.
        coordinates = numpy.vstack((self.coordinate_system.x_mesh.flatten(), self.coordinate_system.y_mesh.flatten())).T
        mesh = self.rasterize_polygons(coordinates=coordinates)

        if self.gaussian_filter is not None:
            mesh = gaussian_filter(mesh, sigma=self.gaussian_filter)

        return mesh

    def render_patch_on_ax(self, ax: Axis) -> None:
        """
        Renders the patch representation of the geometry onto a given matplotlib axis.

        Args:
            ax (Axes): The matplotlib axis to which the patch representation will be appended.
        """
        ax.set_style(
            title='Coupler index structure',
            x_label=r'x-distance [$\mu$m]',
            y_label=r'y-distance [$\mu$m]',
            x_scale_factor=1e6,
            y_scale_factor=1e6,
            equal_limits=True,
        )

        for structure in self.additional_structure_list:
            structure.render_patch_on_ax(ax=ax)

        for fiber in self.fiber_list:
            fiber.render_patch_on_ax(ax=ax)

    def render_mesh_on_ax(self, ax: Axis) -> None:
        """
        Renders the rasterized representation of the geometry onto a given matplotlib axis.

        Args:
            ax (Axes): The matplotlib axis to which the rasterized representation will be appended.
        """
        artist = ax.add_mesh(
            x=self.coordinate_system.x_vector,
            y=self.coordinate_system.y_vector,
            scalar=self.mesh,
        )

        ax.set_style(
            title='Rasterized mesh',
            x_label=r'x-distance [$\mu$m]',
            y_label=r'y-distance [$\mu$m]',
            x_scale_factor=1e6,
            y_scale_factor=1e6,
            equal_limits=True,
            show_colorbar=True,
        )

        ax.add_colorbar(
            artist=artist,
            discreet=False,
            position='right',
            numeric_format='%.4f',
            colormap='Blues',
            norm=colors.LogNorm(vmin=self.refractive_index_minimum / 1.01)
        )

    def plot(self, show_patch: bool = True, show_mesh: bool = True) -> SceneList:
        """
        Plot the different representations [patch, mesh] of the geometry.

        :param      show_patch:     The show patch
        :type       show_patch:     bool
        :param      show_mesh:      The show mesh
        :type       show_mesh:      bool

        :returns:   The figure encompassing all the axis
        :rtype:     SceneList
        """
        self.generate_coordinate_mesh()

        figure = SceneList(
            unit_size=(4, 4),
            tight_layout=True,
            ax_orientation='horizontal'
        )

        if show_patch:
            ax = figure.append_ax()
            self.render_patch_on_ax(ax)

        if show_mesh:
            ax = figure.append_ax()
            self.render_mesh_on_ax(ax)

        ax.set_style(
            title='Fiber structure',
            x_label=r'x-distance [$\mu$m]',
            y_label=r'y-distance [$\mu$m]',
            x_scale_factor=1e6,
            y_scale_factor=1e6,
            equal_limits=True,
        )

        return figure

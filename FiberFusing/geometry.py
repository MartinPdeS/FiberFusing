#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import List, Optional, Tuple, Union
import numpy
from dataclasses import field
from scipy.ndimage import gaussian_filter
from pydantic.dataclasses import dataclass
import FiberFusing
import matplotlib.pyplot as plt
from FiberFusing.coordinate_system import CoordinateSystem
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.colors as colors
from MPSPlots.styles import mps
from FiberFusing.helper import _plot_helper


@dataclass(config=dict(extra='forbid', kw_only=True))
class Geometry:
    """
    Represents the refractive index (RI) geometric profile including background and fiber structures.

    Parameters
    ----------
    background : object
        Geometric object representing the background (usually air).
    additional_structure_list : List[object], optional
        List of geometric objects representing additional structures. Default is an empty list.
    fiber_list : List[object], optional
        List of fiber structures. Default is an empty list.
    x_bounds : Union[Tuple[float, float], str], optional
        X boundaries for rendering the structure. Can be a tuple of bounds or one of ['auto', 'left', 'right', 'centering']. Default is 'centering'.
    y_bounds : Union[Tuple[float, float], str], optional
        Y boundaries for rendering the structure. Can be a tuple of bounds or one of ['auto', 'top', 'bottom', 'centering']. Default is 'centering'.
    resolution : int, optional
        Number of points in x and y directions for evaluating the rendering. Default is 100.
    index_scrambling : float, optional
        Index scrambling for degeneracy lifting. Default is 0.0.
    gaussian_filter : Optional[int], optional
        Standard deviation of the Gaussian blurring for the mesh. Default is None.
    boundary_pad_factor : float, optional
        Factor multiplying the boundary value to keep padding between mesh and boundary. Default is 1.3.
    """

    background: object
    additional_structure_list: Optional[List[object]] = field(default_factory=list)
    fiber_list: Optional[List[object]] = field(default_factory=list)
    x_bounds: Optional[Union[Tuple[float, float], str]] = 'centering'
    y_bounds: Optional[Union[Tuple[float, float], str]] = 'centering'
    resolution: Optional[int] = 100
    index_scrambling: Optional[float] = 0.0
    gaussian_filter: Optional[int] = None
    boundary_pad_factor: Optional[float] = 1.3

    initialized: bool = False

    def generate_coordinate_system(self) -> None:
        """
        Generate the coordinate system for the mesh construction.

        Raises
        ------
        ValueError
            If boundaries cannot be determined from the structures.
        """
        try:
            min_x, min_y, max_x, max_y = self.get_boundaries()
        except ValueError as e:
            raise ValueError(f"Failed to generate coordinate system: {str(e)}")

        self.coordinate_system = CoordinateSystem(
            min_x=min_x, max_x=max_x, min_y=min_y, max_y=max_y, nx=self.resolution, ny=self.resolution
        )
        self.coordinate_system.center(factor=self.boundary_pad_factor)

        self.interpret_y_boundary()
        self.interpret_x_boundary()

    def add_fiber(self, *fibers: object) -> None:
        """
        Add fiber structures to the geometry.

        Parameters
        ----------
        fibers : object
            Fiber structures to be added.
        """
        self.fiber_list.extend(fibers)

    def add_structure(self, *structures: object) -> None:
        """
        Add custom structures to the geometry.

        Parameters
        ----------
        structures : object
            Custom structures to be added.
        """
        self.additional_structure_list.extend(structures)

    @property
    def structure_list(self) -> List[object]:
        """
        Get a list of all optical structures considered for the mesh construction.

        Returns
        -------
        List[object]
            List of the optical structures.
        """
        return [self.background, *self.additional_structure_list, *self.fiber_list]

    def interpret_x_boundary(self) -> None:
        """
        Interpret the x_bounds parameter and apply the appropriate boundary setting to the coordinate system.

        Raises
        ------
        ValueError
            If x_bounds is invalid.
        """
        if isinstance(self.x_bounds, (list, tuple)):
            self.coordinate_system.x_min, self.coordinate_system.x_max = self.x_bounds
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
        Interpret the y_bounds parameter and apply the appropriate boundary setting to the coordinate system.

        Raises
        ------
        ValueError
            If y_bounds is invalid.
        """
        if isinstance(self.y_bounds, (list, tuple)):
            self.coordinate_system.y_min, self.coordinate_system.y_max = self.y_bounds
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
        Calculate the boundaries from the collection of defined structures.

        Returns
        -------
        Tuple[float, float, float, float]
            The boundaries as (min_x, min_y, max_x, max_y).

        Raises
        ------
        ValueError
            If no structures are provided for computing the mesh.
        """
        if not self.additional_structure_list and not self.fiber_list:
            raise ValueError('No internal structures provided for computation of the mesh.')

        min_x, min_y, max_x, max_y = zip(
            *(obj.get_structure_max_min_boundaries() for obj in self.additional_structure_list + self.fiber_list)
        )
        return (numpy.min(min_x), numpy.min(min_y), numpy.max(max_x), numpy.max(max_y))

    @property
    def refractive_index_maximum(self) -> float:
        """
        Calculate the maximum refractive index across all structures.

        Returns
        -------
        float
            Maximum refractive index.
        """
        return max(index for obj in self.structure_list for index in obj.refractive_index_list)

    @property
    def refractive_index_minimum(self) -> float:
        """
        Calculate the minimum refractive index across all non-background structures.

        Returns
        -------
        float
            Minimum refractive index.
        """
        return min(index for obj in self.structure_list if not isinstance(obj, FiberFusing.background.BackGround) for index in obj.refractive_index_list)

    def get_index_range(self) -> List[float]:
        """
        Get a list of all refractive indices associated with the elements of the geometry.

        Returns
        -------
        List[float]
            List of refractive indices.
        """
        return [float(obj.index) for obj in self.structure_list]

    def rotate(self, angle: float) -> None:
        """
        Rotate all structures within the geometry by a given angle.

        Parameters
        ----------
        angle : float
            Angle to rotate the geometry, in degrees.
        """
        for structure in self.structure_list:
            structure.rotate(angle=angle)

    def generate_coordinate_mesh(self) -> None:
        """
        Generate a coordinate system and then create a mesh based on this system.
        """
        if self.initialized is False:
            self.generate_coordinate_system()
            self.mesh = self.generate_mesh()
            self.initialized = True

    def randomize_fiber_structures_index(self, random_factor: float) -> None:
        """
        Randomize the refractive index of fiber structures by a specified factor.

        Parameters
        ----------
        random_factor : float
            Factor to randomize the refractive index.
        """
        for fiber in self.fiber_list:
            for structure in fiber.inner_structure:
                adjustment = structure.index * self.index_scrambling * numpy.random.rand() * random_factor
                structure.index += adjustment

    def rasterize_polygons(self) -> numpy.ndarray:
        """
        Rasterize the polygons defined in the geometry onto a mesh.

        Parameters
        ----------
        coordinates : numpy.ndarray
            The coordinates at which to evaluate the mesh.

        Returns
        -------
        numpy.ndarray
            The rasterized mesh.
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
        Add the rasterized background to the provided mesh.

        Parameters
        ----------
        mesh : numpy.ndarray
            The mesh to which the background is added. Must match the shape of the coordinate system.

        Raises
        ------
        ValueError
            If the mesh dimensions do not match the coordinate system.
        """
        if mesh.shape != self.coordinate_system.shape:
            raise ValueError("The provided mesh dimensions do not match the coordinate system shape.")

        raster = self.background.get_rasterized_mesh(coordinate_system=self.coordinate_system)
        mask = raster != 0
        mesh[mask] = 0
        raster *= self.background.index
        mesh += raster

    def generate_mesh(self) -> numpy.ndarray:
        """
        Generate the full mesh for the geometry using the defined coordinate system.

        Returns
        -------
        numpy.ndarray
            The fully generated mesh.

        Raises
        ------
        AttributeError
            If the coordinate system has not been generated before calling this method.
        """
        if not hasattr(self, 'coordinate_system'):
            raise AttributeError("Coordinate system has not been generated. Call generate_coordinate_system() first.")

        mesh = self.rasterize_polygons()

        if self.gaussian_filter is not None:
            mesh = gaussian_filter(mesh, sigma=self.gaussian_filter)

        return mesh

    @_plot_helper
    def plot_patch(self, ax: plt.Axes = None, show: bool = True) -> None:
        """
        Renders the patch representation of the geometry onto a given matplotlib axis.

        Args:
            ax (plt.Axes): The matplotlib axis to which the patch representation will be appended.
        """
        for structure in self.additional_structure_list:
            structure.plot(ax=ax, show=False)

        for fiber in self.fiber_list:
            fiber.plot(ax=ax, show=False)

        ax.set(title='Fiber structure', xlabel=r'x-distance [m]', ylabel=r'y-distance [m]')
        ax.ticklabel_format(axis='both', style='sci', scilimits=(-6, -6), useOffset=False)

    @_plot_helper
    def plot_raster(self, ax: plt.Axes = None, show: bool = True) -> None:
        """
        Renders the rasterized representation of the geometry onto a given matplotlib axis.

        Args:
            ax (plt.Axes): The matplotlib axis to which the rasterized representation will be appended.
        """
        image = ax.pcolormesh(
            self.coordinate_system.x_vector,
            self.coordinate_system.y_vector,
            self.mesh,
            cmap='Blues',
            norm=colors.PowerNorm(gamma=5)
        )

        divider = make_axes_locatable(ax)
        cax = divider.append_axes('right', size='5%', pad=0.05)
        ax.get_figure().colorbar(image, cax=cax, orientation='vertical')

        ax.set(title='Fiber structure', xlabel=r'x-distance [m]', ylabel=r'y-distance [m]')
        ax.ticklabel_format(axis='both', style='sci', scilimits=(-6, -6), useOffset=False)
        ax.grid(True)

    def plot(self, show_patch: bool = True, show_mesh: bool = True, show: bool = True) -> plt.Figure:
        """
        Plot the different representations [patch, mesh] of the geometry.

        :param      show_patch:     The show patch
        :type       show_patch:     bool
        :param      show_mesh:      The show mesh
        :type       show_mesh:      bool

        :returns:   The figure encompassing all the axis
        :rtype:     plt.Figure
        """
        self.generate_coordinate_mesh()

        n_ax = bool(show_patch) + bool(show_mesh)
        unit_size = numpy.array([1, n_ax])

        with plt.style.context(mps):
            _, axes = plt.subplots(
                *unit_size,
                figsize=5 * numpy.flip(unit_size),
                sharex=True,
                sharey=True,
                subplot_kw=dict(aspect='equal', xlabel='x-distance [m]', ylabel='y-distance [m]'),
            )

        axes_iter = iter(axes.flatten())

        if show_patch:
            ax = next(axes_iter)
            self.plot_patch(axes[0], show=False)

        if show_mesh:
            ax = next(axes_iter)
            self.plot_raster(ax, show=False)

        if show:
            plt.show()

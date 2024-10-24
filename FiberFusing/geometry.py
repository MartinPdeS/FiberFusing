#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import List, Optional, Tuple, Union
import numpy
from scipy.ndimage import gaussian_filter
import FiberFusing
import matplotlib.pyplot as plt
from FiberFusing.coordinate_system import CoordinateSystem
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.colors as colors
from MPSPlots.styles import mps
from FiberFusing.helper import _plot_helper
from FiberFusing.background import BackGround


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

    def __init__(
            self,
            additional_structure_list: Optional[List[object]],
            background: Optional[BackGround] = None,
            fiber_list: Optional[List[object]] = [],
            x_bounds: Optional[Tuple[float, float] | str] = 'centering',
            y_bounds: Optional[Tuple[float, float] | str] = 'centering',
            resolution: Optional[int] = 100,
            index_scrambling: Optional[float] = 0.0,
            gaussian_filter: Optional[int] = None,
            boundary_pad_factor: Optional[float] = 1.3):

        self.resolution = resolution
        self.boundary_pad_factor = boundary_pad_factor
        self.index_scrambling = index_scrambling
        self.gaussian_filter = gaussian_filter

        self.background = background if background else BackGround(index=1)

        self.additional_structure_list = additional_structure_list
        self.fiber_list = fiber_list

        min_x, min_y, max_x, max_y = self.get_boundaries()

        self.coordinate_system = CoordinateSystem(
            min_x=min_x, max_x=max_x, min_y=min_y, max_y=max_y, nx=self.resolution, ny=self.resolution
        )
        self.coordinate_system.center(factor=self.boundary_pad_factor)

        self.x_bounds = x_bounds
        self.y_bounds = y_bounds

        self.mesh = self.generate_mesh()

    def update_coordinate_system(self) -> None:
        """
        Generate the coordinate system for the mesh construction.

        Raises
        ------
        ValueError
            If boundaries cannot be determined from the structures.
        """

        min_x, min_y, max_x, max_y = self.get_boundaries()

        self.coordinate_system = CoordinateSystem(
            min_x=min_x, max_x=max_x, min_y=min_y, max_y=max_y, nx=self.resolution, ny=self.resolution
        )
        self.coordinate_system.center(factor=self.boundary_pad_factor)

    def add_fiber(self, *fibers: object) -> None:
        """
        Add fiber structures to the geometry.

        Parameters
        ----------
        fibers : object
            Fiber structures to be added.
        """
        self.fiber_list.extend(fibers)

    def add_structure(self, *structures: object, update_coordinates: bool = True) -> None:
        """
        Add custom structures to the geometry.

        Parameters
        ----------
        structures : object
            Custom structures to be added.
        """
        self.additional_structure_list.extend(structures)

        if update_coordinates:
            self.update_coordinate_system()

        self.mesh = self.generate_mesh()

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

    @property
    def x_bounds(self) -> Tuple[float, float]:
        return self._x_bounds

    @x_bounds.setter
    def x_bounds(self, value: Union[str, Tuple[float, float]]) -> None:
        """
        Interpret the x_bounds parameter and apply the appropriate boundary setting to the coordinate system.

        Raises
        ------
        ValueError
            If x_bounds is invalid.
        """
        if isinstance(value, (list, tuple)):
            self.coordinate_system.x_min, self.coordinate_system.x_max = value

        else:
            match value:
                case 'right':
                    self.coordinate_system.set_right()
                case 'left':
                    self.coordinate_system.set_left()
                case 'centering':
                    self.coordinate_system.x_centering()
                case _:
                    raise ValueError(f"Invalid x_bounds input: {value}. Valid inputs are a list of bounds or one of ['right', 'left', 'centering'].")

        self.mesh = self.generate_mesh()

    @property
    def y_bounds(self) -> Tuple[float, float]:
        return self._y_bounds

    @y_bounds.setter
    def y_bounds(self, value: Union[str, Tuple[float, float]]) -> None:
        """
        Interpret the y_bounds parameter and apply the appropriate boundary setting to the coordinate system.

        Raises
        ------
        ValueError
            If y_bounds is invalid.
        """
        if isinstance(value, (list, tuple)):
            self.coordinate_system.y_min, self.coordinate_system.y_max = value

        else:
            match value:
                case 'top':
                    self.coordinate_system.set_top()
                case 'bottom':
                    self.coordinate_system.set_bottom()
                case 'centering':
                    self.coordinate_system.y_centering()
                case _:
                    raise ValueError(f"Invalid y_bounds input: {value}. Valid inputs are a list of bounds or one of ['top', 'bottom', 'centering'].")

        self.mesh = self.generate_mesh()

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

        self.mesh = self.generate_mesh()

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

        self.mesh = self.generate_mesh()

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
        Render the patch representation of the geometry onto a given matplotlib axis.

        Parameters
        ----------
        ax : plt.Axes, optional
            The matplotlib axis on which the patch representation will be plotted. If not provided, a new axis is created.
        show : bool, optional
            Whether to display the plot immediately. Default is True.

        Returns
        -------
        None
        """
        for structure in self.additional_structure_list:
            structure.plot(ax=ax, show=False)

        for fiber in self.fiber_list:
            fiber.plot(ax=ax, show=False)

        ax.set(title='Fiber structure', xlabel=r'x-distance [m]', ylabel=r'y-distance [m]')
        ax.ticklabel_format(axis='both', style='sci', scilimits=(-6, -6), useOffset=False)

    @_plot_helper
    def plot_raster(self, ax: plt.Axes = None, gamma: float = 5) -> None:
        """
        Render the rasterized representation of the geometry onto a given matplotlib axis.

        Parameters
        ----------
        ax : plt.Axes, optional
            The matplotlib axis on which the rasterized representation will be plotted. If not provided, a new axis is created.
        show : bool, optional
            Whether to display the plot immediately. Default is True.
        gamma : float, optional
            The gamma correction value for the color normalization. Default is 5.

        Returns
        -------
        None
        """
        image = ax.pcolormesh(
            self.coordinate_system.x_vector,
            self.coordinate_system.y_vector,
            self.mesh,
            cmap='Blues',
            norm=colors.PowerNorm(gamma=gamma)
        )

        divider = make_axes_locatable(ax)
        cax = divider.append_axes('right', size='5%', pad=0.05)
        ax.get_figure().colorbar(image, cax=cax, orientation='vertical')

        ax.set(title='Fiber structure', xlabel=r'x-distance [m]', ylabel=r'y-distance [m]')
        ax.ticklabel_format(axis='both', style='sci', scilimits=(-6, -6), useOffset=False)

    def plot(self, show_patch: bool = True, show_mesh: bool = True, show: bool = True, gamma: float = 5) -> plt.Figure:
        """
        Plot the different representations (patch and mesh) of the geometry.

        Parameters
        ----------
        show_patch : bool, optional
            Whether to display the patch representation of the geometry. Default is True.
        show_mesh : bool, optional
            Whether to display the mesh (rasterized) representation of the geometry. Default is True.
        show : bool, optional
            Whether to immediately show the plot. Default is True.
        gamma : float, optional
            The gamma correction value for the color normalization used in the mesh plot. Default is 5.

        Returns
        -------
        plt.Figure
            The matplotlib figure encompassing all the axes used in the plot.
        """
        n_ax = bool(show_patch) + bool(show_mesh)
        unit_size = numpy.array([1, n_ax])

        with plt.style.context(mps):
            figure, axes = plt.subplots(
                *unit_size,
                figsize=5 * numpy.flip(unit_size),
                sharex=True,
                sharey=True,
                subplot_kw=dict(aspect='equal', xlabel='x-distance [m]', ylabel='y-distance [m]'),
            )

        axes_iter = iter(axes.flatten())

        if show_patch:
            ax = next(axes_iter)
            self.plot_patch(ax, show=False)

        if show_mesh:
            ax = next(axes_iter)
            self.plot_raster(ax, show=False, gamma=gamma)

        if show:
            plt.show()

        return figure
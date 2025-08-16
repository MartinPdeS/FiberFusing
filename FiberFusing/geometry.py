#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import List, Optional, Tuple, Union
from enum import Enum
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
from pydantic import field_validator, ConfigDict
from pydantic.dataclasses import dataclass

class BoundaryMode(Enum):
    """Boundary positioning modes."""
    AUTO = "auto"
    LEFT = "left"
    RIGHT = "right"
    TOP = "top"
    BOTTOM = "bottom"
    CENTERING = "centering"


@dataclass(config=ConfigDict(extra='forbid', kw_only=True, arbitrary_types_allowed=True))
class Geometry():
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
    x_bounds : Union[Tuple[float, float], BoundaryMode], optional
        X boundaries for rendering the structure. Can be a tuple of bounds or one of ['auto', 'left', 'right', 'centering']. Default is 'centering'.
    y_bounds : Union[Tuple[float, float], BoundaryMode], optional
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

    # Optional fields with defaults
    background: Optional[BackGround] = None
    fiber_list: List[object] = None
    additional_structure_list: List[object] = None
    x_bounds: Union[Tuple[float, float], BoundaryMode] = BoundaryMode.CENTERING
    y_bounds: Union[Tuple[float, float], BoundaryMode] = BoundaryMode.CENTERING
    resolution: int = 100
    index_scrambling: float = 0.0
    gaussian_filter: Optional[int] = None
    boundary_pad_factor: float = 1.3

    # Internal computed fields
    coordinate_system: Optional[CoordinateSystem] = None
    mesh: Optional[numpy.ndarray] = None

    def __post_init__(self) -> None:
        """Initialize geometry after model validation."""
        if self.background is None:
            self.background = BackGround(index=1.0)
        if self.fiber_list is None:
            self.fiber_list = []
        if self.additional_structure_list is None:
            self.additional_structure_list = []

        self.initialize_geometry()

    @field_validator('resolution')
    @classmethod
    def validate_resolution(cls, v: int) -> int:
        """Validate resolution is positive."""
        if v <= 0:
            raise ValueError('Resolution must be positive')
        return v

    @field_validator('boundary_pad_factor')
    @classmethod
    def validate_boundary_pad_factor(cls, v: float) -> float:
        """Validate boundary pad factor is positive."""
        if v <= 0:
            raise ValueError('Boundary pad factor must be positive')
        return v

    @field_validator('index_scrambling')
    @classmethod
    def validate_index_scrambling(cls, v: float) -> float:
        """Validate index scrambling is non-negative."""
        if v < 0:
            raise ValueError('Index scrambling must be non-negative')
        return v

    def initialize_geometry(self):
        """
        Initialize the geometry by generating the coordinate system and mesh.
        This method calculates the boundaries based on the defined structures and sets up the coordinate system.
        """
        x_min, y_min, x_max, y_max = self.get_boundaries()

        self.coordinate_system = CoordinateSystem(
            x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max, nx=self.resolution, ny=self.resolution
        )

        self.coordinate_system.center(factor=self.boundary_pad_factor)
        self.apply_boundary_settings()
        self.mesh = self.generate_mesh()

    def update_coordinate_system(self) -> None:
        """
        Generate the coordinate system for the mesh construction.

        Raises
        ------
        ValueError
            If boundaries cannot be determined from the structures.
        """
        x_min, y_min, x_max, y_max = self.get_boundaries()

        self.coordinate_system = CoordinateSystem(
            x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max, nx=self.resolution, ny=self.resolution
        )
        self.coordinate_system.center(factor=self.boundary_pad_factor)
        self.apply_boundary_settings()

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

    @field_validator('x_bounds')
    @classmethod
    def validate_x_bounds(cls, v: Union[BoundaryMode, Tuple[float, float]]) -> Union[BoundaryMode, Tuple[float, float]]:
        """Validate x_bounds parameter."""
        if isinstance(v, (list, tuple)):
            if len(v) != 2:
                raise ValueError("x_bounds tuple must have exactly 2 elements")
            if v[0] >= v[1]:
                raise ValueError("x_bounds min must be less than max")
        elif not isinstance(v, BoundaryMode):
            raise ValueError("x_bounds must be a tuple or BoundaryMode")
        return v

    @field_validator('y_bounds')
    @classmethod
    def validate_y_bounds(cls, v: Union[BoundaryMode, Tuple[float, float]]) -> Union[BoundaryMode, Tuple[float, float]]:
        """Validate y_bounds parameter."""
        if isinstance(v, (list, tuple)):
            if len(v) != 2:
                raise ValueError("y_bounds tuple must have exactly 2 elements")
            if v[0] >= v[1]:
                raise ValueError("y_bounds min must be less than max")
        elif not isinstance(v, BoundaryMode):
            raise ValueError("y_bounds must be a tuple or BoundaryMode")
        return v

    def apply_boundary_settings(self) -> None:
        """Apply boundary settings to coordinate system."""
        if hasattr(self, 'coordinate_system') and self.coordinate_system is not None:
            if isinstance(self.x_bounds, (list, tuple)):
                self.coordinate_system.x_min, self.coordinate_system.x_max = self.x_bounds
            elif isinstance(self.x_bounds, BoundaryMode):
                self._apply_x_boundary_mode(self.x_bounds)

            if isinstance(self.y_bounds, (list, tuple)):
                self.coordinate_system.y_min, self.coordinate_system.y_max = self.y_bounds
            elif isinstance(self.y_bounds, BoundaryMode):
                self._apply_y_boundary_mode(self.y_bounds)

    def _apply_x_boundary_mode(self, mode: BoundaryMode) -> None:
        """Apply x boundary mode to coordinate system."""
        match mode:
            case BoundaryMode.RIGHT:
                self.coordinate_system.set_right()
            case BoundaryMode.LEFT:
                self.coordinate_system.set_left()
            case BoundaryMode.CENTERING:
                self.coordinate_system.x_centering()
            case BoundaryMode.AUTO:
                pass  # Keep current bounds
            case _:
                raise ValueError(f"BoundaryMode {mode} not supported for x_bounds")

    def _apply_y_boundary_mode(self, mode: BoundaryMode) -> None:
        """Apply y boundary mode to coordinate system."""
        match mode:
            case BoundaryMode.TOP:
                self.coordinate_system.set_top()
            case BoundaryMode.BOTTOM:
                self.coordinate_system.set_bottom()
            case BoundaryMode.CENTERING:
                self.coordinate_system.y_centering()
            case BoundaryMode.AUTO:
                pass  # Keep current bounds
            case _:
                raise ValueError(f"BoundaryMode {mode} not supported for y_bounds")

    def get_boundaries(self) -> Tuple[float, float, float, float]:
        """
        Calculate the boundaries from the collection of defined structures.

        Returns
        -------
        Tuple[float, float, float, float]
            The boundaries as (x_min, y_min, x_max, y_max).

        Raises
        ------
        ValueError
            If no structures are provided for computing the mesh.
        """
        if not self.additional_structure_list and not self.fiber_list:
            raise ValueError('No internal structures provided for computation of the mesh.')

        x_min, y_min, x_max, y_max = zip(
            *(obj.get_structure_max_min_boundaries() for obj in self.additional_structure_list + self.fiber_list)
        )
        return (numpy.min(x_min), numpy.min(y_min), numpy.max(x_max), numpy.max(y_max))

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

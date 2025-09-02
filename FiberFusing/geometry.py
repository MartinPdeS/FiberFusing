#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import List, Optional, Tuple, Union
from enum import Enum
import numpy
from scipy.ndimage import gaussian_filter
import FiberFusing
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from mpl_toolkits.axes_grid1 import make_axes_locatable
from pydantic import field_validator
from pydantic.dataclasses import dataclass
from MPSPlots import helper


from FiberFusing.coordinate_system import CoordinateSystem
from FiberFusing.utils import config_dict


class DomainAlignment(Enum):
    """Boundary positioning modes."""

    AUTO = "auto"
    LEFT = "left"
    RIGHT = "right"
    TOP = "top"
    BOTTOM = "bottom"
    CENTERING = "centering"


@dataclass(config=config_dict)
class Geometry:
    """
    Represents the refractive index (RI) geometric profile including background and fiber structures.

    Parameters
    ----------
    x_bounds : Union[Tuple[float, float], DomainAlignment], optional
        X boundaries for rendering the structure. Can be a tuple of bounds or one of ['auto', 'left', 'right', 'centering']. Default is 'centering'.
    y_bounds : Union[Tuple[float, float], DomainAlignment], optional
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
    x_bounds: Union[Tuple[float, float], DomainAlignment] = DomainAlignment.CENTERING
    y_bounds: Union[Tuple[float, float], DomainAlignment] = DomainAlignment.CENTERING
    resolution: int = 100
    index_scrambling: float = 0.0
    gaussian_filter: Optional[int] = None
    boundary_pad_factor: float = 1.3

    # Internal computed fields
    coordinate_system: Optional[CoordinateSystem] = None
    mesh: Optional[numpy.ndarray] = None

    def __post_init__(self) -> None:
        """Initialize geometry after model validation."""
        self.structure_list = list()

    def add_structure(self, *structure: object) -> None:
        """
        Add a structure to the internal structure list.

        Parameters
        ----------
        structure : object
            The structure to be added.
        """
        self.structure_list.extend(structure)

    @field_validator("resolution")
    @classmethod
    def validate_resolution(cls, v: int) -> int:
        """Validate resolution is positive."""
        if v <= 0:
            raise ValueError("Resolution must be positive")
        return v

    @field_validator("boundary_pad_factor")
    @classmethod
    def validate_boundary_pad_factor(cls, v: float) -> float:
        """Validate boundary pad factor is positive."""
        if v <= 0:
            raise ValueError("Boundary pad factor must be positive")
        return v

    @field_validator("index_scrambling")
    @classmethod
    def validate_index_scrambling(cls, v: float) -> float:
        """Validate index scrambling is non-negative."""
        if v < 0:
            raise ValueError("Index scrambling must be non-negative")
        return v

    def initialize(self):
        """
        Initialize the geometry by generating the coordinate system and mesh.
        This method calculates the boundaries based on the defined structures and sets up the coordinate system.
        """
        x_min, y_min, x_max, y_max = self.get_boundaries()

        self.coordinate_system = CoordinateSystem(
            x_min=x_min,
            x_max=x_max,
            y_min=y_min,
            y_max=y_max,
            nx=self.resolution,
            ny=self.resolution,
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
            x_min=x_min,
            x_max=x_max,
            y_min=y_min,
            y_max=y_max,
            nx=self.resolution,
            ny=self.resolution,
        )
        self.coordinate_system.center(factor=self.boundary_pad_factor)
        self.apply_boundary_settings()

    @field_validator("x_bounds")
    @classmethod
    def validate_x_bounds(
        cls, v: Union[DomainAlignment, Tuple[float, float]]
    ) -> Union[DomainAlignment, Tuple[float, float]]:
        """Validate x_bounds parameter."""
        if isinstance(v, (list, tuple)):
            if len(v) != 2:
                raise ValueError("x_bounds tuple must have exactly 2 elements")
            if v[0] >= v[1]:
                raise ValueError("x_bounds min must be less than max")
        elif not isinstance(v, DomainAlignment):
            raise ValueError("x_bounds must be a tuple or DomainAlignment")
        return v

    @field_validator("y_bounds")
    @classmethod
    def validate_y_bounds(
        cls, v: Union[DomainAlignment, Tuple[float, float]]
    ) -> Union[DomainAlignment, Tuple[float, float]]:
        """Validate y_bounds parameter."""
        if isinstance(v, (list, tuple)):
            if len(v) != 2:
                raise ValueError("y_bounds tuple must have exactly 2 elements")
            if v[0] >= v[1]:
                raise ValueError("y_bounds min must be less than max")
        elif not isinstance(v, DomainAlignment):
            raise ValueError("y_bounds must be a tuple or DomainAlignment")
        return v

    def apply_boundary_settings(self) -> None:
        """Apply boundary settings to coordinate system."""
        if hasattr(self, "coordinate_system") and self.coordinate_system is not None:
            if isinstance(self.x_bounds, (list, tuple)):
                self.coordinate_system.x_min, self.coordinate_system.x_max = (
                    self.x_bounds
                )
            elif isinstance(self.x_bounds, DomainAlignment):
                self._apply_x_boundary_mode(self.x_bounds)

            if isinstance(self.y_bounds, (list, tuple)):
                self.coordinate_system.y_min, self.coordinate_system.y_max = (
                    self.y_bounds
                )
            elif isinstance(self.y_bounds, DomainAlignment):
                self._apply_y_boundary_mode(self.y_bounds)

    def _apply_x_boundary_mode(self, mode: DomainAlignment) -> None:
        """Apply x boundary mode to coordinate system."""
        match mode:
            case DomainAlignment.RIGHT:
                self.coordinate_system.set_right()
            case DomainAlignment.LEFT:
                self.coordinate_system.set_left()
            case DomainAlignment.CENTERING:
                self.coordinate_system.x_centering()
            case DomainAlignment.AUTO:
                pass  # Keep current bounds
            case _:
                raise ValueError(f"DomainAlignment {mode} not supported for x_bounds")

    def _apply_y_boundary_mode(self, mode: DomainAlignment) -> None:
        """Apply y boundary mode to coordinate system."""
        match mode:
            case DomainAlignment.TOP:
                self.coordinate_system.set_top()
            case DomainAlignment.BOTTOM:
                self.coordinate_system.set_bottom()
            case DomainAlignment.CENTERING:
                self.coordinate_system.y_centering()
            case DomainAlignment.AUTO:
                pass  # Keep current bounds
            case _:
                raise ValueError(f"DomainAlignment {mode} not supported for y_bounds")

    def get_boundaries(self) -> Tuple[float, float, float, float]:
        """
        Calculate the boundaries from the collection of defined structures.

        Returns
        -------
        Tuple[float, float, float, float]
            The boundaries as (x_min, y_min, x_max, y_max).

        """
        filtered_structures = [
            obj
            for obj in self.structure_list
            if not isinstance(obj, FiberFusing.background.BackGround)
        ]

        if len(filtered_structures) == 0:
            raise ValueError(
                "No structures provided (other than background) for computing the mesh."
            )

        x_min, y_min, x_max, y_max = zip(
            *(obj.get_structure_max_min_boundaries() for obj in filtered_structures)
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
        return max(
            refractive_index
            for obj in self.structure_list
            for refractive_index in obj.refractive_index_list
        )

    @property
    def refractive_index_minimum(self) -> float:
        """
        Calculate the minimum refractive index across all non-background structures.

        Returns
        -------
        float
            Minimum refractive index.
        """
        return min(
            refractive_index
            for obj in self.structure_list
            if not isinstance(obj, FiberFusing.background.BackGround)
            for refractive_index in obj.refractive_index_list
        )

    def get_index_range(self) -> List[float]:
        """
        Get a list of all refractive indices associated with the elements of the geometry.

        Returns
        -------
        List[float]
            List of refractive indices.
        """
        return [float(obj.refractive_index) for obj in self.structure_list]

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
                adjustment = (
                    structure.refractive_index
                    * self.refractive_index_scrambling
                    * numpy.random.rand()
                    * random_factor
                )
                structure.refractive_index += adjustment

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

        for structure in self.structure_list:
            structure.overlay_structures_on_mesh(
                mesh=mesh, coordinate_system=self.coordinate_system
            )

        return mesh

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
        if not hasattr(self, "coordinate_system"):
            raise AttributeError(
                "Coordinate system has not been generated. Call generate_coordinate_system() first."
            )

        mesh = self.rasterize_polygons()

        if self.gaussian_filter is not None:
            mesh = gaussian_filter(mesh, sigma=self.gaussian_filter)

        return mesh

    @helper.pre_plot(nrows=1, ncols=1)
    def plot_patch(self, axes: plt.Axes) -> None:
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
        for structure in self.structure_list:
            if isinstance(structure, FiberFusing.background.BackGround):
                continue

            if isinstance(structure, FiberFusing.profile.Profile):
                structure.plot(
                    axes=axes,
                    show=False,
                    show_added=False,
                    show_removed=False,
                    show_centers=False,
                    show_fibers=True,
                )
                continue

            structure.plot(axes=axes, show=False)

        axes.set(
            title="Fiber structure", xlabel=r"x-distance [m]", ylabel=r"y-distance [m]"
        )

    @helper.pre_plot(nrows=1, ncols=1)
    def plot_raster(self, axes: plt.Axes, gamma: float = 5) -> None:
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
        image = axes.pcolormesh(
            self.coordinate_system.x_vector,
            self.coordinate_system.y_vector,
            self.mesh,
            cmap="Blues",
            norm=colors.PowerNorm(gamma=gamma),
        )

        divider = make_axes_locatable(axes)
        cax = divider.append_axes("right", size="5%", pad=0.05)
        axes.get_figure().colorbar(image, cax=cax, orientation="vertical")

        axes.set(
            title="Fiber structure", xlabel=r"x-distance [m]", ylabel=r"y-distance [m]"
        )

    @helper.pre_plot(
        nrows=1,
        ncols=2,
        subplot_kw=dict(
            aspect="equal", xlabel="x-distance [m]", ylabel="y-distance [m]"
        ),
    )
    def plot(self, axes, gamma: float = 5) -> plt.Figure:
        """
        Plot the different representations (patch and mesh) of the geometry.

        Parameters
        ----------
        show : bool, optional
            Whether to immediately show the plot. Default is True.
        gamma : float, optional
            The gamma correction value for the color normalization used in the mesh plot. Default is 5.

        Returns
        -------
        plt.Figure
            The matplotlib figure encompassing all the axes used in the plot.
        """
        axes[0].sharex(axes[1])
        axes[0].sharey(axes[1])

        self.plot_patch(axes=axes[0], show=False)

        self.plot_raster(axes=axes[1], show=False, gamma=gamma)

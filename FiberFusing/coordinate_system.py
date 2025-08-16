#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from typing import Tuple, Optional
from pydantic.dataclasses import dataclass
from pydantic import ConfigDict, field_validator
from dataclasses import field


@dataclass(config=ConfigDict(extra='forbid', strict=True, kw_only=True, arbitrary_types_allowed=True, frozen=False))
class CoordinateSystem:
    """
    A 2D Cartesian coordinate system for fiber optics simulations.

    This class represents a structured 2D grid with customizable boundaries and
    resolution. It provides utilities for mesh generation, coordinate transformations,
    and grid manipulations commonly needed in optical fiber modeling.

    Parameters
    ----------
    nx : int
        Number of grid points along the x-axis. Must be >= 2.
    ny : int
        Number of grid points along the y-axis. Must be >= 2.
    x_min : float
        Minimum x-coordinate of the computational domain.
    x_max : float
        Maximum x-coordinate of the computational domain. Must be > x_min.
    y_min : float
        Minimum y-coordinate of the computational domain.
    y_max : float
        Maximum y-coordinate of the computational domain. Must be > y_min.
    endpoint : bool, optional
        Whether to include the boundary points in the grid. Default is True.

    Attributes
    ----------
    shape : tuple of int
        Grid shape as (ny, nx) following NumPy convention.
    x_bounds : tuple of float
        X-axis boundaries as (x_min, x_max).
    y_bounds : tuple of float
        Y-axis boundaries as (y_min, y_max).
    dx : float
        Grid spacing along x-axis.
    dy : float
        Grid spacing along y-axis.
    x_vector : ndarray
        1D array of x-coordinates.
    y_vector : ndarray
        1D array of y-coordinates.
    x_mesh : ndarray
        2D meshgrid of x-coordinates.
    y_mesh : ndarray
        2D meshgrid of y-coordinates.
    area : float
        Total area of the computational domain.
    aspect_ratio : float
        Aspect ratio of the domain (width/height).

    Examples
    --------
    Create a square coordinate system centered at origin:

    >>> coords = CoordinateSystem(
    ...     nx=101, ny=101,
    ...     x_min=-5e-6, x_max=5e-6,
    ...     y_min=-5e-6, y_max=5e-6
    ... )
    >>> coords.shape
    (101, 101)
    >>> coords.dx
    1e-07

    Create an asymmetric domain:

    >>> coords = CoordinateSystem.from_bounds_and_resolution(
    ...     x_bounds=(-10e-6, 10e-6),
    ...     y_bounds=(-5e-6, 15e-6),
    ...     resolution=0.1e-6
    ... )
    """

    nx: int = field(metadata={"description": "Number of x grid points"})
    ny: int = field(metadata={"description": "Number of y grid points"})
    x_min: float = field(metadata={"description": "Minimum x boundary"})
    x_max: float = field(metadata={"description": "Maximum x boundary"})
    y_min: float = field(metadata={"description": "Minimum y boundary"})
    y_max: float = field(metadata={"description": "Maximum y boundary"})
    endpoint: bool = field(default=True, metadata={"description": "Include boundary points"})

    @field_validator('nx', 'ny')
    @classmethod
    def validate_grid_points(cls, value: int) -> int:
        """Validate that grid points are reasonable."""
        if value < 2:
            raise ValueError(f"Grid points must be >= 2, got {value}")
        if value > 10000:
            raise ValueError(f"Grid points should be <= 10000 for performance, got {value}")
        return value

    @field_validator('x_max')
    @classmethod
    def validate_x_bounds(cls, x_max: float, info) -> float:
        """Validate x boundaries are properly ordered."""
        if hasattr(info, 'data') and 'x_min' in info.data:
            x_min = info.data['x_min']
            if x_max <= x_min:
                raise ValueError(f"x_max ({x_max}) must be > x_min ({x_min})")
        return x_max

    @field_validator('y_max')
    @classmethod
    def validate_y_bounds(cls, y_max: float, info) -> float:
        """Validate y boundaries are properly ordered."""
        if hasattr(info, 'data') and 'y_min' in info.data:
            y_min = info.data['y_min']
            if y_max <= y_min:
                raise ValueError(f"y_max ({y_max}) must be > y_min ({y_min})")
        return y_max

    def __post_init__(self) -> None:
        """Post-initialization validation and setup."""
        self._validate_grid_spacing()

    def _validate_grid_spacing(self) -> None:
        """
        Validate that grid spacing is reasonable for numerical computations.

        Raises
        ------
        ValueError
            If grid spacing is too small or too large.
        """
        if self.dx < 1e-12:
            raise ValueError(f"X grid spacing too small: {self.dx:.2e}. Consider reducing nx or increasing domain size.")
        if self.dy < 1e-12:
            raise ValueError(f"Y grid spacing too small: {self.dy:.2e}. Consider reducing ny or increasing domain size.")

    @classmethod
    def from_bounds_and_resolution(
        cls,
        x_bounds: Tuple[float, float],
        y_bounds: Tuple[float, float],
        resolution: float,
        endpoint: bool = True
    ) -> 'CoordinateSystem':
        """
        Create coordinate system from bounds and desired resolution.

        Parameters
        ----------
        x_bounds : tuple of float
            X-axis boundaries as (x_min, x_max).
        y_bounds : tuple of float
            Y-axis boundaries as (y_min, y_max).
        resolution : float
            Desired grid spacing in both directions.
        endpoint : bool, optional
            Whether to include boundary points. Default is True.

        Returns
        -------
        CoordinateSystem
            New coordinate system instance.

        Examples
        --------
        >>> coords = CoordinateSystem.from_bounds_and_resolution(
        ...     x_bounds=(-5e-6, 5e-6),
        ...     y_bounds=(-5e-6, 5e-6),
        ...     resolution=0.1e-6
        ... )
        """
        x_min, x_max = x_bounds
        y_min, y_max = y_bounds

        nx = int(np.ceil((x_max - x_min) / resolution)) + (1 if endpoint else 0)
        ny = int(np.ceil((y_max - y_min) / resolution)) + (1 if endpoint else 0)

        return cls(
            nx=nx, ny=ny,
            x_min=x_min, x_max=x_max,
            y_min=y_min, y_max=y_max,
            endpoint=endpoint
        )

    @classmethod
    def square_domain(
        cls,
        size: float,
        resolution: float,
        center: Tuple[float, float] = (0.0, 0.0),
        endpoint: bool = True
    ) -> 'CoordinateSystem':
        """
        Create a square computational domain.

        Parameters
        ----------
        size : float
            Side length of the square domain.
        resolution : float
            Grid spacing.
        center : tuple of float, optional
            Center coordinates (x, y). Default is (0, 0).
        endpoint : bool, optional
            Whether to include boundary points. Default is True.

        Returns
        -------
        CoordinateSystem
            New coordinate system instance.

        Examples
        --------
        >>> coords = CoordinateSystem.square_domain(
        ...     size=20e-6,
        ...     resolution=0.1e-6,
        ...     center=(2e-6, -1e-6)
        ... )
        """
        cx, cy = center
        half_size = size / 2

        return cls.from_bounds_and_resolution(
            x_bounds=(cx - half_size, cx + half_size),
            y_bounds=(cy - half_size, cy + half_size),
            resolution=resolution,
            endpoint=endpoint
        )

    @property
    def shape(self) -> Tuple[int, int]:
        """
        Grid shape following NumPy convention (rows, columns).

        Returns
        -------
        tuple of int
            Shape as (ny, nx).
        """
        return (self.ny, self.nx)

    @property
    def x_bounds(self) -> Tuple[float, float]:
        """
        X-axis boundaries.

        Returns
        -------
        tuple of float
            Boundaries as (x_min, x_max).
        """
        return (self.x_min, self.x_max)

    @property
    def y_bounds(self) -> Tuple[float, float]:
        """
        Y-axis boundaries.

        Returns
        -------
        tuple of float
            Boundaries as (y_min, y_max).
        """
        return (self.y_min, self.y_max)

    @property
    def dx(self) -> float:
        """
        Grid spacing along x-axis.

        Returns
        -------
        float
            Spacing between adjacent x grid points.
        """
        if self.nx == 1:
            return 0.0
        return (self.x_max - self.x_min) / (self.nx - 1 if self.endpoint else self.nx)

    @property
    def dy(self) -> float:
        """
        Grid spacing along y-axis.

        Returns
        -------
        float
            Spacing between adjacent y grid points.
        """
        if self.ny == 1:
            return 0.0
        return (self.y_max - self.y_min) / (self.ny - 1 if self.endpoint else self.ny)

    @property
    def area(self) -> float:
        """
        Total area of the computational domain.

        Returns
        -------
        float
            Domain area.
        """
        return (self.x_max - self.x_min) * (self.y_max - self.y_min)

    @property
    def aspect_ratio(self) -> float:
        """
        Aspect ratio of the domain (width/height).

        Returns
        -------
        float
            Aspect ratio.
        """
        width = self.x_max - self.x_min
        height = self.y_max - self.y_min
        return width / height if height != 0 else float('inf')

    @property
    def x_vector(self) -> np.ndarray:
        """
        1D array of x-coordinates.

        Returns
        -------
        ndarray
            Array of x-coordinates with shape (nx,).
        """
        return np.linspace(
            self.x_min, self.x_max,
            num=self.nx,
            endpoint=self.endpoint
        )


    @property
    def y_vector(self) -> np.ndarray:
        """
        1D array of y-coordinates.

        Returns
        -------
        ndarray
            Array of y-coordinates with shape (ny,).
        """
        return np.linspace(
            self.y_min, self.y_max,
            num=self.ny,
            endpoint=self.endpoint
        )

    @property
    def x_mesh(self) -> np.ndarray:
        """
        2D meshgrid of x-coordinates.

        Returns
        -------
        ndarray
            2D array of x-coordinates with shape (ny, nx).
        """
        x_mesh, _ = np.meshgrid(self.x_vector, self.y_vector, indexing='xy')
        return x_mesh

    @property
    def y_mesh(self) -> np.ndarray:
        """
        2D meshgrid of y-coordinates.

        Returns
        -------
        ndarray
            2D array of y-coordinates with shape (ny, nx).
        """
        _, y_mesh = np.meshgrid(self.x_vector, self.y_vector, indexing='xy')
        return y_mesh

    def get_coordinates_flattened(self) -> np.ndarray:
        """
        Get flattened coordinate pairs for unstructured operations.

        Returns
        -------
        ndarray
            Array of coordinate pairs with shape (nx*ny, 2).
            Each row contains [x, y] coordinates.

        Examples
        --------
        >>> coords = CoordinateSystem(nx=3, ny=2, x_min=0, x_max=2, y_min=0, y_max=1)
        >>> pairs = coords.get_coordinates_flattened()
        >>> pairs.shape
        (6, 2)
        """
        coordinates = np.zeros((self.x_vector.size * self.y_vector.size, 2))
        coordinates[:, 0] = self.x_mesh.ravel()
        coordinates[:, 1] = self.y_mesh.ravel()
        return coordinates

    def find_nearest_indices(self, x: float, y: float) -> Tuple[int, int]:
        """
        Find grid indices closest to given coordinates.

        Parameters
        ----------
        x : float
            Target x-coordinate.
        y : float
            Target y-coordinate.

        Returns
        -------
        tuple of int
            Grid indices (i, j) where i is y-index and j is x-index.

        Raises
        ------
        ValueError
            If coordinates are outside the domain.

        Examples
        --------
        >>> coords = CoordinateSystem.square_domain(size=10e-6, resolution=1e-6)
        >>> i, j = coords.find_nearest_indices(1e-6, 2e-6)
        """
        if not (self.x_min <= x <= self.x_max):
            raise ValueError(f"x={x:.2e} is outside domain [{self.x_min:.2e}, {self.x_max:.2e}]")
        if not (self.y_min <= y <= self.y_max):
            raise ValueError(f"y={y:.2e} is outside domain [{self.y_min:.2e}, {self.y_max:.2e}]")

        j = np.argmin(np.abs(self.x_vector - x))
        i = np.argmin(np.abs(self.y_vector - y))
        return i, j

    def get_value_at_indices(self, array: np.ndarray, i: int, j: int) -> float:
        """
        Safely extract value from array at given indices.

        Parameters
        ----------
        array : ndarray
            2D array with shape matching the grid.
        i : int
            Y-index (row).
        j : int
            X-index (column).

        Returns
        -------
        float
            Value at the specified indices.

        Raises
        ------
        ValueError
            If indices are out of bounds or array shape doesn't match grid.
        """
        if array.shape != self.shape:
            raise ValueError(f"Array shape {array.shape} doesn't match grid shape {self.shape}")
        if not (0 <= i < self.ny):
            raise ValueError(f"Y-index {i} out of bounds [0, {self.ny})")
        if not (0 <= j < self.nx):
            raise ValueError(f"X-index {j} out of bounds [0, {self.nx})")

        return array[i, j]

    def interpolate_at_point(self, array: np.ndarray, x: float, y: float) -> float:
        """
        Bilinear interpolation of array values at given coordinates.

        Parameters
        ----------
        array : ndarray
            2D array with values at grid points.
        x : float
            X-coordinate for interpolation.
        y : float
            Y-coordinate for interpolation.

        Returns
        -------
        float
            Interpolated value.

        Raises
        ------
        ValueError
            If coordinates are outside domain or array shape doesn't match.
        """
        if array.shape != self.shape:
            raise ValueError(f"Array shape {array.shape} doesn't match grid shape {self.shape}")

        # Find bounding indices
        j_float = (x - self.x_min) / self.dx
        i_float = (y - self.y_min) / self.dy

        j0 = int(np.floor(j_float))
        i0 = int(np.floor(i_float))
        j1 = min(j0 + 1, self.nx - 1)
        i1 = min(i0 + 1, self.ny - 1)

        # Handle boundary cases
        j0 = max(0, j0)
        i0 = max(0, i0)

        # Interpolation weights
        wx = j_float - j0 if j1 > j0 else 0
        wy = i_float - i0 if i1 > i0 else 0

        # Bilinear interpolation
        v00 = array[i0, j0]
        v01 = array[i0, j1]
        v10 = array[i1, j0]
        v11 = array[i1, j1]

        v0 = v00 * (1 - wx) + v01 * wx
        v1 = v10 * (1 - wx) + v11 * wx

        return v0 * (1 - wy) + v1 * wy

    def ensure_odd_resolution(self, axis: Optional[str] = None) -> 'CoordinateSystem':
        """
        Ensure grid has odd number of points for symmetric operations.

        Parameters
        ----------
        axis : str or None, optional
            Axis to modify ('x', 'y', or None for both). Default is None.

        Returns
        -------
        CoordinateSystem
            New coordinate system with odd resolution.

        Examples
        --------
        >>> coords = CoordinateSystem(nx=100, ny=50, x_min=-5, x_max=5, y_min=-2, y_max=2)
        >>> odd_coords = coords.ensure_odd_resolution()
        >>> odd_coords.nx, odd_coords.ny
        (101, 51)
        """
        nx = self.nx if axis == 'y' else (self.nx + 1 if self.nx % 2 == 0 else self.nx)
        ny = self.ny if axis == 'x' else (self.ny + 1 if self.ny % 2 == 0 else self.ny)

        return CoordinateSystem(
            nx=nx, ny=ny,
            x_min=self.x_min, x_max=self.x_max,
            y_min=self.y_min, y_max=self.y_max,
            endpoint=self.endpoint
        )

    def center_on_origin(self, preserve_size: bool = True) -> 'CoordinateSystem':
        """
        Create coordinate system centered on the origin (immutable).

        Parameters
        ----------
        preserve_size : bool, optional
            If True, preserve the original domain size. If False, make symmetric
            around origin using the maximum absolute boundary. Default is True.

        Returns
        -------
        CoordinateSystem
            New centered coordinate system.

        Examples
        --------
        >>> coords = CoordinateSystem(nx=100, ny=100, x_min=-2, x_max=8, y_min=1, y_max=6)
        >>> centered = coords.center_on_origin(preserve_size=True)
        >>> centered.x_bounds
        (-5.0, 5.0)
        >>> centered.y_bounds
        (-2.5, 2.5)
        """
        if preserve_size:
            x_size = self.x_max - self.x_min
            y_size = self.y_max - self.y_min
            x_min, x_max = -x_size / 2, x_size / 2
            y_min, y_max = -y_size / 2, y_size / 2
        else:
            x_max = max(abs(self.x_min), abs(self.x_max))
            y_max = max(abs(self.y_min), abs(self.y_max))
            x_min, y_min = -x_max, -y_max

        return CoordinateSystem(
            nx=self.nx, ny=self.ny,
            x_min=x_min, x_max=x_max,
            y_min=y_min, y_max=y_max,
            endpoint=self.endpoint
        )

    def scale(self, factor: float) -> 'CoordinateSystem':
        """
        Create scaled coordinate system.

        Parameters
        ----------
        factor : float
            Scaling factor. Must be > 0.

        Returns
        -------
        CoordinateSystem
            New scaled coordinate system.

        Raises
        ------
        ValueError
            If factor <= 0.
        """
        if factor <= 0:
            raise ValueError(f"Scaling factor must be positive, got {factor}")

        return CoordinateSystem(
            nx=self.nx, ny=self.ny,
            x_min=self.x_min * factor,
            x_max=self.x_max * factor,
            y_min=self.y_min * factor,
            y_max=self.y_max * factor,
            endpoint=self.endpoint
        )

    def translate(self, dx: float, dy: float) -> 'CoordinateSystem':
        """
        Create translated coordinate system.

        Parameters
        ----------
        dx : float
            Translation along x-axis.
        dy : float
            Translation along y-axis.

        Returns
        -------
        CoordinateSystem
            New translated coordinate system.
        """
        return CoordinateSystem(
            nx=self.nx, ny=self.ny,
            x_min=self.x_min + dx,
            x_max=self.x_max + dx,
            y_min=self.y_min + dy,
            y_max=self.y_max + dy,
            endpoint=self.endpoint
        )

    def refine(self, factor: int) -> 'CoordinateSystem':
        """
        Create refined coordinate system with higher resolution.

        Parameters
        ----------
        factor : int
            Refinement factor. Must be >= 1.

        Returns
        -------
        CoordinateSystem
            New coordinate system with factor times more grid points.

        Raises
        ------
        ValueError
            If factor < 1.
        """
        if factor < 1:
            raise ValueError(f"Refinement factor must be >= 1, got {factor}")

        nx_new = (self.nx - 1) * factor + 1 if self.endpoint else self.nx * factor
        ny_new = (self.ny - 1) * factor + 1 if self.endpoint else self.ny * factor

        return CoordinateSystem(
            nx=nx_new, ny=ny_new,
            x_min=self.x_min, x_max=self.x_max,
            y_min=self.y_min, y_max=self.y_max,
            endpoint=self.endpoint
        )

    def get_subdomain(
        self,
        x_range: Tuple[float, float],
        y_range: Tuple[float, float]
    ) -> 'CoordinateSystem':
        """
        Extract a subdomain from the current coordinate system.

        Parameters
        ----------
        x_range : tuple of float
            X-axis range as (x_min, x_max).
        y_range : tuple of float
            Y-axis range as (y_min, y_max).

        Returns
        -------
        CoordinateSystem
            New coordinate system covering the specified subdomain.

        Raises
        ------
        ValueError
            If the specified ranges are outside the current domain.
        """
        x_min_new, x_max_new = x_range
        y_min_new, y_max_new = y_range

        # Validate ranges
        if not (self.x_min <= x_min_new < x_max_new <= self.x_max):
            raise ValueError(f"X range {x_range} outside domain {self.x_bounds}")
        if not (self.y_min <= y_min_new < y_max_new <= self.y_max):
            raise ValueError(f"Y range {y_range} outside domain {self.y_bounds}")

        # Calculate new grid sizes maintaining similar resolution
        nx_new = max(2, int(np.round((x_max_new - x_min_new) / self.dx)) + (1 if self.endpoint else 0))
        ny_new = max(2, int(np.round((y_max_new - y_min_new) / self.dy)) + (1 if self.endpoint else 0))

        return CoordinateSystem(
            nx=nx_new, ny=ny_new,
            x_min=x_min_new, x_max=x_max_new,
            y_min=y_min_new, y_max=y_max_new,
            endpoint=self.endpoint
        )

    def is_uniform(self, rtol: float = 1e-10) -> bool:
        """
        Check if the grid has uniform spacing.

        Parameters
        ----------
        rtol : float, optional
            Relative tolerance for comparison. Default is 1e-10.

        Returns
        -------
        bool
            True if grid spacing is uniform in both directions.
        """
        return np.isclose(self.dx, self.dy, rtol=rtol)

    def summary(self) -> str:
        """
        Get a formatted summary of the coordinate system.

        Returns
        -------
        str
            Multi-line string summary with key properties.
        """
        return f"""CoordinateSystem Summary:
Grid Shape: {self.shape} (ny×nx)
X Domain: [{self.x_min:.3e}, {self.x_max:.3e}] with {self.nx} points
Y Domain: [{self.y_min:.3e}, {self.y_max:.3e}] with {self.ny} points
Resolution: dx={self.dx:.3e}, dy={self.dy:.3e}
Area: {self.area:.3e}
Aspect Ratio: {self.aspect_ratio:.3f}
Uniform: {self.is_uniform()}
Endpoint: {self.endpoint}"""

    # ==========================================
    # BACKWARD COMPATIBILITY METHODS (MUTABLE)
    # ==========================================

    def to_unstructured_coordinate(self) -> np.ndarray:
        """
        Get unstructured coordinate representation (backward compatibility).

        Returns
        -------
        ndarray
            Array of coordinate pairs with shape (nx*ny, 2).

        Notes
        -----
        This method is provided for backward compatibility.
        New code should use get_coordinates_flattened().
        """
        return self.get_coordinates_flattened()

    def ensure_odd(self, attribute: str) -> None:
        """
        Ensure the specified grid attribute (nx or ny) is odd (mutable).

        Parameters
        ----------
        attribute : str
            The attribute to update ('nx' or 'ny').

        Raises
        ------
        ValueError
            If the attribute is not 'nx' or 'ny'.
        """
        if attribute not in ['nx', 'ny']:
            raise ValueError("Attribute must be 'nx' or 'ny'.")

        value = getattr(self, attribute)
        if value % 2 == 0:
            object.__setattr__(self, attribute, value + 1)
        self._clear_cache()

    def x_centering(self, zero_included: bool = False) -> None:
        """
        Center the x-axis coordinate system around zero (mutable).

        Parameters
        ----------
        zero_included : bool, optional
            If True, adjusts grid points to include zero. Default is False.
        """
        abs_boundary = max(abs(self.x_min), abs(self.x_max))
        object.__setattr__(self, 'x_min', -abs_boundary)
        object.__setattr__(self, 'x_max', abs_boundary)

        if zero_included:
            self.ensure_odd('nx')
        self._clear_cache()

    def y_centering(self, zero_included: bool = False) -> None:
        """
        Center the y-axis coordinate system around zero (mutable).

        Parameters
        ----------
        zero_included : bool, optional
            If True, adjusts grid points to include zero. Default is False.
        """
        abs_boundary = max(abs(self.y_min), abs(self.y_max))
        object.__setattr__(self, 'y_min', -abs_boundary)
        object.__setattr__(self, 'y_max', abs_boundary)

        if zero_included:
            self.ensure_odd('ny')
        self._clear_cache()

    def center(self, factor: float = 1.0, zero_included: bool = False) -> None:
        """
        Center the coordinate system by scaling the boundaries (mutable).

        Parameters
        ----------
        factor : float, optional
            Scaling factor for the boundaries. Must be greater than 0. Default is 1.0.
        zero_included : bool, optional
            If True, adjust grid points to include zero. Default is False.

        Raises
        ------
        ValueError
            If the scaling factor is not positive.
        """
        if factor <= 0:
            raise ValueError("The scaling factor must be greater than 0.")

        object.__setattr__(self, 'x_min', self.x_min * factor)
        object.__setattr__(self, 'x_max', self.x_max * factor)
        object.__setattr__(self, 'y_min', self.y_min * factor)
        object.__setattr__(self, 'y_max', self.y_max * factor)

        if zero_included:
            self.ensure_odd('nx')
            self.ensure_odd('ny')
        self._clear_cache()

    def add_padding(self, padding_factor: float) -> None:
        """
        Add padding space around the coordinate boundaries (mutable).

        Parameters
        ----------
        padding_factor : float
            Factor by which to pad the boundaries. Must be greater than 1.0.

        Raises
        ------
        ValueError
            If the padding factor is not greater than 1.0.
        """
        if padding_factor <= 1.0:
            raise ValueError("Padding factor must be greater than 1.0.")

        x_center = (self.x_max + self.x_min) / 2
        y_center = (self.y_max + self.y_min) / 2

        x_half_size = (self.x_max - self.x_min) / 2 * padding_factor
        y_half_size = (self.y_max - self.y_min) / 2 * padding_factor

        self.x_min = x_center - x_half_size
        self.x_max = x_center + x_half_size
        self.y_min = y_center - y_half_size
        self.y_max = y_center + y_half_size

        return self

    def update(self, **kwargs) -> None:
        """
        Update the coordinate system attributes and recompute parameters (mutable).

        Parameters
        ----------
        **kwargs : dict
            Attribute-value pairs to update in the coordinate system.

        Raises
        ------
        ValueError
            If an invalid attribute is passed.
        """
        valid_attributes = {'nx', 'ny', 'x_min', 'x_max', 'y_min', 'y_max'}
        for key, value in kwargs.items():
            if key not in valid_attributes:
                raise ValueError(f"Invalid attribute '{key}'. Valid attributes are: {valid_attributes}")
            object.__setattr__(self, key, value)
        self._clear_cache()

    def set_left(self) -> None:
        """
        Set the coordinate system boundaries to align the grid to the left.
        """
        object.__setattr__(self, 'x_max', 0)
        object.__setattr__(self, 'nx', int(self.nx / 2) + 1)
        self._clear_cache()

    def set_right(self) -> None:
        """
        Set the coordinate system boundaries to align the grid to the right.
        """
        object.__setattr__(self, 'x_min', 0)
        object.__setattr__(self, 'nx', int(self.nx / 2) + 1)
        self._clear_cache()

    def set_top(self) -> None:
        """
        Set the coordinate system boundaries to align the grid to the top.
        """
        object.__setattr__(self, 'y_min', 0)
        object.__setattr__(self, 'ny', int(self.ny / 2) + 1)
        self._clear_cache()

    def set_bottom(self) -> None:
        """
        Set the coordinate system boundaries to align the grid to the bottom.
        """
        object.__setattr__(self, 'y_max', 0)
        object.__setattr__(self, 'ny', int(self.ny / 2) + 1)
        self._clear_cache()

    # ==========================================
    # IMMUTABLE METHODS (NEW INTERFACE)
    # ==========================================

    def with_padding(self, padding_factor: float) -> 'CoordinateSystem':
        """
        Create coordinate system with added padding (immutable version).

        This is the preferred method for new code.

        Parameters
        ----------
        padding_factor : float
            Factor by which to expand the domain. Must be > 1.0.

        Returns
        -------
        CoordinateSystem
            New coordinate system with expanded boundaries.
        """
        if padding_factor <= 1.0:
            raise ValueError(f"Padding factor must be > 1.0, got {padding_factor}")

        x_center = (self.x_max + self.x_min) / 2
        y_center = (self.y_max + self.y_min) / 2

        x_half_size = (self.x_max - self.x_min) / 2 * padding_factor
        y_half_size = (self.y_max - self.y_min) / 2 * padding_factor

        return CoordinateSystem(
            nx=self.nx, ny=self.ny,
            x_min=x_center - x_half_size,
            x_max=x_center + x_half_size,
            y_min=y_center - y_half_size,
            y_max=y_center + y_half_size,
            endpoint=self.endpoint
        )

    def __str__(self) -> str:
        """String representation."""
        return f"CoordinateSystem({self.shape}, x∈[{self.x_min:.2e},{self.x_max:.2e}], y∈[{self.y_min:.2e},{self.y_max:.2e}])"

    def __repr__(self) -> str:
        """Detailed string representation."""
        return (f"CoordinateSystem(nx={self.nx}, ny={self.ny}, "
                f"x_min={self.x_min}, x_max={self.x_max}, "
                f"y_min={self.y_min}, y_max={self.y_max}, "
                f"endpoint={self.endpoint})")

    def set_right(self) -> None:
        """
        Set the coordinate system boundaries to align the grid to the left.
        """
        self.x_min = 0
        self.nx = int(self.nx / 2) + 1

    def set_left(self) -> None:
        """
        Set the coordinate system boundaries to align the grid to the right.
        """
        self.x_max = 0
        self.nx = int(self.nx / 2) + 1

    def set_top(self) -> None:
        """
        Set the coordinate system boundaries to align the grid to the top.
        """
        self.y_min = 0
        self.ny = int(self.ny / 2) + 1

    def set_bottom(self) -> None:
        """
        Set the coordinate system boundaries to align the grid to the bottom.
        """
        self.y_max = 0
        self.ny = int(self.ny / 2) + 1

    def y_centering(self, zero_included: bool = False) -> None:
        """
        Center the y-axis coordinate system around zero.

        Parameters
        ----------
        zero_included : bool, optional
            If True, adjusts grid points to include zero. Default is True.
        """
        abs_boundary = max(abs(self.y_min), abs(self.y_max))
        self.y_min, self.y_max = -abs_boundary, abs_boundary

        if zero_included:
            self.ensure_odd('ny')

    def x_centering(self, zero_included: bool = False) -> None:
        """
        Center the x-axis coordinate system around zero.

        Parameters
        ----------
        zero_included : bool, optional
            If True, adjusts grid points to include zero. Default is True.
        """
        abs_boundary = max(abs(self.x_min), abs(self.x_max))
        self.x_min, self.x_max = -abs_boundary, abs_boundary

        if zero_included:
            self.ensure_odd('nx')

    def center(self, factor: float = 1.0, zero_included: bool = False) -> None:
        """
        Center the coordinate system by scaling the boundaries.

        Parameters
        ----------
        factor : float, optional
            Scaling factor for the boundaries. Must be greater than 0. Default is 1.2.
        zero_included : bool, optional
            If True, adjust grid points to include zero. Default is True.

        Raises
        ------
        ValueError
            If the scaling factor is not positive.
        """
        if factor <= 0:
            raise ValueError("The scaling factor must be greater than 0.")

        self.x_min *= factor
        self.x_max *= factor
        self.y_min *= factor
        self.y_max *= factor

        if zero_included:
            self.ensure_odd('nx')
            self.ensure_odd('ny')

    def update(self, **kwargs) -> None:
        """
        Update the coordinate system attributes and recompute parameters.

        Parameters
        ----------
        **kwargs : dict
            Attribute-value pairs to update in the coordinate system.

        Raises
        ------
        ValueError
            If an invalid attribute is passed.
        """
        valid_attributes = {'nx', 'ny', 'x_min', 'x_max', 'y_min', 'y_max'}
        for key, value in kwargs.items():
            if key not in valid_attributes:
                raise ValueError(f"Invalid attribute '{key}'. Valid attributes are: {valid_attributes}")
            setattr(self, key, value)

    def ensure_odd(self, attribute: str) -> None:
        """
        Ensure the specified grid attribute (nx or ny) is odd.

        Parameters
        ----------
        attribute : str
            The attribute to update ('nx' or 'ny').

        Raises
        ------
        ValueError
            If the attribute is not 'nx' or 'ny'.
        """
        if attribute not in ['nx', 'ny']:
            raise ValueError("Attribute must be 'nx' or 'ny'.")

        value = getattr(self, attribute)
        if value % 2 == 0:
            setattr(self, attribute, value + 1)

    def to_unstructured_coordinate(self) -> np.ndarray:
        """
        Get an unstructured coordinate representation of the grid.

        Returns
        -------
        numpy.ndarray
            An unstructured array of coordinates.
        """
        coordinates = np.zeros([self.x_vector.size * self.y_vector.size, 2])
        coordinates[:, 0] = self.x_mesh.ravel()
        coordinates[:, 1] = self.y_mesh.ravel()

        return coordinates
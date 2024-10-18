#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy
from typing import Tuple
from pydantic.dataclasses import dataclass
from pydantic import ConfigDict


@dataclass(config=ConfigDict(extra='forbid', strict=True, kw_only=True))
class CoordinateSystem:
    """
    Represents a 2D coordinate system defined by grid points and boundaries.

    Parameters
    ----------
    nx : int
        The number of grid points along the x-axis.
    ny : int
        The number of grid points along the y-axis.
    min_x : float
        The minimum x-coordinate boundary.
    max_x : float
        The maximum x-coordinate boundary.
    min_y : float
        The minimum y-coordinate boundary.
    max_y : float
        The maximum y-coordinate boundary.
    """

    nx: int
    ny: int
    min_x: float
    max_x: float
    min_y: float
    max_y: float

    def __post_init__(self):
        """
        Initialize the coordinate system boundaries and compute grid parameters.
        """
        self.x_bounds = [self.min_x, self.max_x]
        self.y_bounds = [self.min_y, self.max_y]
        self.compute_parameters()

    def _make_odd(self, attribute: str) -> None:
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
        new_value = (value // 2) * 2 + 1
        self.update(**{attribute: new_value})

    def centering(self, factor: float = 1.2, zero_included: bool = True) -> None:
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

        # Scale the boundaries
        min_bound = min(self.min_x, self.min_y) * factor
        max_bound = max(self.max_x, self.max_y) * factor

        self.min_x = self.min_y = min_bound
        self.max_x = self.max_y = max_bound

        if zero_included:
            self._make_odd('nx')
            self._make_odd('ny')

    def add_padding(self, padding_factor: float) -> None:
        """
        Add padding space around the coordinate boundaries.

        Parameters
        ----------
        padding_factor : float
            Factor by which to pad the boundaries. Must be greater than 0.

        Raises
        ------
        ValueError
            If the padding factor is not positive.
        """
        if padding_factor <= 0:
            raise ValueError("Padding factor must be greater than 0.")

        average_x = (self.min_x + self.max_x) / 2
        difference_x = abs(self.min_x - self.max_x)

        average_y = (self.min_y + self.max_y) / 2
        difference_y = abs(self.min_y - self.max_y)

        self.min_x = average_x - (difference_x * padding_factor) / 2
        self.max_x = average_x + (difference_x * padding_factor) / 2

        self.min_y = average_y - (difference_y * padding_factor) / 2
        self.max_y = average_y + (difference_y * padding_factor) / 2

    def x_centering(self, zero_included: bool = True) -> None:
        """
        Center the x-axis coordinate system around zero.

        Parameters
        ----------
        zero_included : bool, optional
            If True, adjusts grid points to include zero. Default is True.
        """
        abs_boundary = max(abs(self.x_bounds[0]), abs(self.x_bounds[1]))
        self.x_bounds = (-abs_boundary, abs_boundary)

        if zero_included:
            self.make_nx_odd()

    def y_centering(self, zero_included: bool = True) -> None:
        """
        Center the y-axis coordinate system around zero.

        Parameters
        ----------
        zero_included : bool, optional
            If True, adjusts grid points to include zero. Default is True.
        """
        abs_boundary = max(abs(self.y_bounds[0]), abs(self.y_bounds[1]))
        self.y_bounds = (-abs_boundary, abs_boundary)

        if zero_included:
            self.make_ny_odd()

    def set_x_boundary(self, x_bounds: Tuple[float, float]) -> None:
        """
        Set the x-coordinate boundaries.

        Parameters
        ----------
        x_bounds : Tuple[float, float]
            The new boundaries for the x-axis as (min_x, max_x).
        """
        self.x_bounds = x_bounds

    def set_y_boundary(self, y_bounds: Tuple[float, float]) -> None:
        """
        Set the y-coordinate boundaries.

        Parameters
        ----------
        y_bounds : Tuple[float, float]
            The new boundaries for the y-axis as (min_y, max_y).
        """
        self.y_bounds = y_bounds

    def to_unstructured_coordinate(self) -> numpy.ndarray:
        """
        Get an unstructured coordinate representation of the grid.

        Returns
        -------
        numpy.ndarray
            An unstructured array of coordinates.
        """
        coordinates = numpy.zeros([self.x_vector.size * self.y_vector.size, 2])
        coordinates[:, 0] = self.x_mesh.ravel()
        coordinates[:, 1] = self.y_mesh.ravel()

        return coordinates

    def make_nx_odd(self) -> None:
        """
        Adjust nx to be an odd number.
        """
        nx = (self.nx // 2) * 2 + 1
        self.update(nx=nx)

    def make_ny_odd(self) -> None:
        """
        Adjust ny to be an odd number.
        """
        ny = (self.ny // 2) * 2 + 1
        self.update(ny=ny)

    def make_nx_even(self) -> None:
        """
        Adjust nx to be an even number.
        """
        nx = (self.nx // 2) * 2
        self.update(nx=nx)

    def make_ny_even(self) -> None:
        """
        Adjust ny to be an even number.
        """
        ny = (self.ny // 2) * 2
        self.update(ny=ny)

    @property
    def shape(self) -> numpy.ndarray:
        """
        Get the shape of the grid as (ny, nx).

        Returns
        -------
        numpy.ndarray
            The shape of the grid.
        """
        return numpy.array([self.ny, self.nx])

    def set_left(self) -> None:
        """
        Set the coordinate system boundaries to align the grid to the left.
        """
        nx = self.nx // 2 + 1
        self.update(nx=nx, max_x=0)

    def set_right(self) -> None:
        """
        Set the coordinate system boundaries to align the grid to the right.
        """
        nx = self.nx // 2 + 1
        self.update(nx=nx, min_x=0)

    def set_top(self) -> None:
        """
        Set the coordinate system boundaries to align the grid to the top.
        """
        ny = self.ny // 2 + 1
        self.update(ny=ny, min_y=0)

    def set_bottom(self) -> None:
        """
        Set the coordinate system boundaries to align the grid to the bottom.
        """
        ny = self.ny // 2 + 1
        self.update(ny=ny, max_y=0)

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
        valid_attributes = {'nx', 'ny', 'min_x', 'max_x', 'min_y', 'max_y'}
        for key, value in kwargs.items():
            if key not in valid_attributes:
                raise ValueError(f"Invalid attribute '{key}'. Valid attributes are: {valid_attributes}")
            setattr(self, key, value)

        self.compute_parameters()

    def compute_parameters(self) -> None:
        """
        Compute the grid parameters such as step sizes, vectors, and meshes.

        Notes
        -----
        Computes the grid spacing (dx, dy), area element (dA), and vector and mesh representations
        of the grid in Cartesian and polar coordinates (theta and rho).
        """
        self.dx = numpy.abs(self.min_x - self.max_x) / (self.nx - 1)
        self.dy = numpy.abs(self.min_y - self.max_y) / (self.ny - 1)
        self.dA = self.dx * self.dy

        self.x_vector = numpy.linspace(self.min_x, self.max_x, num=self.nx, endpoint=True)
        self.y_vector = numpy.linspace(self.min_y, self.max_y, num=self.ny, endpoint=True)
        self.x_mesh, self.y_mesh = numpy.meshgrid(self.x_vector, self.y_vector)
        self.theta_mesh = numpy.arctan2(self.y_mesh, self.x_mesh)
        self.rho_mesh = numpy.sqrt(self.x_mesh**2 + self.y_mesh**2)

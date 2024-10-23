#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
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

    @property
    def shape(self) -> Tuple[int, int]:
        return (self.ny, self.nx)

    @property
    def x_bounds(self) -> Tuple[float, float]:
        return self.min_x, self.max_x

    @x_bounds.setter
    def x_bounds(self, bounds: Tuple[float, float]):
        self.min_x, self.max_x = bounds

    @property
    def y_bounds(self) -> Tuple[float, float]:
        return self.min_y, self.max_y

    @y_bounds.setter
    def y_bounds(self, bounds: Tuple[float, float]):
        self.min_y, self.max_y = bounds

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

    def y_centering(self, zero_included: bool = False) -> None:
        """
        Center the y-axis coordinate system around zero.

        Parameters
        ----------
        zero_included : bool, optional
            If True, adjusts grid points to include zero. Default is True.
        """
        abs_boundary = max(abs(self.min_y), abs(self.max_y))
        self.min_y, self.max_y = -abs_boundary, abs_boundary

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
        abs_boundary = max(abs(self.min_x), abs(self.max_x))
        self.min_x, self.max_x = -abs_boundary, abs_boundary

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

        self.min_x *= factor
        self.max_x *= factor
        self.min_y *= factor
        self.max_y *= factor

        if zero_included:
            self.ensure_odd('nx')
            self.ensure_odd('ny')

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

        self.min_x -= (self.max_x - self.min_x) * (padding_factor - 1) / 2
        self.max_x += (self.max_x - self.min_x) * (padding_factor - 1) / 2
        self.min_y -= (self.max_y - self.min_y) * (padding_factor - 1) / 2
        self.max_y += (self.max_y - self.min_y) * (padding_factor - 1) / 2

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

    @property
    def dx(self) -> float:
        return self.x_vector[1] - self.x_vector[0]

    @property
    def dy(self) -> float:
        return self.y_vector[1] - self.y_vector[0]

    @property
    def x_bounds(self) -> Tuple:
        return (self.min_x, self.max_x)

    @property
    def y_bounds(self) -> Tuple:
        return (self.min_y, self.max_y)

    @property
    def x_vector(self) -> np.ndarray:
        return np.linspace(*self.x_bounds, num=self.nx, endpoint=True)

    @property
    def y_vector(self) -> np.ndarray:
        return np.linspace(*self.y_bounds, num=self.ny, endpoint=True)

    @property
    def x_mesh(self) -> np.ndarray:
        x_mesh, y_mesh = np.meshgrid(self.x_vector, self.y_vector)

        return x_mesh

    @property
    def y_mesh(self) -> np.ndarray:
        x_mesh, y_mesh = np.meshgrid(self.x_vector, self.y_vector)

        return y_mesh

    def set_right(self) -> None:
        """
        Set the coordinate system boundaries to align the grid to the left.
        """
        self.min_x = 0
        self.nx = int(self.nx / 2) + 1

    def set_left(self) -> None:
        """
        Set the coordinate system boundaries to align the grid to the right.
        """
        self.max_x = 0
        self.nx = int(self.nx / 2) + 1

    def set_top(self) -> None:
        """
        Set the coordinate system boundaries to align the grid to the top.
        """
        self.min_y = 0
        self.ny = int(self.ny / 2) + 1

    def set_bottom(self) -> None:
        """
        Set the coordinate system boundaries to align the grid to the bottom.
        """
        self.max_y = 0
        self.ny = int(self.ny / 2) + 1

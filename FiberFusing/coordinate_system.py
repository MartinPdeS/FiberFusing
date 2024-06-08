#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy
from typing import Tuple
from pydantic.dataclasses import dataclass
from pydantic import ConfigDict


@dataclass(config=ConfigDict(extra='forbid', strict=True), kw_only=True)
class CoordinateSystem(object):
    nx: int
    ny: int
    min_x: float
    max_x: float
    min_y: float
    max_y: float

    def __post_init__(self):
        self.x_bounds = [self.min_x, self.max_x]
        self.y_bounds = [self.min_y, self.max_y]

        self.compute_parameters()

    def centering(self, factor: float = 1.2, zero_included: bool = True) -> None:
        """
        Center the coordinate system by scaling the boundaries.

        Args:
            factor (float): Scaling factor for the boundaries.
            zero_included (bool): If True, adjust grid points to include zero.
        """
        min_bound = min(self.min_x, self.min_y) * factor
        max_bound = min(self.max_x, self.max_y) * factor

        self.min_x = self.min_y = min_bound
        self.max_x = self.max_y = max_bound

        if zero_included:
            self.make_nx_odd()
            self.make_ny_odd()

    def add_padding(self, padding_factor: float) -> None:
        """
        Add padding space around the coordinate boundaries.

        Args:
            padding_factor (float): Factor by which to pad the boundaries.
        """
        average_x = (self.min_x + self.max_x) / 2
        difference_x = abs(self.min_x - self.max_x)

        average_y = (self.min_y + self.max_y) / 2
        difference_y = abs(self.min_y - self.max_y)

        self.min_x = average_x - difference_x * padding_factor / 2,
        self.max_x = average_x + difference_x * padding_factor / 2,

        self.min_y = average_y - difference_y * padding_factor / 2,
        self.max_y = average_y + difference_y * padding_factor / 2,

    def x_centering(self, zero_included: bool = True) -> None:
        """
        Center the x coordinate system around zero.

        Args:
            zero_included (bool): If True, adjust grid points to include zero.
        """
        abs_boundary = abs(self.x_bounds[0]), abs(self.x_bounds[1])
        abs_boundary = max(abs_boundary)

        self.x_bounds = (-abs_boundary, +abs_boundary)

        if zero_included:
            self.make_nx_odd()

    def y_centering(self, zero_included: bool = True) -> None:
        """
        Center the y coordinate system around zero.

        Args:
            zero_included (bool): If True, adjust grid points to include zero.
        """
        abs_boundary = abs(self.y_bounds[0]), abs(self.y_bounds[1])
        abs_boundary = max(abs_boundary)

        self.y_bounds = (-abs_boundary, +abs_boundary)

        if zero_included:
            self.make_ny_odd()

    def set_x_boundary(self, x_bounds: Tuple[float, float]) -> None:
        self.x_bounds = x_bounds

    def set_y_boundary(self, y_bounds: Tuple[float, float]) -> None:
        self.y_bounds = y_bounds

    def to_unstructured_coordinate(self) -> numpy.ndarray:
        """
        Returns an unstructured coordinate representation of the object.

        :returns:   Unstructured coordinate representation of the object.
        :rtype:     numpy.ndarray
        """
        coordinates = numpy.zeros([self.x_vector.size * self.y_vector.size, 2])
        coordinates[:, 0] = self.x_mesh.ravel()
        coordinates[:, 1] = self.y_mesh.ravel()

        return coordinates

    def make_nx_odd(self) -> None:
        nx = (self.nx // 2) * 2 + 1
        self.update(nx=nx)

    def make_ny_odd(self) -> None:
        ny = (self.ny // 2) * 2 + 1
        self.update(ny=ny)

    def make_nx_even(self) -> None:
        nx = (self.nx // 2) * 2
        self.update(nx=nx)

    def make_ny_even(self) -> None:
        ny = (self.ny // 2) * 2
        self.update(ny=ny)

    @property
    def shape(self) -> numpy.ndarray:
        return numpy.array([self.ny, self.nx])

    def set_left(self) -> None:
        nx = self.nx // 2 + 1
        self.update(nx=nx, max_x=0)

    def set_right(self) -> None:
        nx = self.nx // 2 + 1
        self.update(nx=nx, min_x=0)

    def set_top(self) -> None:
        ny = self.ny // 2 + 1
        self.update(ny=ny, min_y=0)

    def set_bottom(self) -> None:
        ny = self.ny // 2 + 1
        self.update(ny=ny, max_y=0)

    def update(self, **kwargs) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)

        self.compute_parameters()

    def compute_parameters(self):
        self.dx = numpy.abs(self.min_x - self.max_x) / (self.nx - 1)
        self.dy = numpy.abs(self.min_y - self.max_y) / (self.ny - 1)
        self.dA = self.dx * self.dy

        self.x_vector = numpy.linspace(self.min_x, self.max_x, num=self.nx, endpoint=True)
        self.y_vector = numpy.linspace(self.min_y, self.max_y, num=self.ny, endpoint=True)
        self.x_mesh, self.y_mesh = numpy.meshgrid(self.x_vector, self.y_vector)
        self.theta_mesh = numpy.arctan2(self.y_mesh, self.x_mesh)
        self.rho_mesh = numpy.sqrt(self.x_mesh**2 + self.y_mesh**2)


# -

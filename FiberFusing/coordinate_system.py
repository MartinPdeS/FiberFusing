#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Built-in imports
import numpy
import matplotlib.pyplot as plt


class CoordinateSystem(object):
    def __init__(self, nx: int, ny: int, min_x: float, max_x: float, min_y: float, max_y: float):
        self._nx = nx
        self._ny = ny

        self._x_bounds = [min_x, max_x]
        self._y_bounds = [min_y, max_y]

    @property
    def min_x(self) -> float:
        return numpy.min(self.x_bounds)

    @property
    def max_x(self) -> float:
        return numpy.max(self.x_bounds)

    @property
    def min_y(self) -> float:
        return numpy.min(self.y_bounds)

    @property
    def max_y(self) -> float:
        return numpy.max(self.y_bounds)

    def centering(self, factor: float = 1.2, zero_included: bool = True) -> None:
        min_bound = min(self.x_bounds[0], self.y_bounds[0]) * factor
        max_bound = min(self.x_bounds[1], self.y_bounds[1]) * factor

        self._x_bounds = self._y_bounds = (min_bound, max_bound)

        if zero_included:
            self.make_nx_odd()
            self.make_ny_odd()

    def add_padding(self, padding_factor: float) -> None:
        """
        Adds a padding space between the .

        :param      padding_factor:  The padding factor
        :type       padding_factor:  float

        :returns:   No returns
        :rtype:     None
        """
        average_x = (self.min_x + self.max_x) / 2
        difference_x = abs(self.min_x - self.max_x)

        average_y = (self.min_y + self.max_y) / 2
        difference_y = abs(self.min_y - self.max_y)

        self.x_bounds = [
            average_x - difference_x * padding_factor / 2,
            average_x + difference_x * padding_factor / 2,
        ]

        self.y_bounds = [
            average_y - difference_y * padding_factor / 2,
            average_y + difference_y * padding_factor / 2,
        ]

    def x_centering(self, zero_included: bool = True) -> None:
        """
        Center the x coordinate system around 0

        :param      zero_included:  Indicates if zero included
        :type       zero_included:  bool

        :returns:   No returns
        :rtype:     None
        """
        abs_boundary = abs(self.x_bounds[0]), abs(self.x_bounds[1])
        abs_boundary = max(abs_boundary)

        self._x_bounds = (-abs_boundary, +abs_boundary)

        if zero_included:
            self.make_nx_odd()

    def y_centering(self, zero_included: bool = True) -> None:
        """
        Center the y coordinate system around 0

        :param      zero_included:  Indicates if zero included
        :type       zero_included:  bool

        :returns:   No returns
        :rtype:     None
        """
        abs_boundary = abs(self.y_bounds[0]), abs(self.y_bounds[1])
        abs_boundary = max(abs_boundary)

        self._y_bounds = (-abs_boundary, +abs_boundary)

        if zero_included:
            self.make_ny_odd()

    def set_x_boundary(self, x_bounds: list):
        self._x_bounds = x_bounds

    def set_y_boundary(self, y_bounds: list):
        self._y_bounds = y_bounds

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
        self.nx = self.to_odd(self.nx)

    def make_ny_odd(self) -> None:
        self.ny = self.to_odd(self.ny)

    def make_nx_even(self) -> None:
        self.nx = self.to_even(self.nx)

    def make_ny_even(self) -> None:
        self.ny = self.to_even(self.ny)

    @property
    def shape(self) -> numpy.ndarray:
        return numpy.array([self.ny, self.nx])

    @property
    def dA(self) -> float:
        return self.dx * self.dy

    @property
    def rho_mesh(self) -> numpy.ndarray:
        return numpy.sqrt(self.x_mesh**2 + self.y_mesh**2)

    @property
    def theta_mesh(self) -> numpy.ndarray:
        return numpy.arctan2(self.y_mesh, self.x_mesh)

    def set_left(self) -> None:
        self._nx = self._nx // 2 + 1
        self.x_bounds = (self.x_bounds[0], 0)

    def set_right(self) -> None:
        self._nx = self._nx // 2 + 1
        self.x_bounds = (0, self.x_bounds[1])

    def set_top(self) -> None:
        self._ny = self._ny // 2 + 1
        self.y_bounds = (0, self.x_bounds[1])

    def set_bottom(self) -> None:
        self._ny = self._ny // 2 + 1
        self.y_bounds = (self.x_bounds[0], 0)

    # nx property------------
    @property
    def nx(self) -> int:
        return self._nx

    @nx.setter
    def nx(self, value) -> None:
        self._nx = value

    # ny property------------
    @property
    def ny(self) -> int:
        return self._ny

    @ny.setter
    def ny(self, value) -> None:
        self._ny = value

    # dx property------------
    @property
    def dx(self) -> numpy.ndarray:
        return numpy.abs(self.x_bounds[0] - self.x_bounds[1]) / (self.nx - 1)

    # dy property------------
    @property
    def dy(self) -> numpy.ndarray:
        return numpy.abs(self.y_bounds[0] - self.y_bounds[1]) / (self.ny - 1)

    @property
    def x_vector(self) -> numpy.ndarray:
        return numpy.linspace(*self.x_bounds, num=self.nx, endpoint=True)

    @property
    def y_vector(self) -> numpy.ndarray:
        return numpy.linspace(*self.y_bounds, num=self.ny, endpoint=True)

    @property
    def x_mesh(self):
        x_mesh, _ = numpy.meshgrid(self.x_vector, self.y_vector)

        return x_mesh

    @property
    def y_mesh(self):
        _, y_mesh = numpy.meshgrid(self.x_vector, self.y_vector)

        return y_mesh

    # x_bound property------------
    @property
    def x_bounds(self) -> tuple:
        return self._x_bounds

    @x_bounds.setter
    def x_bounds(self, value) -> None:
        self._x_bounds = value

    # y_bound property------------
    @property
    def y_bounds(self) -> tuple:
        return self._y_bounds

    @y_bounds.setter
    def y_bounds(self, value) -> None:
        self._y_bounds = value

    def to_odd(self, value: int) -> int:
        return (value // 2) * 2 + 1

    def to_even(self, value: int) -> int:
        return (value // 2) * 2

    def plot(self):
        figure, ax = plt.subplots(1, 1)
        ax.grid('on')
        ax.set_xticks(self.x_vector)
        ax.set_yticks(self.y_vector)
        ax.set_xlim(self.x_bounds)
        ax.set_ylim(self.y_bounds)
        ax.set_title('Mesh grid')
        ax.set_xlabel('x-direction')
        ax.set_ylabel('y-direction')
        ax.set_aspect('equal')
        plt.show()

# -

#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Built-in imports
from typing import Optional, Tuple, Self
import numpy
from pydantic.dataclasses import dataclass
import shapely.geometry as geo
import matplotlib.pyplot as plt
from MPSPlots import helper

from FiberFusing import geometries
from FiberFusing.utils import config_dict

@dataclass(config=config_dict)
class Point(geometries.base_class.Alteration):
    position: Optional[Tuple[float, float]] = None
    instance: Optional[geo.Point] = None
    index: Optional[float] = None

    def __post_init__(self):
        """
        Initializes the Point with either a tuple of coordinates or an existing Shapely Point instance.
        """
        if (self.position is None) == (self.instance is None):
            raise ValueError("Point must be instantiated with either 'position' or 'instance', not both.")

        self._shapely_object = self.instance if self.instance is not None else geo.Point(self.position)

    @property
    def x(self) -> float:
        """Returns the x-coordinate of the point."""
        return self._shapely_object.x

    @property
    def y(self) -> float:
        """Returns the y-coordinate of the point."""
        return self._shapely_object.y

    def shift_position(self, shift: Tuple[float, float]) -> Self:
        """
        Shifts the point by a given offset and returns a new Point instance.

        Parameters
        ----------
        shift : tuple of float
            The (x, y) offset to shift the point by.

        Returns
        -------
        Point
            A new Point instance representing the shifted position.
        """
        point_shift = geometries.utils.interpret_to_point(shift)
        return self.__add__(point_shift)

    def __add__(self, other) -> Self:
        """
        Adds the coordinates of another point to this one and returns a new Point instance.

        Parameters
        ----------
        other : Point
            The other point to add.

        Returns
        -------
        Point
            A new Point instance representing the sum of the two points.
        """
        other = geometries.utils.interpret_to_point(other)

        return Point(position=(self.x + other.x, self.y + other.y))

    def __sub__(self, other) -> Self:
        """
        Subtracts the coordinates of another point from this one and returns a new Point instance.
        """
        other = geometries.utils.interpret_to_point(other)
        return Point(position=(self.x - other.x, self.y - other.y))

    def __neg__(self) -> Self:
        """
        Negates the coordinates of this point and returns a new Point instance.
        """
        return Point(position=[-self.x, -self.y])

    def __mul__(self, factor: float) -> Self:
        """
        Multiplies the coordinates of this point by a scalar and returns a new Point instance.
        """
        return Point(position=[self.x * factor, self.y * factor])

    def distance(self, other: Self) -> float:
        """
        Computes the Euclidean distance between this point and another point.

        Parameters
        ----------
        other : Point
            The other point to compute the distance to.

        Returns
        -------
        float
            The Euclidean distance between the two points.
        """
        return numpy.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

    @helper.pre_plot(nrows=1, ncols=1)
    def plot(self, axes: plt.Axes, marker: str = 'x', size: int = 20, label: str = None) -> None:
        """
        Renders this point on the given axis, optionally with text.

        Parameters
        ----------
        ax : plt.Axes
            The Matplotlib axis to render the point on.
        marker : str
            The marker style for the point.
        size : int
            The size of the point marker.
        label : str
            The label for the point, if any.
        """
        axes.scatter(self.x, self.y, label=label, marker=marker, s=size)

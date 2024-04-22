#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Built-in imports
import numpy
from typing import Self

from dataclasses import dataclass
from FiberFusing.components.base_class import Alteration
import shapely.geometry as geo
from MPSPlots.render2D import SceneList, Axis
import FiberFusing as ff


@dataclass
class Point(Alteration):
    position: list | None = None
    instance: geo.Point | None = None
    index: float | None = None

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

    def shift_position(self, shift: tuple[float, float]) -> Self:
        """
        Shifts the point by a given offset and returns a new Point instance.
        """
        point_shift = ff.components.utils.interpret_to_point(shift)
        return self.__add__(point_shift)

    def __add__(self, other) -> Self:
        """
        Adds the coordinates of another point to this one and returns a new Point instance.
        """
        other = ff.components.utils.interpret_to_point(other)

        return Point(position=(self.x + other.x, self.y + other.y))

    def __sub__(self, other) -> Self:
        """
        Subtracts the coordinates of another point from this one and returns a new Point instance.
        """
        other = ff.components.utils.interpret_to_point(other)
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

    def distance(self, other) -> float:
        """
        Computes the Euclidean distance between this point and another point.
        """
        return numpy.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

    def render_on_axis(self, ax: Axis, text: str = None, text_shift: tuple = (1.01, 1.01), **kwargs) -> None:
        """
        Renders this point on the given axis, optionally with text.
        """
        ax.add_scatter(x=self.x, y=self.y, **kwargs)

        if text is not None:
            ax.add_text(
                position=(self.x * text_shift[0], self.y * text_shift[1]),
                text=text
            )

    def plot(self, **kwargs) -> SceneList:
        """
        Plots the point within a new plotting scene.
        """
        figure = SceneList(unit_size=(6, 6))

        ax = figure.append_ax(x_label='x', y_label='y')

        self._render_on_ax_(ax)

        return figure

# -

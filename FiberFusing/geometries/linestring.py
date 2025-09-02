#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Optional, Tuple, Self
import numpy as np
from pydantic.dataclasses import dataclass
from dataclasses import field
from shapely.affinity import scale
import shapely.geometry as geo

from FiberFusing.geometries.base_class import Alteration
from FiberFusing.utils import config_dict
import geometries

@dataclass(config=config_dict)
class LineString(Alteration):
    coordinates: Optional[Tuple] = field(default=None, repr=False)
    instance: Optional[geo.LineString] = field(default=None, repr=False)
    index: Optional[float] = field(default=None)

    def __post_init__(self):
        """
        Initialize a LineString object either from coordinates or a Shapely LineString instance.
        """
        if not ((self.coordinates is None) ^ (self.instance is None)):
            raise ValueError("Must initialize LineString with either 'coordinates' or 'instance', not both.")

        if self.instance is not None:
            self._shapely_object = self.instance
        else:
            if len(self.coordinates) != 2:
                raise ValueError('LineString must be initialized with exactly two coordinate pairs.')
            _coordinates = (self.coordinates[0]._shapely_object, self.coordinates[1]._shapely_object)
            self._shapely_object = geo.LineString(_coordinates)

    @property
    def boundary(self) -> Tuple[geo.Point, geo.Point]:
        """ Returns the boundary points of the line string as a tuple of Shapely Point objects. """
        return self._shapely_object.boundary.geoms

    @property
    def center(self) -> geo.Point:
        """ Returns the centroid of the line as a Shapely Point object. """
        return self._shapely_object.centroid

    @property
    def mid_point(self) -> 'geometries.Point':
        """ Returns the midpoint of the line string as a Shapely Point object. """
        P0, P1 = self.boundary
        return geometries.Point(position=[(P0.x + P1.x) / 2, (P0.y + P1.y) / 2])

    @property
    def length(self) -> float:
        """ Returns the length of the line string. """
        return self._shapely_object.length

    def intersect(self, other: Self) -> None:
        """
        Intersects this line string with another, updating the shapely object in place.

        Parameters
        ----------
        other : LineString
            The other line string to intersect with.

        """
        self._shapely_object = self._shapely_object.intersection(other._shapely_object)

    def get_perpendicular(self) -> Self:
        """ Returns a new LineString object that is perpendicular to this one. """
        mid = self.mid_point
        p0, p1 = self.boundary
        dx, dy = p1.x - p0.x, p1.y - p0.y
        new_coords = geometries.Point(position=(mid.x - dy, mid.y + dx)), geometries.Point(position=(mid.x + dy, mid.y - dx))
        return LineString(coordinates=new_coords)

    def get_position_parametrization(self, t: float) -> 'geometries.Point':
        """
        Returns the point at parameter t along the line. 0 <= t <= 1.

        Parameters
        ----------
        t : float
            The parameter along the line, where 0 <= t <= 1.

        Returns
        -------
        geometries.Point
            The point at parameter t along the line.
        """
        p0, p1 = self.boundary
        x = p0.x * (1 - t) + p1.x * t
        y = p0.y * (1 - t) + p1.y * t
        return geometries.Point(position=(x, y))

    def render_on_axis(self, ax, **kwargs) -> None:
        """
        Renders the line string on a given matplotlib axis.

        Parameters
        ----------
        ax : matplotlib.axes.Axes
            The axes to render the line string on.
        **kwargs : keyword arguments
            Additional keyword arguments to pass to the plot function.
        """
        x, y = self._shapely_object.xy
        ax.plot(x, y, **kwargs)

    def make_length(self, length: float) -> Self:
        """ Returns a new LineString scaled to the specified length. """
        return self.extend(factor=length / self.length)

    def centering(self, center: geo.Point) -> Self:
        """
        Centers the line string at a given point.

        Parameters
        ----------
        center : geo.Point
            The point to center the line string around.

        Returns
        -------
        LineString
            A new LineString centered at the specified point.
        """
        p0, p1 = self.boundary
        mid = self.mid_point
        dx, dy = center.x - mid.x, center.y - mid.y
        new_coords = [(p.x + dx, p.y + dy) for p in [p0, p1]]
        new_coords = geometries.Point(position=new_coords[0]), geometries.Point(position=new_coords[1])
        return LineString(coordinates=tuple(new_coords))

    def get_vector(self) -> np.ndarray:
        """ Returns a unit vector representing the direction of the line string. """
        p0, p1 = self.boundary
        dx, dy = p1.x - p0.x, p1.y - p0.y
        norm = np.sqrt(dx**2 + dy**2)
        return np.array([dx, dy]) / norm if norm != 0 else np.array([0, 0])

    def extend(self, factor: float = 1) -> Self:
        """
        Returns a new LineString scaled by the specified factor.

        Parameters
        ----------
        factor : float
            The scaling factor to apply to the line string.

        Returns
        """
        scaled_string = scale(self._shapely_object, xfact=factor, yfact=factor, origin='center')
        return LineString(instance=scaled_string)

# -

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
import numpy as np
from typing import Iterable, Tuple
from shapely import affinity
import shapely.geometry as geo
from FiberFusing.coordinate_system import CoordinateSystem
from shapely.ops import split
import FiberFusing as ff


class Alteration:
    def in_place_copy(func):
        """
        Decorator to manage in-place operations.

        Parameters
        ----------
        func : callable
            The function to wrap.

        Returns
        -------
        callable
            Wrapped function that optionally modifies the object in-place.
        """
        def wrapper(self, *args, in_place=False, **kwargs):
            instance = self if in_place else self.copy()
            return func(self, instance, *args, **kwargs)
        return wrapper

    def copy(self) -> 'Alteration':
        """
        Create a deep copy of the object.

        Returns
        -------
        Alteration
            A new instance that is a deep copy of the current object.
        """
        return copy.deepcopy(self)

    def __repr__(self) -> str:
        """
        Return the string representation of the shapely object.

        Returns
        -------
        str
            The string representation of the shapely object.
        """
        return repr(self._shapely_object)

    @property
    def is_empty(self) -> bool:
        """
        Check if the shapely object is empty.

        Returns
        -------
        bool
            True if the object is empty, False otherwise.
        """
        return self._shapely_object.is_empty

    @in_place_copy
    def union(self, output, *others) -> 'Alteration':
        """
        Perform the union operation with other geometries.

        Parameters
        ----------
        output : Alteration
            The object to store the result.
        *others : Alteration
            Other geometries to union with.

        Returns
        -------
        Alteration
            The union of the geometries.
        """
        other_shapes = (o._shapely_object for o in others)
        output._shapely_object = self._shapely_object.union(*other_shapes)
        return output

    @in_place_copy
    def intersection(self, output, *others) -> 'Alteration':
        """
        Perform the intersection operation with other geometries.

        Parameters
        ----------
        output : Alteration
            The object to store the result.
        *others : Alteration
            Other geometries to intersect with.

        Returns
        -------
        Alteration
            The intersection of the geometries.
        """
        other_shapes = (o._shapely_object for o in others)
        output._shapely_object = self._shapely_object.intersection(*other_shapes)
        return output

    @in_place_copy
    def scale(self, output, factor: float, origin: Tuple[float, float] = (0, 0)) -> 'Alteration':
        """
        Scale the geometry by a given factor.

        Parameters
        ----------
        output : Alteration
            The object to store the result.
        factor : float
            The scaling factor.
        origin : tuple of float, optional
            The origin point for scaling, by default (0, 0).

        Returns
        -------
        Alteration
            The scaled geometry.
        """
        origin_point = ff.components.utils.interpret_to_point(origin)
        output._shapely_object = affinity.scale(self._shapely_object, xfact=factor, yfact=factor, origin=origin_point._shapely_object)
        return output

    @in_place_copy
    def translate(self, output, shift: Tuple[float, float]) -> 'Alteration':
        """
        Translate the geometry by a given shift.

        Parameters
        ----------
        output : Alteration
            The object to store the result.
        shift : tuple of float
            The (x, y) shift values.

        Returns
        -------
        Alteration
            The translated geometry.
        """
        shift_point = ff.components.utils.interpret_to_point(shift)
        output._shapely_object = affinity.translate(self._shapely_object, shift_point.x, shift_point.y)
        return output

    @in_place_copy
    def rotate(self, output, angle: float, origin: Tuple[float, float] = (0, 0)) -> 'Alteration':
        """
        Rotate the geometry by a specified angle around an origin.

        Parameters
        ----------
        output : Alteration
            The object to store the result.
        angle : float
            The rotation angle in degrees.
        origin : tuple of float, optional
            The origin point for rotation, by default (0, 0).

        Returns
        -------
        Alteration
            The rotated geometry.
        """
        origin_point = ff.components.utils.interpret_to_point(origin)
        output._shapely_object = affinity.rotate(self._shapely_object, angle=angle, origin=origin_point._shapely_object)
        return output


class BaseArea(Alteration):
    @property
    def is_iterable(self) -> bool:
        """
        Check if the shapely object is iterable.

        Returns
        -------
        bool
            True if the object is iterable, False otherwise.
        """
        return isinstance(self._shapely_object, Iterable)

    @property
    def is_multi(self) -> bool:
        """
        Check if the shapely object is a MultiPolygon.

        Returns
        -------
        bool
            True if the object is a MultiPolygon, False otherwise.
        """
        return isinstance(self._shapely_object, geo.MultiPolygon)

    @property
    def is_empty(self) -> bool:
        """
        Check if the shapely object is empty.

        Returns
        -------
        bool
            True if the object is empty, False otherwise.
        """
        return self._shapely_object.is_empty

    @property
    def is_pure_polygon(self) -> bool:
        """
        Check if the shapely object is a pure Polygon.

        Returns
        -------
        bool
            True if the object is a pure Polygon, False otherwise.
        """
        return isinstance(self._shapely_object, geo.Polygon)

    @property
    def exterior(self):
        """
        Get the exterior boundary of the polygon.

        Returns
        -------
        LinearRing
            The exterior boundary of the polygon.
        """
        return self._shapely_object.exterior

    def get_rasterized_mesh(self, coordinate_system: CoordinateSystem) -> np.ndarray:
        """
        Rasterize the shape based on the given coordinate system.

        Parameters
        ----------
        coordinate_system : CoordinateSystem
            The coordinate system used for rasterization.

        Returns
        -------
        numpy.ndarray
            The rasterized shape as a mesh.
        """
        raster = self.rasterize(coordinate_system=coordinate_system)
        raster = raster.reshape(coordinate_system.shape)
        return raster.astype(np.float64)

    @property
    def convex_hull(self) -> geo.Polygon:
        """
        Get the convex hull of the shape.

        Returns
        -------
        Polygon
            The convex hull as a Polygon.
        """
        return ff.Polygon(instance=self._shapely_object.convex_hull)

    @property
    def area(self) -> float:
        """
        Calculate the area of the shape.

        Returns
        -------
        float
            The area of the shape.
        """
        return self._shapely_object.area

    @property
    def bounds(self) -> Tuple[float, float, float, float]:
        """
        Get the bounds of the shape.

        Returns
        -------
        tuple of float
            The (minx, miny, maxx, maxy) bounds of the shape.
        """
        return self._shapely_object.bounds

    @property
    def center(self) -> geo.Point:
        """
        Get the center (centroid) of the shape.

        Returns
        -------
        Point
            The centroid of the shape as a Point.
        """
        return ff.Point(position=(self._shapely_object.centroid.x, self._shapely_object.centroid.y))

    def __add__(self, other: 'BaseArea') -> 'BaseArea':
        """
        Add two geometries together using union.

        Parameters
        ----------
        other : BaseArea
            The other geometry to union with.

        Returns
        -------
        BaseArea
            The union of the two geometries.
        """
        output = self.copy()
        output._shapely_object = self._shapely_object.union(other._shapely_object)
        return output

    def __sub__(self, other: 'BaseArea') -> 'BaseArea':
        """
        Subtract one geometry from another.

        Parameters
        ----------
        other : BaseArea
            The geometry to subtract.

        Returns
        -------
        BaseArea
            The difference of the two geometries.
        """
        output = self.copy()
        output._shapely_object = self._shapely_object.difference(other._shapely_object)
        return output

    def __and__(self, other: 'BaseArea') -> 'BaseArea':
        """
        Perform the intersection operation.

        Parameters
        ----------
        other : BaseArea
            The geometry to intersect with.

        Returns
        -------
        BaseArea
            The intersection of the two geometries.
        """
        output = self.copy()
        output._shapely_object = self._shapely_object.intersection(other._shapely_object)
        return output

    def scale_position(self, factor: float) -> 'BaseArea':
        """
        Scale the position of the shape.

        Parameters
        ----------
        factor : float
            The scaling factor for the shape's position.

        Returns
        -------
        BaseArea
            The scaled shape.
        """
        new_position = affinity.scale(
            self.center._shapely_object,
            xfact=factor,
            yfact=factor,
            origin=(0, 0)
        )

        shift = (new_position.x - self.center.x, new_position.y - self.center.y)

        self.core.translate(shift=shift, in_place=True)
        self.translate(shift=shift, in_place=True)

        return self

    def shift_position(self, shift: Tuple[float, float], inplace: bool = True) -> 'BaseArea':
        """
        Shift the position of the shape.

        Parameters
        ----------
        shift : tuple of float
            The (x, y) shift values.

        Returns
        -------
        BaseArea
            The shifted shape.
        """
        if hasattr(self, 'core'):
            self.core.translate(shift=shift, in_place=inplace)
        self.translate(shift=shift, in_place=inplace)
        return self

    def split_with_line(self, line, return_largest: bool = True) -> 'ff.Polygon':
        """
        Split the shape using a line.

        Parameters
        ----------
        line : LineString
            The line used for splitting the shape.
        return_largest : bool, optional
            If True, returns the largest resulting polygon. Otherwise, returns the smallest. Default is True.

        Returns
        -------
        ff.Polygon
            The resulting polygon based on the split.

        Raises
        ------
        ValueError
            If the shape is not a pure polygon.
        """
        if not self.is_pure_polygon:
            raise ValueError(f"Error: expected a pure polygon, but got {self._shapely_object.__class__}.")

        split_geometry = split(self._shapely_object, line.copy().extend(factor=100)._shapely_object).geoms
        areas = [poly.area for poly in split_geometry]
        idx = np.argmax(areas) if return_largest else np.argmin(areas)

        return ff.Polygon(instance=split_geometry[idx])

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Tuple, Callable, Self
import copy
from shapely import affinity

import FiberFusing as ff


class Alteration:
    def in_place_copy(function: Callable) -> Callable:
        """
        Decorator to manage in-place operations.

        Parameters
        ----------
        function : Callable
            The function to wrap.

        Returns
        -------
        Callable
            Wrapped function that optionally modifies the object in-place.
        """
        def wrapper(self, *args, in_place=False, **kwargs):
            instance = self if in_place else self.copy()
            return function(self, instance, *args, **kwargs)

        return wrapper

    def copy(self) -> Self:
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
    def intersection(self, output, *others) -> Self:
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
    def scale(self, output, factor: float, origin: Tuple[float, float] = (0, 0)) -> Self:
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
        origin_point = ff.geometries.utils.interpret_to_point(origin)
        output._shapely_object = affinity.scale(self._shapely_object, xfact=factor, yfact=factor, origin=origin_point._shapely_object)
        return output

    @in_place_copy
    def translate(self, output, shift: Tuple[float, float]) -> Self:
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
        shift_point = ff.geometries.utils.interpret_to_point(shift)
        output._shapely_object = affinity.translate(self._shapely_object, shift_point.x, shift_point.y)
        return output

    @in_place_copy
    def rotate(self, output, angle: float, origin: Tuple[float, float] = (0, 0)) -> Self:
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
        origin_point = ff.geometries.utils.interpret_to_point(origin)
        output._shapely_object = affinity.rotate(self._shapely_object, angle=angle, origin=origin_point._shapely_object)
        return output

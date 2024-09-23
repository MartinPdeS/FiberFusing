#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
from typing import Iterable, Tuple
import numpy
from shapely import affinity
import shapely.geometry as geo
from FiberFusing.coordinate_system import CoordinateSystem
from shapely.ops import split
import FiberFusing as ff


class Alteration():
    def in_place_copy(function, *args, **kwargs):
        def wrapper(self, *args, in_place=False, **kwargs):
            if in_place:
                output = self
            else:
                output = self.copy()
            return function(self, output, *args, **kwargs)

        return wrapper

    def copy(self) -> 'Alteration':
        return copy.deepcopy(self)

    def __repr__(self) -> str:
        return self._shapely_object.__repr__()

    @property
    def is_empty(self) -> bool:
        return self._shapely_object.is_empty

    @in_place_copy
    def union(self, output, *others) -> 'Alteration':
        others = tuple(o._shapely_object for o in others)
        output._shapely_object = self._shapely_object.union(*others)
        return output

    @in_place_copy
    def intersection(self, output, *others) -> 'Alteration':
        others = tuple(o._shapely_object for o in others)
        output._shapely_object = self._shapely_object.intersection(*others)
        return output

    @in_place_copy
    def scale(self, output, factor: float, origin: tuple = (0, 0)) -> None:
        origin = ff.components.utils.interpret_to_point(origin)
        output._shapely_object = affinity.scale(self._shapely_object, xfact=factor, yfact=factor, origin=origin._shapely_object)
        return output

    @in_place_copy
    def translate(self, output, shift: tuple) -> None:
        shift = ff.components.utils.interpret_to_point(shift)
        output._shapely_object = affinity.translate(self._shapely_object, shift.x, shift.y)
        return output

    @in_place_copy
    def rotate(self, output, angle, origin: tuple = (0, 0)) -> None:
        origin = ff.components.utils.interpret_to_point(origin)
        output._shapely_object = affinity.rotate(self._shapely_object, angle=angle, origin=origin._shapely_object)
        return output


class BaseArea(Alteration):
    @property
    def is_iterable(self) -> bool:
        return isinstance(self._shapely_object, Iterable)

    @property
    def is_multi(self) -> bool:
        return isinstance(self._shapely_object, geo.MultiPolygon)

    @property
    def is_empty(self) -> bool:
        return self._shapely_object.is_empty

    @property
    def is_pure_polygon(self) -> bool:
        if isinstance(self._shapely_object, geo.Polygon):
            return True
        else:
            return False

    @property
    def exterior(self):
        return self._shapely_object.exterior

    def get_rasterized_mesh(self, coordinate_system: CoordinateSystem) -> numpy.ndarray:
        raster = self.rasterize(coordinate_system=coordinate_system)
        raster = raster.reshape(coordinate_system.shape)
        return raster.astype(numpy.float64)

    @property
    def convex_hull(self) -> geo.Polygon:
        return ff.Polygon(instance=self._shapely_object.convex_hull)

    @property
    def area(self) -> float:
        return self._shapely_object.area

    @property
    def bounds(self) -> Tuple[float, float]:
        return self._shapely_object.bounds

    @property
    def center(self) -> geo.Point:
        return ff.Point(position=(self._shapely_object.centroid.x, self._shapely_object.centroid.y))

    def __add__(self, other):
        output = self.copy()
        output._shapely_object = self._shapely_object.__add__(other._shapely_object)
        return output

    def __sub__(self, other):
        output = self.copy()
        output._shapely_object = self._shapely_object.__sub__(other._shapely_object)
        return output

    def __and__(self, other):
        output = self.copy()
        output._shapely_object = self._shapely_object.__and__(other._shapely_object)
        return output

    def scale_position(self, factor: float) -> 'BaseArea':
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

    def shift_position(self, shift: Tuple[float, float]) -> 'BaseArea':
        self.core.translate(shift=shift, in_place=True)
        self.translate(shift=shift, in_place=True)

        return self

    def split_with_line(self, line, return_largest: bool = True) -> 'ff.Polygon':
        assert self.is_pure_polygon, f"Error: non-pure polygone is catch before spliting: {self._shapely_object.__class__}."

        split_geometry = split(self._shapely_object, line.copy().extend(factor=100)._shapely_object).geoms

        areas = [poly.area for poly in split_geometry]

        sorted_area = numpy.argsort(areas)

        if return_largest:
            idx = sorted_area[-1]
            return ff.Polygon(instance=split_geometry[idx])
        else:
            idx = sorted_area[0]
            return ff.Polygon(instance=split_geometry[idx])

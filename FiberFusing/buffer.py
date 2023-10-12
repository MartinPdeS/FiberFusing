#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Built-in imports
import numpy
import copy
from collections.abc import Iterable
from dataclasses import dataclass


# matplotlib imports
from matplotlib.path import Path


# shapely imports
from shapely.ops import split, unary_union
import shapely.geometry as geo
from shapely import affinity

# other imports
from MPSPlots.render2D import SceneList, Axis


def get_polygon_union(*Objects):
    if len(Objects) == 0:
        return Polygon(instance=geo.Polygon())

    Objects = [o._shapely_object if hasattr(o, '_shapely_object') else o for o in Objects]
    output = unary_union(Objects)

    return Polygon(instance=output)


def interpret_to_point(*args):
    args = tuple(arg if isinstance(arg, Point) else Point(position=arg) for arg in args)

    if len(args) == 1:
        return args[0]
    return args


class Alteration():
    def in_place_copy(function, *args, **kwargs):
        def wrapper(self, *args, in_place=False, **kwargs):
            if in_place:
                output = self
            else:
                output = self.copy()
                for attr in self.inherit_attr:
                    setattr(output, attr, getattr(self, attr))
            return function(self, output, *args, **kwargs)

        return wrapper

    def copy(self):
        return copy.deepcopy(self)

    def __repr__(self):
        return self._shapely_object.__repr__()

    @property
    def is_empty(self):
        return self._shapely_object.is_empty

    @in_place_copy
    def union(self, output, *others):
        others = tuple(o._shapely_object for o in others)
        output._shapely_object = self._shapely_object.union(*others)
        return output

    @in_place_copy
    def intersection(self, output, *others):
        others = tuple(o._shapely_object for o in others)
        output._shapely_object = self._shapely_object.intersection(*others)
        return output

    @in_place_copy
    def scale(self, output, factor: float, origin: tuple = (0, 0)) -> None:
        origin = interpret_to_point(origin)
        output._shapely_object = affinity.scale(self._shapely_object, xfact=factor, yfact=factor, origin=origin._shapely_object)
        return output

    @in_place_copy
    def translate(self, output, shift: tuple) -> None:
        shift = interpret_to_point(shift)
        output._shapely_object = affinity.translate(self._shapely_object, shift.x, shift.y)
        return output

    @in_place_copy
    def rotate(self, output, angle, origin: tuple = (0, 0)) -> None:
        origin = interpret_to_point(origin)
        output._shapely_object = affinity.rotate(self._shapely_object, angle=angle, origin=origin._shapely_object)
        return output


class BaseArea(Alteration):
    @property
    def is_iterable(self):
        return isinstance(self._shapely_object, Iterable)

    @property
    def is_multi(self):
        return isinstance(self._shapely_object, geo.MultiPolygon)

    @property
    def is_pure_polygon(self) -> bool:
        if isinstance(self._shapely_object, geo.Polygon):
            return True
        else:
            return False

    @property
    def exterior(self):
        return self._shapely_object.exterior

    def get_rasterized_mesh(self, coordinate_system: Axis) -> numpy.ndarray:
        return self.__raster__(coordinate_system=coordinate_system).reshape(coordinate_system.shape).astype(numpy.float64)

    @property
    def is_empty(self):
        return self._shapely_object.is_empty

    @property
    def convex_hull(self):
        return Polygon(instance=self._shapely_object.convex_hull)

    @property
    def area(self):
        return self._shapely_object.area

    @property
    def bounds(self):
        return self._shapely_object.bounds

    @property
    def center(self):
        return Point(position=(self._shapely_object.centroid.x, self._shapely_object.centroid.y))

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

    def scale_position(self, factor: float):
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

    def shift_position(self, shift: list):
        self.core.translate(shift=shift, in_place=True)
        self.translate(shift=shift, in_place=True)

        return self

    def split_with_line(self, line, return_type: str = 'largest') -> 'Polygon':
        assert self.is_pure_polygon, f"Error: non-pure polygone is catch before spliting: {self._shapely_object.__class__}."

        split_geometry = split(self._shapely_object, line.copy().extend(factor=100)._shapely_object).geoms

        areas = [poly.area for poly in split_geometry]

        sorted_area = numpy.argsort(areas)

        match return_type:
            case 'largest':
                idx = sorted_area[-1]
                return Polygon(instance=split_geometry[idx])
            case 'smallest':
                idx = sorted_area[0]
                return Polygon(instance=split_geometry[idx])


@dataclass
class Point(Alteration):
    position: list = (0, 0)
    index: float = 1.0

    inherit_attr: list = ('index',)

    def __post_init__(self) -> None:
        if isinstance(self.position, Point):
            self._shapely_object = self.position._shapely_object
        elif isinstance(self.position, geo.Point):
            self._shapely_object = self.position
        else:
            self._shapely_object = geo.Point(self.position)

    @property
    def x(self) -> float:
        return self._shapely_object.x

    @property
    def y(self) -> float:
        return self._shapely_object.y

    def shift_position(self, shift: list) -> 'Point':
        point_shift = interpret_to_point(shift)
        return self.__add__(point_shift)

    def __add__(self, other) -> 'Point':
        other = interpret_to_point(other)

        return Point(position=(self.x + other.x, self.y + other.y))

    def __sub__(self, other) -> 'Point':
        other = interpret_to_point(other)
        return Point(position=(self.x - other.x, self.y - other.y))

    def __neg__(self) -> 'Point':
        return Point(position=[-self.x, -self.y])

    def __mul__(self, factor: float) -> 'Point':
        return Point(position=[self.x * factor, self.y * factor])

    def distance(self, other):
        return numpy.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

    def _render_on_ax_(self, ax: Axis, text: str = None, text_shift: tuple = (1.01, 1.01), **kwargs) -> None:
        ax.add_scatter(
            x=self.x,
            y=self.y,
            **kwargs
        )

        if text is not None:
            ax.add_text(
                position=(self.x * text_shift[0], self.y * text_shift[1]),
                text=text
            )

    def plot(self, **kwargs) -> SceneList:
        figure = SceneList(unit_size=(6, 6))

        ax = figure.append_ax(
            x_label='x',
            y_label='y',
            colorbar=False,
            equal=True
        )

        self._render_on_ax_(ax)

        return figure


@dataclass
class LineString(Alteration):
    coordinates: list = ()
    index: float = 1.0

    inherit_attr: list = ('index', )

    def __post_init__(self) -> None:
        assert len(self.coordinates) == 2, 'LineString class is only intended for two coordinates.'
        self.coordinates = interpret_to_point(*self.coordinates)

        shapely_coordinate = [c._shapely_object for c in self.coordinates]

        self._shapely_object = geo.LineString(shapely_coordinate)

        self.coordinates = None

    @property
    def boundary(self):
        return [Point(p) for p in self._shapely_object.boundary.geoms]

    @property
    def center(self):
        return self._shapely_object.centroid

    def intersect(self, other):
        self._shapely_object = self._shapely_object.intersection(other._shapely_object)

    @property
    def mid_point(self):
        P0, P1 = self.boundary
        return Point(position=[(P0.x + P1.x) / 2, (P0.y + P1.y) / 2])

    @property
    def length(self):
        P0, P1 = self.boundary
        return numpy.sqrt((P0.x - P1.x)**2 + (P0.y - P1.y)**2)

    def get_perpendicular(self):
        perpendicular = self.copy()
        perpendicular.rotate(angle=90, origin=perpendicular.mid_point, in_place=True)
        return perpendicular

    def get_position_parametrisation(self, x: float):
        P0, P1 = self.boundary
        return P0 - (P0 - P1) * x

    def _render_on_ax_(self, ax: Axis, **kwargs) -> None:
        ax.add_line(
            x=self._shapely_object.x,
            y=self._shapely_object.y,
            **kwargs
        )

    def make_length(self, length: float):
        return self.extend(factor=length / self.length)

    def centering(self, center: Point):
        P0, P1 = self.boundary

        shift = (center.x - self.mid_point.x, center.y - self.mid_point.y)
        P2 = P0.translate(shift=shift)
        P3 = P1.translate(shift=shift)

        output = LineString(coordinates=[P2._shapely_object, P3._shapely_object])

        self._shapely_object = output._shapely_object

        return self

    def get_vector(self):
        P0, P1 = self.boundary

        dy = P0.y - P1.y
        dx = P0.x - P1.x
        if dx == 0:
            return numpy.asarray([0, 1])
        else:
            norm = numpy.sqrt(1 + (dy / dx)**2)
            return numpy.array([1, dy / dx]) / norm

    def extend(self, factor: float = 1):
        self._shapely_object = affinity.scale(
            self._shapely_object,
            xfact=factor,
            yfact=factor,
            origin=self.mid_point._shapely_object
        )

        return self

    def plot(self, **kwargs) -> SceneList:
        figure = SceneList(unit_size=(6, 6))

        ax = figure.append_ax(
            x_label='x',
            y_label='y',
            colorbar=False,
            equal=True
        )

        self._render_on_ax_(ax, **kwargs)

        return figure


class Polygon(BaseArea):
    inherit_attr: list = ('index',)

    def __init__(self,
            coordinates: list = None,
            instance: geo.Polygon = None,
            index: float = 1.0):

        self.index = index

        if coordinates is not None:
            coordinates = interpret_to_point(*coordinates)
            self._shapely_object = geo.Polygon((c.x, c.y) for c in coordinates)
        elif instance is not None:
            self._shapely_object = instance
        else:
            raise ValueError('Either coordinate or instance has to be given in the constructor')

    def get_hole(self):
        """
        Return the hole in the polygon if there is one. Else it returns and empty polygon

        :returns:   The hole.
        :rtype:     { return_type_description }
        """
        if isinstance(self._shapely_object, geo.MultiPolygon):
            return EmptyPolygon()

        output = self.copy()

        if isinstance(output.interiors, Iterable):
            polygon = [geo.Polygon(c) for c in output.interiors]
            output = get_polygon_union(*polygon)
        else:
            output._shapely_object = geo.Polygon(*output.interiors)

        return output

    @property
    def interiors(self):
        """
        Return interior of the polygon

        :returns:   { description_of_the_return_value }
        :rtype:     { return_type_description }
        """
        return self._shapely_object.interiors

    def remove_non_polygon(self):
        """
        Remove non-polyon element of the (multi) polygon.

        :returns:   { description_of_the_return_value }
        :rtype:     { return_type_description }
        """
        if isinstance(self._shapely_object, geo.GeometryCollection):
            new_polygon_set = [
                p for p in self._shapely_object.geoms if isinstance(p, (geo.Polygon, geo.MultiPolygon))
            ]

            self._shapely_object = geo.MultiPolygon(new_polygon_set)

        return self

    def keep_largest_polygon(self):
        """
        Remove all the smaller polygon only to keep the one with the largest area value.

        :returns:   { description_of_the_return_value }
        :rtype:     { return_type_description }
        """
        if isinstance(self._shapely_object, geo.MultiPolygon):
            area_list = [poly.area for poly in self._shapely_object.geoms]
            largest_area_idx = numpy.argmax(area_list)
            self._shapely_object = self._shapely_object.geoms[largest_area_idx]

        return self

    def _render_on_ax_(self, ax: Axis, **kwargs) -> None:
        """
        Render the Polygon on a specific axis.

        :param      ax:   { parameter_description }
        :type       ax:   Axis

        :returns:   { description_of_the_return_value }
        :rtype:     None
        """
        if isinstance(self._shapely_object, geo.MultiPolygon):
            for polygon in self._shapely_object.geoms:
                self.render_simple_polygon_on_axis(ax=ax, polygon=polygon, **kwargs)

        else:
            self.render_simple_polygon_on_axis(ax=ax, polygon=self._shapely_object, **kwargs)

    def render_simple_polygon_on_axis(self, polygon: geo.Polygon, ax: Axis, **kwargs) -> None:
        """
        Render the a specific polygon on the given axis.

        :param      polygon:        The multi polygon
        :type       polygon:        { type_description }
        :param      ax:             { parameter_description }
        :type       ax:             { type_description }
        """

        # TODO: rings -> https://sgillies.net/2010/04/06/painting-punctured-polygons-with-matplotlib.html
        coordinates = numpy.asarray(polygon.exterior.coords)

        ax.add_polygon(coordinates=coordinates, **kwargs)

    def plot(self) -> SceneList:
        """
        Plot the Polygon structure.

        :param      polygon:        The multi polygon
        :type       polygon:        { type_description }
        :param      ax:             { parameter_description }
        :type       ax:             { type_description }
        """
        figure = SceneList(unit_size=(6, 6))

        ax = figure.append_ax(
            x_label='x',
            y_label='y',
            colorbar=False,
            equal=True
        )

        self._render_on_ax_(ax=ax)

        return figure

    def __raster__(self, coordinate_system: Axis) -> numpy.ndarray:
        """
        Rasterize the polygone using a coordinate set.

        :param      coordinate:  The coordinate
        :type       coordinate:  numpy.ndarray

        :returns:   The rasterize mesh
        :rtype:     numpy.ndarray
        """
        unstructured_coordinate = coordinate_system.to_unstructured_coordinate()

        Exterior = self.contains_points(coordinate=unstructured_coordinate)

        hole = self.get_hole()

        hole_contained = numpy.zeros(Exterior.shape)

        if isinstance(hole, Iterable):
            for sub_hole in hole.geoms():
                hole_contained *= sub_hole.contains_points(unstructured_coordinate)
        else:
            hole_contained = hole.contains_points(unstructured_coordinate)

        return Exterior.astype(int) - hole_contained.astype(int)

    def contains_points(self, coordinate) -> numpy.ndarray:
        """
        Return a rasterized mesh where the value is one if coordinate is in the
        polygone zero either.

        :param      coordinate:  The coordinate
        :type       coordinate:  numpy.ndarray

        :returns:   { description_of_the_return_value }
        :rtype:     numpy.ndarray
        """
        exterior = numpy.zeros(coordinate.shape[0])

        if isinstance(self._shapely_object, geo.MultiPolygon):
            for polygon in self._shapely_object.geoms:
                exterior += self.sub_contain_points(coordinate=coordinate, polygon=polygon)

        else:
            exterior = self.sub_contain_points(coordinate=coordinate, polygon=self._shapely_object)

        return exterior.astype(bool)

    def sub_contain_points(self, coordinate, polygon):
        path_exterior = Path(polygon.exterior.coords)

        return path_exterior.contains_points(coordinate).astype(bool)


class Circle(Polygon):
    def __init__(self,
            position: list,
            radius: float,
            resolution: int = 128,
            *args,
            **kwargs):

        self.radius = radius
        position = interpret_to_point(position)
        instance = position._shapely_object.buffer(radius, resolution=resolution)

        super().__init__(instance=instance, *args, **kwargs)

        self.core = self.center.copy()


class EmptyPolygon(Polygon):
    def __init__(self, *args, **kwargs):
        super().__init__(instance=geo.Polygon(), *args, **kwargs)


# -

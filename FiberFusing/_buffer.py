import numpy

from dataclasses import dataclass
from matplotlib.patches import PathPatch
from matplotlib.collections import PatchCollection
from matplotlib.path import Path
import copy

from shapely.ops import split
import shapely.geometry as geo
from shapely import affinity

from MPSPlots.Render2D import Scene2D, Axis

ORIGIN = geo.Point(0, 0)
RESOLUTION = 128


def interpret_point(*args):
    args = tuple(arg if isinstance(arg, PointComposition) else PointComposition(position=arg) for arg in args)

    if len(args) == 1:
        return args[0]
    return args


@dataclass
class PointComposition():
    position: list = (0, 0)
    name: str = ''
    index: float = 1.0
    color: str = 'black'
    alpha: float = 1.0
    marker: str = "o"
    markersize: int = 60

    inherit_attr: list = ('name', 'color', 'marker', 'alpha', 'markersize', 'index')

    object_description = 'Point'
    is_empty = False

    def __post_init__(self) -> None:
        if isinstance(self.position, PointComposition):
            self._shapely_object = self.position._shapely_object
        else:
            self._shapely_object = geo.Point(self.position)

    def _pass_info_output_(function, *args, **kwargs):
        def wrapper(*args, **kwargs):
            output = function(*args, **kwargs)
            self = args[0]
            for attr in self.inherit_attr:
                setattr(output, attr, getattr(self, attr))
            return output

        return wrapper

    @property
    def x(self):
        return self._shapely_object.x

    @property
    def y(self):
        return self._shapely_object.y

    def __repr__(self):
        return self._shapely_object.__repr__()

    @_pass_info_output_
    def __add__(self, other):
        assert isinstance(other, self.__class__), f"Cannot add to object not of the same class: {other.__class__}-{self.__class__}"

        return PointComposition(position=(self.x + other.x, self.y + other.y))

    @_pass_info_output_
    def __sub__(self, other):
        assert isinstance(other, self.__class__), f"Cannot add to object not of the same class: {other.__class__}-{self.__class__}"

        return PointComposition(position=(self.x - other.x, self.y - other.y))

    @_pass_info_output_
    def __neg__(self):
        return PointComposition(position=[-self.x, -self.y])

    @_pass_info_output_
    def __mul__(self, factor: float):
        return PointComposition(position=[self.x * factor, self.y * factor])

    def translate(self, shift: tuple):
        shift = interpret_point(shift)
        self._shapely_object = affinity.translate(self._shapely_object, shift.x, shift.y)
        return self

    @property
    def center(self):
        return self._shapely_object.x, self._shapely_object.y

    def rotate(self, angle, origin=ORIGIN):
        self._shapely_object = affinity.rotate(self._shapely_object, angle=angle, origin=origin)
        return self

    def _render_(self, Ax):
        if self.is_empty:
            return

        Ax._ax.scatter(self.x, self.y, s=self.markersize, marker=self.marker, color=self.color, alpha=self.alpha)
        Ax._ax.text(self.x * 1.01, self.y * 1.01, self.object_description)

    def plot(self):
        figure = Scene2D(unit_size=(6, 6))
        ax = Axis(row=0, col=0, x_label='x', y_label='y', colorbar=False, equal=True)
        figure.add_axes(ax)
        figure._generate_axis_()

        self._render_(ax)

        return figure

    def copy(self):
        return copy.deepcopy(self)


@dataclass
class LineStringComposition():
    coordinates: list = ()
    name: str = ''
    index: float = 1.0
    color: str = 'black'
    alpha: float = 1.0
    marker: str = "o"
    markersize: int = 60

    inherit_attr: list = ('name', 'color', 'marker', 'alpha', 'markersize', 'index')

    object_description = 'LineString'
    is_empty = False

    def _pass_info_output_(function, *args, **kwargs):
        def wrapper(*args, **kwargs):
            output = function(*args, **kwargs)
            self = args[0]
            for attr in self.inherit_attr:
                setattr(output, attr, getattr(self, attr))
            return output

        return wrapper

    def __post_init__(self) -> None:
        self.coordinates = interpret_point(*self.coordinates)

        shapely_coordinate = [c._shapely_object for c in self.coordinates]

        self._shapely_object = geo.LineString(shapely_coordinate)

    @property
    def center(self):
        return self._shapely_object.centroid

    def intersect(self, other):
        self._shapely_object = self._shapely_object.intersection(other._shapely_object)
        self.update_coordinates()

    @property
    def boundary(self):
        return self.coordinates

    def update_coordinates(self):
        self.coordinates = [PointComposition(position=(p.x, p.y)) for p in self._shapely_object.boundary.geoms]

    def rotate(self, angle, origin=None) -> None:
        if origin is None:
            origin = self.mid_point
        origin = interpret_point(origin)
        self._shapely_object = affinity.rotate(self._shapely_object, angle=angle, origin=origin._shapely_object)
        self.update_coordinates()
        return self

    @property
    def mid_point(self):
        P0, P1 = self.coordinates
        return PointComposition(position=[(P0.x + P1.x) / 2, (P0.y + P1.y) / 2])

    @property
    def length(self):
        P0, P1 = self.coordinates
        return numpy.sqrt((P0.x - P1.x)**2 + (P0.y - P1.y)**2)

    def get_perpendicular(self):
        perpendicular = self.copy()
        perpendicular.rotate(angle=90, origin=perpendicular.mid_point)
        perpendicular.update_coordinates()
        return perpendicular

    def get_position_parametrisation(self, x: float):
        P0, P1 = self.boundary
        return P0 - (P0 - P1) * x

    def translate(self, shift: PointComposition):
        self._shapely_object = affinity.translate(self._shapely_object, shift.x, shift.y)
        self.update_coordinates()
        return self

    def _render_(self, ax: Axis) -> None:
        ax._ax.plot(*self._shapely_object.xy, color=self.color, alpha=self.alpha)

    def make_length(self, length: float):
        P0, P1 = self.boundary
        distance = numpy.sqrt((P0.x - P1.x)**2 + (P0.y - P1.y)**2)
        factor = length / distance
        return self.extend(factor=factor)

    def centering(self, center):
        P0, P1 = self.boundary

        mid_point = self.mid_point
        xShift = center.x - mid_point.x
        yShift = center.y - mid_point.y
        get_vector = [xShift, yShift]

        P2 = P0.translate(shift=get_vector)
        P3 = P1.translate(shift=get_vector)

        output = LineStringComposition(coordinates=[P2._shapely_object, P3._shapely_object])

        self._shapely_object = output._shapely_object
        self.update_coordinates()
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
        self._shapely_object = affinity.scale(self._shapely_object, xfact=factor, yfact=factor, origin=self.mid_point._shapely_object)
        self.update_coordinates()
        return self

    def plot(self) -> Scene2D:
        figure = Scene2D(unit_size=(6, 6))
        ax = Axis(row=0, col=0, x_label='x', y_label='y', colorbar=False, equal=True)
        figure.add_axes(ax)
        figure._generate_axis_()

        self._render_(ax)

        return figure

    def copy(self):
        return copy.deepcopy(self)


@dataclass
class CircleComposition():
    position: list = PointComposition
    radius: float = 1
    name: str = ''
    index: float = 1.0
    facecolor: str = 'lightblue'
    edgecolor: str = 'black'
    alpha: float = 0.4
    resolution: int = 128 * 2

    inherit_attr: list = ('name', 'facecolor', 'alpha', 'edgecolor', 'index')
    is_empty = False
    has_z = False

    def _pass_info_output_(function, *args, **kwargs):
        def wrapper(*args, **kwargs):
            output = function(*args, **kwargs)
            self = args[0]
            for attr in self.inherit_attr:
                setattr(output, attr, getattr(self, attr))
            return output

        return wrapper

    def __post_init__(self) -> None:
        self._shapely_object = self.position._shapely_object.buffer(self.radius, resolution=self.resolution)

    @property
    def exterior(self):
        return self._shapely_object.exterior

    @property
    def center(self):
        return PointComposition(position=(self._shapely_object.centroid.x, self._shapely_object.centroid.y))

    @property
    def area(self):
        return self._shapely_object.area

    @property
    def convex_hull(self):
        output = self.copy()
        output._shapely_object = self._shapely_object.convex_hull
        return output

    def intersection(self, *others):
        output = self.copy()
        others = tuple(o._shapely_object for o in others)
        output._shapely_object = self._shapely_object.intersection(*others)
        return output

    def union(self, *others):
        output = self.copy()
        others = tuple(o._shapely_object for o in others)
        output._shapely_object = self._shapely_object.union(*others)
        return output

    def _render_(self, ax):
        path = Path.make_compound_path(
            Path(numpy.asarray(self.exterior.coords)[:, :2]),
            *[Path(numpy.asarray(ring.coords)[:, :2]) for ring in self._shapely_object.interiors])

        patch = PathPatch(path)
        collection = PatchCollection([patch], alpha=self.alpha, facecolor=self.facecolor, edgecolor=self.edgecolor)

        ax._ax.add_collection(collection, autolim=True)
        ax._ax.autoscale_view()
        if self.name:
            ax._ax.scatter(self.position.x, self.position.y, color='k', zorder=10)
            ax._ax.text(self.position.x, self.position.y, self.name)

    def plot(self) -> Scene2D:
        figure = Scene2D(unit_size=(6, 6))
        ax = Axis(row=0, col=0, x_label='x', y_label='y', colorbar=False, equal=True)
        figure.add_axes(ax)
        figure._generate_axis_()
        self._render_(ax)

        return figure

    def update_coordinates(self) -> None:
        self.position = PointComposition(position=self.center)

    @_pass_info_output_
    def scale(self, factor: float, origin: PointComposition = (0, 0)) -> None:
        origin = interpret_point(origin)
        self._shapely_object = affinity.scale(self._shapely_object, xfact=factor, yfact=factor, origin=origin)
        self.update_coordinates()
        return self

    def translate(self, shift: tuple) -> None:
        self._shapely_object = affinity.translate(self._shapely_object, *shift)
        self.update_coordinates()
        return self

    def rotate(self, angle, origin: tuple = (0, 0)) -> None:
        origin = interpret_point(origin)
        if isinstance(origin, PointComposition):
            origin = origin._shapely_object

        self._shapely_object = affinity.rotate(self._shapely_object, angle=angle, origin=origin)
        self.update_coordinates()
        return self

    def copy(self):
        return copy.deepcopy(self)

    def __raster__(self, coordinate: numpy.ndarray):
        Exterior = Path(self.exterior.coords)

        Exterior = Exterior.contains_points(coordinate)

        return Exterior.astype(int)

    def get_rasterized_mesh(self, coordinate: numpy.ndarray, n_x: int, n_y: int) -> numpy.ndarray:
        return self.__raster__(coordinate).reshape([n_y, n_x])

    def contains_points(self, coordinate: numpy.ndarray) -> numpy.ndarray:
        exterior = Path(self.exterior.coords)
        return exterior.contains_points(coordinate).astype(bool)

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


@dataclass
class PolygonComposition():
    coordinates: list = None
    instance: geo.Polygon = None
    name: str = ''
    index: float = 1.0
    facecolor: str = 'lightblue'
    edgecolor: str = 'black'
    alpha: float = 0.4

    inherit_attr: list = ('name', 'facecolor', 'alpha', 'edgecolor', 'index')
    is_empty = False
    has_z = False

    def __post_init__(self) -> None:
        if self.instance is not None:
            self._shapely_object = self.instance
        else:
            self.coordinates = interpret_point(*self.coordinates)
            self._shapely_object = geo.Polygon((c.x, c.y) for c in self.coordinates)

    def copy(self):
        return copy.deepcopy(self)

    @property
    def exterior(self):
        return self._shapely_object.exterior

    @property
    def area(self):
        return self._shapely_object.area

    def update_coordinates(self):
        self.coordinates = [PointComposition(position=(p.x, p.y)) for p in self.coordinates]

    def remove_non_polygon(self):
        if isinstance(self._shapely_object, geo.GeometryCollection):
            new_polygon_set = [p for p in self._shapely_object.geoms if isinstance(p, (geo.Polygon, geo.MultiPolygon))]
            self._shapely_object = geo.Polygon(*new_polygon_set)

        return self

    def scale(self, factor: float, origin: PointComposition = (0, 0)) -> None:
        origin = interpret_point(origin)
        self._shapely_object = affinity.scale(self._shapely_object, xfact=factor, yfact=factor, origin=origin._shapely_object)
        self.update_coordinates()
        return self

    def translate(self, shift: tuple) -> None:
        self._shapely_object = affinity.translate(self._shapely_object, *shift)
        self.update_coordinates()
        return self

    def rotate(self, angle, origin: tuple = (0, 0)) -> None:
        origin = interpret_point(origin)
        if isinstance(origin, PointComposition):
            origin = origin._shapely_object

        self._shapely_object = affinity.rotate(self._shapely_object, angle=angle, origin=origin)
        self.update_coordinates()
        return self

    @property
    def center(self):
        return self._shapely_object.centroid.x, self._shapely_object.centroid.y

    @property
    def convex_hull(self):
        output = self.copy()
        output._shapely_object = self._shapely_object.convex_hull
        return output

    def _render_(self, ax, instance=None):
        if instance is None:
            instance = self._shapely_object

        path = Path.make_compound_path(
            Path(numpy.asarray(instance.exterior.coords)[:, :]),
            *[Path(numpy.asarray(ring.coords)[:, :]) for ring in instance.interiors])

        patch = PathPatch(path)
        collection = PatchCollection([patch], alpha=self.alpha, facecolor=self.facecolor, edgecolor=self.edgecolor)

        ax._ax.add_collection(collection, autolim=True)
        ax._ax.autoscale_view()
        if self.name:
            ax._ax.scatter(*self.center)
            ax._ax.text(*self.center, self.name)

    def plot(self) -> Scene2D:
        figure = Scene2D(unit_size=(6, 6))
        ax = Axis(row=0, col=0, x_label='x', y_label='y', colorbar=False, equal=True)
        figure.add_axes(ax)
        figure._generate_axis_()

        if isinstance(self._shapely_object, geo.MultiPolygon):
            for poly in self._shapely_object.geoms:
                self._render_(instance=poly, ax=ax)

        else:
            self._render_(instance=self._shapely_object, ax=ax)

        return figure

    def __raster__(self, coordinate: numpy.ndarray):
        Exterior = Path(self.exterior.coords)

        Exterior = Exterior.contains_points(coordinate)

        hole = self.hole.contains_points(coordinate)

        return Exterior.astype(int) - hole.astype(int)

    def get_rasterized_mesh(self, coordinate: numpy.ndarray, n_x: int, n_y: int) -> numpy.ndarray:
        return self.__raster__(coordinate).reshape([n_y, n_x])

    def contains_points(self, Coordinate):
        Exterior = Path(self.exterior.coords)
        return Exterior.contains_points(Coordinate).astype(bool)

    def simplify(self, *args, **kwargs):
        return self

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

    def split_with_line(self, line, return_type: str = 'largest'):
        assert isinstance(self._shapely_object, geo.Polygon)

        split_geometry = split(self._shapely_object, line.copy().extend(factor=100)._shapely_object).geoms

        if split_geometry[0].area < split_geometry[1].area:
            largest_section = PolygonComposition(instance=split_geometry[1])
            smallest_section = PolygonComposition(instance=split_geometry[0])
        else:
            largest_section = PolygonComposition(instance=split_geometry[0])
            smallest_section = PolygonComposition(instance=split_geometry[1])

        match return_type:
            case 'largest':
                return largest_section
            case 'smallest':
                return smallest_section
            case 'both':
                return largest_section, smallest_section



























class Polygon(geo.Polygon):  # https://github.com/shapely/shapely/issues/1233#issuecomment-977837620
    _id_to_attrs: dict = {}
    __slots__: tuple = geo.Polygon.__slots__
    inherit_attr: list = ('name', 'facecolor', 'edgecolor', 'alpha', 'index')

    def __init__(self,
                 instance: geo.Polygon = None,
                 coordinate: list = None,
                 name: str = None,
                 index: float = 1,
                 facecolor: str = 'lightblue',
                 alpha: float = 0.9,
                 edgecolor: str = "black") -> None:

        self._id_to_attrs[id(self)] = dict(name=name,
                                           index=index,
                                           facecolor=facecolor,
                                           edgecolor=edgecolor,
                                           alpha=alpha)

    def __new__(cls,
                instance: geo.Polygon = None,
                coordinate: list = None,
                name: str = None,
                index: float = 1,
                facecolor: str = 'black',
                alpha: float = 0.9,
                edgecolor: str = "black") -> None:

        if instance is not None:
            instance.__class__ = cls
            return instance

        elif coordinate is not None:
            if isinstance(coordinate[0], geo.Point):
                coordinate = [[p.x, p.y] for p in coordinate]
            instance = geo.Polygon(coordinate)
            instance.__class__ = cls
            return instance

        else:
            raise Exception(f"argument type not valid {coordinate=}, {instance=}")

    def _pass_info_output_(function, *args, **kwargs):
        def wrapper(*args, **kwargs):
            output = function(*args, **kwargs)
            self = args[0]
            output = self.__class__(output)
            for attr in self.inherit_attr:
                setattr(output, attr, getattr(self, attr))
            return output

        return wrapper

    def __getattr__(self, attribute: str):
        try:
            return self.__class__._id_to_attrs[id(self)][attribute]
        except KeyError as e:
            raise AttributeError(str(e)) from None

    def __setattr__(self, attribute: str, value):
        try:
            self.__class__._id_to_attrs[id(self)][attribute] = value
        except KeyError as e:
            raise AttributeError(str(e)) from None

    def __del__(self):
        del self._id_to_attrs[id(self)]

    @_pass_info_output_
    def scale(self, factor: float, origin: geo.Point = ORIGIN):
        o = affinity.scale(self, xfact=factor, yfact=factor, origin=origin)
        return o

    @_pass_info_output_
    def translate(self, shift: tuple):
        o = affinity.translate(self, *shift)
        return o

    @_pass_info_output_
    def rotate(self, angle, origin=ORIGIN):
        o = affinity.rotate(self, angle=angle, origin=origin)
        return o

    @property
    def center(self):
        return self.centroid.x, self.centroid.y

    def _render_(self, ax):
        if self.is_empty:
            return

        path = Path.make_compound_path(
            Path(numpy.asarray(self.exterior.coords)[:, :]),
            *[Path(numpy.asarray(ring.coords)[:, :]) for ring in self.interiors])

        patch = PathPatch(path)
        collection = PatchCollection([patch], alpha=self.alpha, facecolor=self.facecolor, edgecolor=self.edgecolor)

        ax._ax.add_collection(collection, autolim=True)
        ax._ax.autoscale_view()
        if self.name:
            ax._ax.scatter(*self.center)
            ax._ax.text(*self.center, self.name)

    def plot(self, Figure=None, Ax=None, Return=False, Show=True):
        Figure = Scene2D(unit_size=(6, 6))
        ax = Axis(row=0, col=0, x_label='x', y_label='y', colorbar=False, equal=True)
        Figure.add_axes(ax)
        Figure._generate_axis_()
        self._render_(ax)

        return Figure

    @property
    def hole(self):
        return Polygon(Polygon(self.exterior) - self)

    def __raster__(self, coordinate: numpy.ndarray):
        Exterior = Path(self.exterior.coords)

        Exterior = Exterior.contains_points(coordinate)

        hole = self.hole.contains_points(coordinate)

        return Exterior.astype(int) - hole.astype(int)

    def get_rasterized_mesh(self, coordinate: numpy.ndarray, n_x: int, n_y: int) -> numpy.ndarray:
        return self.__raster__(coordinate).reshape([n_y, n_x])

    def contains_points(self, Coordinate):
        if self.is_empty:
            return numpy.zeros(Coordinate.shape[0])
        else:
            Exterior = Path(self.exterior.coords)
            return Exterior.contains_points(Coordinate).astype(bool)

    @_pass_info_output_
    def remove_non_polygon(self):
        return self

    @_pass_info_output_
    def simplify(self, *args, **kwargs):
        return super().simplify(*args, **kwargs)

    @_pass_info_output_
    def simplify(self, *args, **kwargs):
        return super().simplify(*args, **kwargs)


class GeometryCollection(geo.GeometryCollection):
    _id_to_attrs: dict = {}
    __slots__: tuple = geo.Polygon.__slots__
    inherit_attr: list = ('name', 'facecolor', 'edgecolor', 'alpha', 'index')

    def __init__(self,
                 *args,
                 name: str = None,
                 index: float = 1,
                 facecolor: str = 'lightblue',
                 alpha: float = 0.9,
                 edgecolor: str = "black",
                 **kwargs) -> None:

        self._id_to_attrs[id(self)] = dict(name=name,
                                           index=index,
                                           facecolor=facecolor,
                                           edgecolor=edgecolor,
                                           alpha=alpha)

    def __new__(cls,
                 *args,
                 name: str = None,
                 index: float = 1,
                 facecolor: str = 'black',
                 alpha: float = 0.9,
                 edgecolor: str = "black",
                 **kwargs) -> None:

        instance = super().__new__(cls, *args, **kwargs)
        instance.__class__ = cls
        return instance

    def _pass_info_output_(function, *args, **kwargs):
        def wrapper(*args, **kwargs):
            output = function(*args, **kwargs)
            self = args[0]
            output = self.__class__(output)
            for attr in self.inherit_attr:
                setattr(output, attr, getattr(self, attr))
            return output

        return wrapper

    def __getattr__(self, attribute: str):
        try:
            return self.__class__._id_to_attrs[id(self)][attribute]
        except KeyError as e:
            raise AttributeError(str(e)) from None

    def __setattr__(self, attribute: str, value):
        try:
            self.__class__._id_to_attrs[id(self)][attribute] = value
        except KeyError as e:
            raise AttributeError(str(e)) from None

    def __del__(self):
        del self._id_to_attrs[id(self)]

    @_pass_info_output_
    def scale(self, factor: float, origin: geo.Point = ORIGIN):
        o = affinity.scale(self, xfact=factor, yfact=factor, origin=origin)
        return o

    @_pass_info_output_
    def translate(self, shift: tuple):
        if isinstance(shift, geo.Point):
            shift = (shift.x, shift.y)

        o = affinity.translate(self, *shift)
        return o

    @_pass_info_output_
    def rotate(self, angle, origin=ORIGIN):
        o = affinity.rotate(self, angle=angle, origin=origin)
        return o

    def keep_only_largest_polygon(self, *args, **kwargs):
        max_area = 0
        for poly in self.geoms:
            if poly.area > max_area:
                max_area = poly.area

        for poly in self.geoms:
            if poly.area == max_area:
                output = Polygon(poly)
                return output

    def center(self):
        return self.centroid.x, self.centroid.y

    def _render_(self, ax):
        if self.is_empty:
            return

        for geometry in self.geoms:
            path = Path.make_compound_path(
                Path(numpy.asarray(geometry.exterior.coords)[:, :2]),
                *[Path(numpy.asarray(ring.coords)[:, :2]) for ring in geometry.interiors])

            patch = PathPatch(path)
            collection = PatchCollection([patch], alpha=self.alpha, facecolor=self.facecolor, edgecolor=self.edgecolor)

            ax._ax.add_collection(collection, autolim=True)
            ax._ax.autoscale_view()
            if self.name:
                ax._ax.scatter(*self.center)
                ax._ax.text(*self.center, self.name)

    def plot(self, Figure=None, Ax=None, Return=False, Show=True):
        Figure = Scene2D(unit_size=(6, 6))
        ax = Axis(row=0, col=0, x_label='x', y_label='y', colorbar=False, equal=True)
        Figure.add_axes(ax)
        Figure._generate_axis_()
        self._render_(ax)

        return Figure

    @property
    def hole(self):
        return Polygon(Polygon(self.exterior) - self)

    def __raster__(self, coordinate):
        Exterior = Path(self.exterior.coords)

        Exterior = Exterior.contains_points(coordinate)

        hole = self.hole.contains_points(coordinate)

        return Exterior.astype(int) - hole.astype(int)

    def get_rasterized_mesh(self, coordinate: numpy.ndarray, n_x: int, n_y: int) -> numpy.ndarray:
        return self.__raster__(coordinate).reshape([n_y, n_x])

    def contains_points(self, Coordinate):
        if self.is_empty:
            return numpy.zeros(Coordinate.shape[0])
        else:
            Exterior = Path(self.exterior.coords)
            return Exterior.contains_points(Coordinate).astype(bool)

    @_pass_info_output_
    def remove_non_polygon(self):
        cleaned = [e for e in self.geoms if not isinstance(e, (geo.LineString, geo.Point))]
        return cleaned


class BackGround(geo.Polygon):  # https://github.com/shapely/shapely/issues/1233#issuecomment-977837620
    _id_to_attrs: dict = {}
    __slots__: tuple = geo.Polygon.__slots__
    inherit_attr: list = ('name', 'facecolor', 'edgecolor', 'alpha', 'index')

    def __init__(self,
                 *args,
                 name: str = None,
                 index: float = 1,
                 facecolor: str = 'lightblue',
                 alpha: float = 0.9,
                 edgecolor: str = "black",
                 **kwargs) -> None:

        self._id_to_attrs[id(self)] = dict(name='background',
                                           index=index,
                                           facecolor=facecolor,
                                           edgecolor=edgecolor,
                                           alpha=alpha)

    def __new__(cls,
                 *args,
                 name: str = None,
                 index: float = 1,
                 facecolor: str = 'black',
                 alpha: float = 0.9,
                 edgecolor: str = "black",
                 **kwargs) -> None:

        instance = geo.Point(ORIGIN).buffer(1000)
        instance.__class__ = cls
        return instance

    def _pass_info_output_(function, *args, **kwargs):
        def wrapper(*args, **kwargs):
            output = function(*args, **kwargs)
            self = args[0]
            output = self.__class__(output)
            for attr in self.inherit_attr:
                setattr(output, attr, getattr(self, attr))
            return output

        return wrapper

    def __getattr__(self, attribute: str):
        try:
            return self.__class__._id_to_attrs[id(self)][attribute]
        except KeyError as e:
            raise AttributeError(str(e)) from None

    def __setattr__(self, attribute: str, value):
        try:
            self.__class__._id_to_attrs[id(self)][attribute] = value
        except KeyError as e:
            raise AttributeError(str(e)) from None

    def __del__(self):
        del self._id_to_attrs[id(self)]

    @_pass_info_output_
    def scale(self, factor: float, origin: geo.Point = ORIGIN):
        o = affinity.scale(self, xfact=factor, yfact=factor, origin=origin)
        return o

    @_pass_info_output_
    def translate(self, shift: tuple):
        if isinstance(shift, geo.Point):
            shift = (shift.x, shift.y)

        o = affinity.translate(self, *shift)
        return o

    @_pass_info_output_
    def rotate(self, angle, origin=ORIGIN):
        o = affinity.rotate(self, angle=angle, origin=origin)
        return o

    @property
    def center(self):
        return self.centroid.x, self.centroid.y

    def _render_(self, ax):
        if self.is_empty:
            return

        path = Path.make_compound_path(
            Path(numpy.asarray(self.exterior.coords)[:, :2]),
            *[Path(numpy.asarray(ring.coords)[:, :2]) for ring in self.interiors])

        patch = PathPatch(path)
        collection = PatchCollection([patch], alpha=self.alpha, facecolor=self.facecolor, edgecolor=self.edgecolor)

        ax._ax.add_collection(collection, autolim=True)
        ax._ax.autoscale_view()
        if self.name:
            ax._ax.scatter(*self.center)
            ax._ax.text(*self.center, self.name)

    def plot(self, Figure=None, Ax=None, Return=False, Show=True):
        Figure = Scene2D(unit_size=(6, 6))
        ax = Axis(row=0, col=0, x_label='x', y_label='y', colorbar=False, equal=True)
        Figure.add_axes(ax)
        Figure._generate_axis_()
        self._render_(ax)

        return Figure

    def get_rasterized_mesh(self, coordinate: numpy.ndarray, n_x: int, n_y: int) -> numpy.ndarray:
        return self.__raster__(coordinate).reshape([n_y, n_x])

    def __raster__(self, coordinate) -> numpy.ndarray:
        Exterior = Path(self.exterior.coords)

        Exterior = Exterior.contains_points(coordinate)

        return Exterior.astype(int)

    def contains_points(self, Coordinate):
        if self.is_empty:
            return numpy.zeros(Coordinate.shape[0])
        else:
            Exterior = Path(self.exterior.coords)
            return Exterior.contains_points(Coordinate).astype(bool)

    @_pass_info_output_
    def remove_non_polygon(self):
        return self

    @_pass_info_output_
    def simplify(self, *args, **kwargs):
        return super().simplify(*args, **kwargs)
# -

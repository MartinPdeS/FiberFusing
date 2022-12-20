import numpy

from matplotlib.patches import PathPatch
from matplotlib.collections import PatchCollection
from matplotlib.path import Path

import shapely.geometry as geo
from shapely import affinity

from MPSPlots.Render2D import Scene2D, Axis

ORIGIN = geo.Point(0, 0)
RESOLUTION = 128


class Point(geo.Point):  # https://github.com/shapely/shapely/issues/1233#issuecomment-977837620
    _id_to_attrs: dict = {}
    __slots__: tuple = geo.Point.__slots__
    inherit_attr: list = ('name', 'color', 'marker', 'alpha', 'markersize', 'index')

    def __init__(self,
                 *args,
                 name: str = None,
                 index: float = 1,
                 color: str = 'black',
                 alpha: float = 0.9,
                 marker: str = "o",
                 markersize: int = 60,
                 **kwargs) -> None:

        self._id_to_attrs[id(self)] = dict(name=name,
                                           index=index,
                                           color=color,
                                           marker=marker,
                                           alpha=alpha,
                                           markersize=markersize)

    def __new__(cls,
                 *args,
                 name: str = None,
                 index: float = 1,
                 color: str = 'black',
                 alpha: float = 0.9,
                 marker: str = "o",
                 markersize: int = 60,
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
            Point._id_to_attrs[id(self)][attribute] = value
        except KeyError as e:
            raise AttributeError(str(e)) from None

    def __del__(self):
        del self._id_to_attrs[id(self)]

    @_pass_info_output_
    def __add__(self, other):
        if not isinstance(other, geo.Point):
            other = geo.Point(other)
        return Point([self.x + other.x, self.y + other.y])

    @_pass_info_output_
    def __sub__(self, other):
        if not isinstance(other, geo.Point):
            other = geo.Point(other)
        return Point([self.x - other.x, self.y - other.y])

    @_pass_info_output_
    def __neg__(self):
        return Point([-self.x, -self.y])

    @_pass_info_output_
    def __mul__(self, factor: float):
        return Point([self.x * factor, self.y * factor])

    @_pass_info_output_
    def __rmul__(self, factor: float):
        return Point([self.x * factor, self.y * factor])

    @_pass_info_output_
    def __truediv__(self, factor: float):
        return Point([self.x / factor, self.y / factor])

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

    def _render_(self, Ax):
        if self.is_empty:
            return

        Ax._ax.scatter(self.x, self.y, s=self.markersize, marker=self.marker, color=self.color, alpha=self.alpha)
        Ax._ax.text(self.x * 1.01, self.y * 1.01, self.name)

    def Plot(self, Figure=None, Ax=None, Return=False, Show=True):
        Figure = Scene2D(unit_size=(6, 6))
        Ax = Axis(row=0, col=0, x_label='x', y_label='y', colorbar=False, equal=True)
        Figure.AddAxes(Ax)
        Figure._generate_axis_()

        self._render_(Ax)

        return Figure

    def __raster__(self):
        raise Exception("Rastering not available for points.")

    @_pass_info_output_
    def remove_non_polygon(self):
        return self


class LineString(geo.LineString):
    _id_to_attrs: dict = {}
    __slots__: tuple = geo.LineString.__slots__
    inherit_attr: list = ('name', 'color', 'alpha', 'linewidth', 'index')

    def __init__(self,
                 instance: geo.LineString = None,
                 coordinate: list = None,
                 name: str = None,
                 index: float = 1,
                 color: str = 'black',
                 alpha: float = 0.9,
                 linewidth: str = 2) -> None:

        self._id_to_attrs[id(self)] = dict(name=name,
                                           index=index,
                                           color=color,
                                           linewidth=linewidth,
                                           alpha=alpha)

    def __new__(cls,
                instance: geo.LineString = None,
                coordinate: list = None,
                name: str = None,
                index: float = 1,
                color: str = 'black',
                alpha: float = 0.9,
                linewidth: str = 2) -> None:

        if instance is not None:
            instance = super().__new__(cls, instance)
            instance.__class__ = cls
            return instance

        elif coordinate:
            instance = super().__new__(cls, coordinate)
            instance.__class__ = cls
            return instance

        else:
            raise Exception(f"argument type not valid {coordinate=}, {linestring=}")

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

    @_pass_info_output_
    def centering(self, center):
        P0, P1 = self.boundary

        mid_point = self.mid_point
        xShift = center.x - mid_point.x
        yShift = center.y - mid_point.y
        get_vector = [xShift, yShift]

        P2 = Point(P0).translate(shift=get_vector)
        P3 = Point(P1).translate(shift=get_vector)

        return LineString(coordinate=[P2, P3])

    def MakeLength(self, length: float):
        P0, P1 = self.boundary
        distance = numpy.sqrt((P0.x - P1.x)**2 + (P0.y - P1.y)**2)
        factor = length / distance
        return self.extend(factor=factor)

    @_pass_info_output_
    def extend(self, factor: float = 1):
        return LineString(instance=affinity.scale(self,
                                                    xfact=factor,
                                                    yfact=factor,
                                                    origin=self.mid_point))

    @property
    def mid_point(self):
        P0, P1 = self.boundary
        return Point([(P0.x + P1.x) / 2, (P0.y + P1.y) / 2])

    def get_perpendicular(self):
        return self.rotate(angle=90, origin=self.mid_point)

    def get_vector(self):
        P0, P1 = self.boundary

        dy = P0.y - P1.y
        dx = P0.x - P1.x
        if dx == 0:
            return numpy.asarray([0, 1])
        else:
            norm = numpy.sqrt(1 + (dy / dx)**2)
            return numpy.array([1, dy / dx]) / norm

    @property
    def boundary(self):
        return [Point(bound) for bound in super().boundary.geoms]

    def get_position_parametrisation(self, x):
        P0, P1 = self.boundary
        return P0 - (P0 - P1) * x

    def _render_(self, Ax):
        if self.is_empty:
            return

        Ax._ax.plot(*self.xy, color=self.color, alpha=self.alpha)

    def Plot(self, Figure=None, Ax=None, Return=False, Show=True):
        Figure = Scene2D(unit_size=(6, 6))
        Ax = Axis(row=0, col=0, x_label='x', y_label='y', colorbar=False, equal=True, equal_limits=True)
        Figure.AddAxes(Ax)
        Figure._generate_axis_()

        self._render_(Ax)

        return Figure

    def __raster__(self):
        raise Exception("Rastering not available for points.")

    @_pass_info_output_
    def remove_non_polygon(self):
        return self


class Circle(geo.Polygon):
    _id_to_attrs: dict = {}
    __slots__: tuple = geo.Polygon.__slots__
    inherit_attr: list = ('name', 'facecolor', 'alpha', 'edgecolor', 'index')

    def __init__(self,
                 instance: geo.Polygon = None,
                 radius: float = 1,
                 center: Point = ORIGIN,
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
                 radius: float = 1.,
                 center: Point = ORIGIN,
                 name: str = None,
                 index: float = 1,
                 facecolor: str = 'black',
                 alpha: float = 0.9,
                 edgecolor: str = "black") -> None:

        if instance is not None:
            instance.__class__ = cls
            return instance

        else:
            instance = geo.Point(center).buffer(radius, resolution=RESOLUTION)
            instance.__class__ = cls
            return instance

    def _pass_info_output_(function, *args, **kwargs):
        def wrapper(*args, **kwargs):
            output = function(*args, **kwargs)
            self = args[0]
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

    @property
    def hole(self):
        return Polygon(Polygon(self.exterior) - self)

    @property
    def Object(self):
        return self

    @_pass_info_output_
    def scale(self, factor: float, origin: geo.Point = ORIGIN):
        o = affinity.scale(self, xfact=factor, yfact=factor, origin=origin)
        return Circle(o)

    @_pass_info_output_
    def translate(self, shift: tuple):
        o = affinity.translate(self, *shift)
        return Circle(o)

    @_pass_info_output_
    def rotate(self, angle, origin=ORIGIN):
        o = affinity.rotate(self, angle=angle, origin=origin)
        return Circle(o)

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

    def Plot(self, Figure=None, Ax=None, Return=False, Show=True):
        Figure = Scene2D(unit_size=(6, 6))
        ax = Axis(row=0, col=0, x_label='x', y_label='y', colorbar=False, equal=True)
        Figure.AddAxes(ax)
        Figure._generate_axis_()
        self._render_(ax)

        return Figure

    def __raster__(self, coordinate):
        Exterior = Path(self.exterior.coords)

        Exterior = Exterior.contains_points(coordinate)

        return Exterior.astype(int)

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

    def Plot(self, Figure=None, Ax=None, Return=False, Show=True):
        Figure = Scene2D(unit_size=(6, 6))
        ax = Axis(row=0, col=0, x_label='x', y_label='y', colorbar=False, equal=True)
        Figure.AddAxes(ax)
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

    def Plot(self, Figure=None, Ax=None, Return=False, Show=True):
        Figure = Scene2D(unit_size=(6, 6))
        ax = Axis(row=0, col=0, x_label='x', y_label='y', colorbar=False, equal=True)
        Figure.AddAxes(ax)
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

    def Plot(self, Figure=None, Ax=None, Return=False, Show=True):
        Figure = Scene2D(unit_size=(6, 6))
        ax = Axis(row=0, col=0, x_label='x', y_label='y', colorbar=False, equal=True)
        Figure.AddAxes(ax)
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

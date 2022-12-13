import numpy

from matplotlib.patches import PathPatch
from matplotlib.collections import PatchCollection
from matplotlib.path import Path

import shapely.geometry as geo
from shapely import affinity

from MPSPlots.Render2D import Scene2D, Axis

ORIGIN = geo.Point(0, 0)


class Point(geo.Point):
    name: str = None
    color: str = 'black'
    alpha: float = 0.9
    marker: str = "o"
    markersize: int = 60
    index: float = 1
    attributes: list = ('name', 'color', 'marker', 'alpha', 'markersize', 'index')

    def _pass_info_output_(function, *args, **kwargs):
        def wrapper(*args, **kwargs):
            output = function(*args, **kwargs)
            self = args[0]
            output.__class__ = self.__class__
            for attr in self.attributes:
                setattr(output, attr, getattr(self, attr))
            return output

        return wrapper

    @_pass_info_output_
    def __add__(self, other):
        return Point([self.x + other.x, self.y + other.y])

    @_pass_info_output_
    def __sub__(self, other):
        return Point([self.x - other.x, self.y - other.y])

    @_pass_info_output_
    def __neg__(self):
        return Point([-self.x, -self.y])

    def __init__(self, *args, name: str = 'none', index: float = 1, **kwargs) -> None:
        self.name = name

    def __new__(cls, *args, name: str = 'none', index: float = 1, **kwargs):
        instance = geo.Point(*args, **kwargs)
        instance.__class__ = cls
        return instance

    @_pass_info_output_
    def scale(self, factor: float, origin: geo.Point = ORIGIN):
        o = affinity.scale(self, xfact=factor, yfact=factor, origin=origin)
        o.__class__ = self.__class__
        return o

    @_pass_info_output_
    def translate(self, shift: tuple):
        if isinstance(shift, geo.Point):
            shift = (shift.x, shift.y)

        o = affinity.translate(self, *shift)
        o.__class__ = self.__class__
        return o

    @_pass_info_output_
    def rotate(self, angle, origin=ORIGIN):
        o = affinity.rotate(self, angle=angle, origin=origin)
        o.__class__ = self.__class__
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


class Circle(geo.Polygon):
    name: str = None
    facecolor: str = 'lightblue'
    edgecolor: str = 'black'
    alpha: float = 0.4
    resolution: int = 128
    index: float = 1.
    attributes: list = ('name', 'facecolor', 'edgecolor', 'alpha', 'resolution', 'index')

    def _pass_info_output_(function, *args, **kwargs):
        def wrapper(*args, **kwargs):
            output = function(*args, **kwargs)
            self = args[0]
            output.__class__ = self.__class__
            for attr in self.attributes:
                setattr(output, attr, getattr(self, attr))
            return output

        return wrapper

    def __init__(self, *args, center: tuple = (0, 0), name: str = None, radius: float = 1, resolution: int = 128, index: float = 1., **kwargs) -> None:
        self.name = name
        self.resolution = 128
        super().__init__(*args, **kwargs)

    def __new__(cls, *args, center: tuple = (0, 0), name: str = None, radius: float = 1, resolution: int = 128, index: float = 1., **kwargs):
        instance = geo.Point(center).buffer(radius)
        instance.__class__ = cls
        return instance

    @property
    def hole(self):
        return Polygon(Polygon(self.exterior) - self)

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
        Exterior = Path(list(self.exterior.coords))

        Exterior = Exterior.contains_points(coordinate)

        return Exterior.astype(int)

    def get_rasterized_mesh(self, coordinate: numpy.ndarray, shape: list) -> numpy.ndarray:
        return self.__raster__(coordinate).reshape(shape)

    def contains_points(self, Coordinate):
        if self.is_empty:
            return numpy.zeros(Coordinate.shape[0])
        else:
            Exterior = Path(list(self.exterior.coords))
            return Exterior.contains_points(Coordinate).astype(bool)


class Polygon(geo.Polygon):
    name: str = None
    facecolor: str = 'lightblue'
    edgecolor: str = 'black'
    alpha: float = 0.4
    index: float = 1.
    attributes: list = ('name', 'facecolor', 'edgecolor', 'alpha', 'index')

    def _pass_info_output_(function, *args, **kwargs):
        def wrapper(*args, **kwargs):
            output = function(*args, **kwargs)
            self = args[0]
            output.__class__ = self.__class__
            for attr in self.attributes:
                setattr(output, attr, getattr(self, attr))
            return output

        return wrapper

    def __init__(self, *args, name: str = None, index: float = 1, **kwargs) -> None:
        self.name = name
        super().__init__(*args, **kwargs)

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

    @property
    def hole(self):
        return Polygon(Polygon(self.exterior) - self)

    def __raster__(self, coordinate):
        Exterior = Path(list(self.exterior.coords))

        Exterior = Exterior.contains_points(coordinate)

        hole = self.hole.contains_points(coordinate)

        return Exterior.astype(int) - hole.astype(int)

    def get_rasterized_mesh(self, coordinate: numpy.ndarray, shape: list) -> numpy.ndarray:
        return self.__raster__(coordinate).reshape(shape)

    def contains_points(self, Coordinate):
        if self.is_empty:
            return numpy.zeros(Coordinate.shape[0])
        else:
            Exterior = Path(list(self.exterior.coords))
            return Exterior.contains_points(Coordinate).astype(bool)


class GeometryCollection(geo.GeometryCollection):
    name: str = None
    facecolor: str = 'lightblue'
    edgecolor: str = 'black'
    alpha: float = 0.4
    index: float = 1.
    attributes: list = ('name', 'facecolor', 'edgecolor', 'alpha', 'index')

    def _pass_info_output_(function, *args, **kwargs):
        def wrapper(*args, **kwargs):
            output = function(*args, **kwargs)
            self = args[0]
            output.__class__ = self.__class__
            for attr in self.attributes:
                setattr(output, attr, getattr(self, attr))
            return output

        return wrapper

    def __init__(self, *args, name: str = None, index: float = 1, **kwargs) -> None:
        self.name = name
        super().__init__(*args, **kwargs)

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

        for geometry in self:
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
        Exterior = Path(list(self.exterior.coords))

        Exterior = Exterior.contains_points(coordinate)

        hole = self.hole.contains_points(coordinate)

        return Exterior.astype(int) - hole.astype(int)

    def get_rasterized_mesh(self, coordinate: numpy.ndarray, shape: list) -> numpy.ndarray:
        return self.__raster__(coordinate).reshape(shape)

    def contains_points(self, Coordinate):
        if self.is_empty:
            return numpy.zeros(Coordinate.shape[0])
        else:
            Exterior = Path(list(self.exterior.coords))
            return Exterior.contains_points(Coordinate).astype(bool)

    @_pass_info_output_
    def remove_non_polygon(self):
        cleaned = [e for e in self.geoms if not isinstance(e, (geo.LineString, geo.Point))]
        return GeometryCollection(cleaned)


class BackGround(Polygon):
    name: str = None
    facecolor: str = 'lightblue'
    edgecolor: str = 'black'
    alpha: float = 0.5
    index: float = 1.
    attributes: list = ('name', 'facecolor', 'edgecolor', 'alpha', 'index')

    def _pass_info_output_(function, *args, **kwargs):
        def wrapper(*args, **kwargs):
            output = function(*args, **kwargs)
            self = args[0]
            output.__class__ = self.__class__
            for attr in self.attributes:
                setattr(output, attr, getattr(self, attr))
            return output

        return wrapper

    def __init__(self, *args, center: tuple = (0, 0), name: str = None, radius: float = 1000, resolution: int = 128, index: float = 1., **kwargs) -> None:
        self.name = name
        self.resolution = 32
        super().__init__(*args, **kwargs)

    def __new__(cls, *args, center: tuple = (0, 0), name: str = None, radius: float = 1, resolution: int = 128, index: float = 1., **kwargs):
        instance = geo.Point(center).buffer(radius)
        instance.__class__ = cls
        return instance

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

    def get_rasterized_mesh(self, coordinate: numpy.ndarray, shape: list) -> numpy.ndarray:
        return self.__raster__(coordinate).reshape(shape)

    def __raster__(self, coordinate) -> numpy.ndarray:
        Exterior = Path(list(self.exterior.coords))

        Exterior = Exterior.contains_points(coordinate)

        return Exterior.astype(int)

    def contains_points(self, Coordinate):
        if self.is_empty:
            return numpy.zeros(Coordinate.shape[0])
        else:
            Exterior = Path(list(self.exterior.coords))
            return Exterior.contains_points(Coordinate).astype(bool)
# -

import numpy
import shapely.geometry as geo
from shapely import affinity
from collections.abc import Iterable
from matplotlib.patches import PathPatch
from matplotlib.collections import PatchCollection
from matplotlib.path import Path

from MPSPlots.Render2D import Scene2D, Axis
import FiberFusing

RESOLUTION = 128
ORIGIN = geo.Point([0, 0])


def Normalize(Array):
    Array = numpy.asarray(Array)
    Norm = numpy.sqrt(numpy.sum(Array**2))
    return Array / Norm


class PlotClass():
    facecolor: str = 'lightblue'
    alpha: float = 0.4
    marker: str = None
    edgecolor: str = "black"
    linewidth: float = None

    @property
    def plot_options(self):
        temp_dict = {"facecolor": self.facecolor,
                     "alpha": self.alpha,
                     "marker": self.marker,
                     "linewidth": self.linewidth,
                     "edgecolor": self.edgecolor}

        return {k: v for k, v in temp_dict.items() if v is not None}

    def Plot(self, Figure=None, Ax=None, Return=False, Show=True):
        if Ax is None:
            Figure = Scene2D(title='FiberFusing figure', unit_size=(6, 6))
            Ax = Axis(row=0, col=0, x_label='x', y_label='y', colorbar=False, equal=True)
            Figure.AddAxes(Ax)
            Figure._generate_axis_()

        self._render_(Ax)

        return Figure


class FFBuffer(PlotClass):
    Name: str = None
    Area = None
    Index: float = 1
    Raster = None

    def __init__(self, Object=None, Name=None, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

        if Object is None:
            super().__init__()
        else:
            super().__init__(Object)

    @property
    def center(self):
        return Point([self.centroid.x, self.centroid.y])

    @property
    def convex_hull(self):
        return super().convex_hull

    def get_rasterized_mesh(self, Coordinate: numpy.ndarray, Shape: list) -> numpy.ndarray:
        return self.__raster__(Coordinate).reshape(Shape)

    def _get_max_distance_(self):
        x, y = self.exterior.xy
        x = numpy.asarray(x)
        y = numpy.asarray(y)
        return numpy.sqrt(x**2 + y**2).max()

    def Clean(self):
        return self

    def Scale(self, Factor: float, Origin: geo.Point = ORIGIN):
        o = affinity.scale(self, xfact=Factor, yfact=Factor, origin=Origin)
        return to_buffer(Object=o, **self.plot_options)

    def Translate(self, shift: tuple):
        print(self.__class__)
        o = affinity.translate(geo.Polygon([ORIGIN, geo.Point(10, 10), geo.Point(10, 2)]), xoff=shift[0], yoff=shift[0])
        return to_buffer(Object=o, **self.plot_options)

    def Rotate(self, angle, Origin=ORIGIN):
        if isinstance(angle, Iterable):
            return [self.Rotate(angle=angle, Origin=Origin) for angle in angle]
        else:
            return self.__class__(Object=affinity.rotate(self, angle, origin=Origin), **self.plot_options)

    @property
    def Hole(self):
        return Polygon(self.exterior.coords) - self

    def _render_(self, Ax):
        if self.is_empty:
            return

        path = Path.make_compound_path(
            Path(numpy.asarray(self.exterior.coords)[:, :2]),
            *[Path(numpy.asarray(ring.coords)[:, :2]) for ring in self.interiors])

        patch = PathPatch(path, **self.plot_options)
        collection = PatchCollection([patch], **self.plot_options)

        Ax._ax.add_collection(collection, autolim=True)
        Ax._ax.autoscale_view()
        if self.Name is not None:
            Ax._ax.text(self.centroid.x, self.centroid.y, self.Name)


class Polygon(geo.Polygon):
    def __sub__(self, Other):
        return to_buffer(super().__sub__(Other))

    def __add__(self, Other):
        return to_buffer(super().__add__(Other))

    def __raster__(self, Coordinate):
        Exterior = Path(list(self.exterior.coords))

        Exterior = Exterior.contains_points(Coordinate)

        hole = self.Hole.contains_points(Coordinate)

        return Exterior.astype(int) - hole.astype(int)

    def contains_points(self, Coordinate):
        if self.is_empty:
            return numpy.zeros(Coordinate.shape[0])
        else:
            Exterior = Path(list(self.exterior.coords))
            return Exterior.contains_points(Coordinate).astype(bool)


class Point(FFBuffer, geo.Point):
    def __repr__(self):
        return f"Point: ({self.x:.2f}, {self.y:.2f})"

    def __neg__(self):
        return Point([-self.x, -self.y], **self.plot_options)

    def __sub__(self, Other):
        if isinstance(Other, geo.Point):
            return Point([self.x - Other.x, self.y - Other.y], **self.plot_options)

        if isinstance(Other, (list, numpy.ndarray)):
            return Point([self.x - Other[0], self.y - Other[1]], **self.plot_options)

    def __add__(self, Other):
        if isinstance(Other, geo.Point):
            return Point([self.x + Other.x, self.y + Other.y], **self.plot_options)

        if isinstance(Other, (list, numpy.ndarray)):
            return Point([self.x + Other[0], self.y + Other[1]], **self.plot_options)

    def __mul__(self, Factor: float):
        return Point([self.x * Factor, self.y * Factor], **self.plot_options)

    def __rmul__(self, Factor: float):
        return Point([self.x * Factor, self.y * Factor], **self.plot_options)

    def __truediv__(self, Factor: float):
        return Point([self.x / Factor, self.y / Factor], **self.plot_options)

    def Distance(self, Other=None):
        if Other is None:
            return numpy.sqrt(self.x**2 + self.y**2)
        else:
            return numpy.sqrt((self.x - Other.x)**2 + (self.y - Other.y)**2)

    def Shift(self, Vector: list):
        x = self.x + Vector[0]
        y = self.y + Vector[1]
        return Point([x, y], **self.plot_options)

    def Buffer(self, Radius):
        return Circle(Radius=Radius, center=self)

    def _render_(self, Ax):
        Ax._ax.text(self.x, self.y, self.Name)
        Ax._ax.scatter(self.x, self.y, s=60, **self.plot_options)


class MultiPolygon(FFBuffer, geo.MultiPolygon):
    def _render_(self, Ax):
        for polygone in self.geoms:
            to_buffer(polygone)._render_(Ax)

    def contains_points(self, Coordinate):
        Init = numpy.zeros(Coordinate.shape[0])

        for polygon in self.geoms:
            Exterior = Path(list(polygon.exterior.coords))
            Init += Exterior.contains_points(Coordinate)

        return Init.astype(bool)


class GeometryCollection(FFBuffer, geo.GeometryCollection):
    def Clean(self):
        NewClean = [e for e in self.geoms if not isinstance(e, (geo.LineString, geo.Point))]
        return GeometryCollection(NewClean)

    def _render_(self, Ax):
        for polygone in self:
            to_buffer(polygone)._render_(Ax)


class Line(FFBuffer, geo.LineString):
    @property
    def boundary(self):
        return (Point(e) for e in super().boundary.geoms)

    @property
    def MidPoint(self):
        P0, P1 = self.boundary
        return Point([(P0.x + P1.x) / 2, (P0.y + P1.y) / 2], **self.plot_options)

    def GetPosition(self, x):
        P0, P1 = self.boundary
        return P0 - (P0 - P1) * x

    def GetBissectrice(self):
        return Line(affinity.rotate(self, 90, origin=self.MidPoint), **self.plot_options)

    def MakeLength(self, Length: float):
        P0, P1 = self.boundary
        Distance = numpy.sqrt((P0.x - P1.x)**2 + (P0.y - P1.y)**2)
        Factor = Length / Distance
        return self.Extend(factor=Factor)

    def Shift(self, Vector: list):
        P0, P1 = self.boundary

        P2 = Point(P0).Shift(Vector=Vector)
        P3 = Point(P1).Shift(Vector=Vector)

        return Line([P2, P3], **self.plot_options)

    def centering(self, center):
        P0, P1 = self.boundary

        MidPoint = self.MidPoint
        xShift = center.x - MidPoint.x
        yShift = center.y - MidPoint.y
        Vector = [xShift, yShift]

        P2 = Point(P0).Shift(Vector=Vector)
        P3 = Point(P1).Shift(Vector=Vector)

        return Line([P2, P3])

    @property
    def Perpendicular(self):
        return Line(self.Rotate(90, Origin=self.MidPoint))

    def Extend(self, factor: float = 1):
        return Line(affinity.scale(self, xfact=factor, yfact=factor, origin=self.MidPoint), **self.plot_options)

    def Rotate(self, angle, Origin=None):
        if Origin is None:
            Origin = self.MidPoint
        return Line(affinity.rotate(self, angle, origin=Origin), **self.plot_options)

    @property
    def Vector(self):
        P0, P1 = self.boundary

        dy = P0.y - P1.y
        dx = P0.x - P1.x
        if dx == 0:
            return numpy.asarray([0, 1])
        else:
            return Normalize([1, dy / dx])

    def _render_(self, Ax):
        Ax._ax.plot(*self.xy, color='k', alpha=self.alpha)
        if self.Name is not None:
            Ax._ax.text(self.centroid.x, self.centroid.y, self.Name)


class Circle(Polygon):
    Radius: float = None

    def __new__(cls, Radius: float, center: Point = ORIGIN, Name: str = ''):
        Instance = Polygon.__new__(cls)
        return Instance

    def __init__(self, Radius: float, center: Point = ORIGIN, Name: str = ''):
        self.Radius = Radius
        self.Name = Name

        super(Circle, self).__init__(Point(center).buffer(Radius, resolution=RESOLUTION))

    @property
    def center(self):
        return Point([self.centroid.x, self.centroid.y])

    @center.setter
    def center(self, value):
        # print(self.__class__)
        # self = affinity.translate(geom=self, xoff=0, yoff=0)
        o = affinity.translate(self, xoff=0, yoff=0)
        print(o)
        # return to_buffer(Object=o, **self.plot_options)

    @property
    def Area(self):
        return numpy.pi * self.Radius**2

    def GetConscriptedFiber(self, Other=None, Type='Interior', Rotate: bool = False):

        if Other is None:
            return FiberFusing.Fiber.Fiber(Radius=self.Radius, center=self.center + [0, 2 * self.Radius])

        else:
            centerLine = Line([self.center, Other.center])

            Shift = numpy.sqrt((self.Radius + Other.Radius)**2 - (centerLine.length / 2)**2)

            Point = centerLine.MidPoint.Shift(centerLine.Perpendicular.Vector * Shift)

            if Type in ['Exterior', 'concave']:
                Radius = numpy.sqrt(Shift**2 + (centerLine.length / 2)**2) - self.Radius

            if Type in ['Interior', 'convex']:
                Radius = numpy.sqrt(Shift**2 + (centerLine.length / 2)**2) + self.Radius

            if Rotate:
                return FiberFusing.Fiber.Fiber(Radius=self.Radius, center=Point, **self.plot_options).Rotate(angle=180, Origin=centerLine.MidPoint)

            else:
                return FiberFusing.Fiber.Fiber(Radius=self.Radius, center=Point, **self.plot_options)

    def _render_(self, Ax):
        super()._render_(Ax)
        self.center._render_(Ax)

    def Rotate(self, angle: float, Origin: Point = None):
        Origin = self.centroid if Origin is None else Origin
        return self.__class__(Radius=self.Radius, center=self.center.Rotate(angle, Origin=Origin), Name=self.Name)

    def Scalecenter(self, Factor: float):
        Newcenter = self.center.Scale(Factor=Factor, Origin=ORIGIN)
        return self.__class__(Radius=self.Radius, center=Newcenter)


class to_buffer():
    def __new__(self, Object, **kwargs):
        if isinstance(Object, list):
            return Point(Object, **kwargs)

        if isinstance(Object, geo.Polygon):
            return Polygon(Object, **kwargs)

        if isinstance(Object, geo.MultiPolygon):
            return MultiPolygon(Object, **kwargs)

        if isinstance(Object, geo.GeometryCollection):
            return GeometryCollection(Object, **kwargs)

        if isinstance(Object, geo.LineString):
            return Line(Object, **kwargs)

        if isinstance(Object, geo.Point):
            return Point(Object, **kwargs)


# -

import FiberFusing._buffer as _buffer
import numpy

from matplotlib.patches import PathPatch
from matplotlib.collections import PatchCollection
from matplotlib.path import Path

import shapely.geometry as geo
from shapely import affinity

from MPSPlots.Render2D import Scene2D, Axis

ORIGIN = geo.Point(0, 0)


class Fiber(geo.Polygon):
    _id_to_attrs: dict = {}
    __slots__: tuple = geo.Polygon.__slots__
    inherit_attr: list = ('name', 'radius', 'center', 'core', 'color', 'marker', 'alpha', 'markersize', 'index')

    def __init__(self,
                 *args,
                 radius: float = 1,
                 center: _buffer.Point = ORIGIN,
                 name: str = 'none',
                 index: float = 1,
                 facecolor: str = 'lightblue',
                 alpha: float = 0.9,
                 edgecolor: str = "black",
                 **kwargs) -> None:

        self._id_to_attrs[id(self)] = dict(name=name,
                                           radius=radius,
                                           center=center,
                                           core=center,
                                           index=index,
                                           facecolor=facecolor,
                                           edgecolor=edgecolor,
                                           alpha=alpha)

    def __new__(cls,
                 *args,
                 radius: float = 1.,
                 center: _buffer.Point = ORIGIN,
                 name: str = 'none',
                 index: float = 1,
                 facecolor: str = 'black',
                 alpha: float = 0.9,
                 edgecolor: str = "black",
                 **kwargs) -> None:

        instance = geo.Point(center).buffer(radius)
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

    @property
    def hole(self):
        return _buffer.Polygon(_buffer.Polygon(self.exterior) - self)

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

    def get_rasterized_mesh(self, coordinate: numpy.ndarray, n_x: int, n_y: int) -> numpy.ndarray:
        return self.__raster__(coordinate).reshape([n_y, n_x])

    def contains_points(self, Coordinate):
        if self.is_empty:
            return numpy.zeros(Coordinate.shape[0])
        else:
            Exterior = Path(list(self.exterior.coords))
            return Exterior.contains_points(Coordinate).astype(bool)


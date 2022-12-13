import numpy
import logging
from dataclasses import dataclass
from collections.abc import Iterable

from matplotlib.path import Path
from itertools import combinations
from scipy.optimize import minimize_scalar
import shapely.geometry as geo

from MPSPlots.Render2D import Scene2D, Axis
import FiberFusing.Utils as Utils
from FiberFusing.Connection import Connection
import FiberFusing._buffer as _buffer

logging.basicConfig(level=logging.INFO)


ORIGIN = _buffer.Point([0, 0])
RESOLUTION = 68


@dataclass
class BaseFused():
    fiber_radius: float
    fusion_degree: float
    index: float
    gradient: object = None
    tolerance: float = 1e-2

    def __repr__(self):
        return f" {self.topology}"

    def __post_init__(self):
        logging.info("Setting up the structure geometry...")
        self._initialize_()
        self._fiber_list = None

    def _initialize_(self):
        self._fiber_rings = []
        self.custom_fiber = []
        self._hole = None
        self._topology = None
        self._added_section = None
        self._removed_section = None
        self._fiber_centers = None
        self._core_shift = None

    @property
    def Cores(self):
        return [f.core for f in self.fiber_list]

    @property
    def added_section(self):
        if self._added_section is None:
            self.compute_added_section()
        return self._added_section

    @property
    def removed_section(self):
        if self._removed_section is None:
            self.compute_removed_section()
        return self._removed_section

    @property
    def topology(self):
        if self._topology is None:
            self.compute_topology()
        return self._topology

    def compute_topology(self) -> None:
        Limit = []
        for connection in self.Connections:
            Limit.append(connection.LimitAdded)

        OverallLimit = Utils.Union(*Limit) - Utils.Union(*self.fiber_list)

        self._topology = 'convex' if self.removed_section.Area > OverallLimit.area else 'concave'

    def merge_connections(self) -> None:
        NewConnections = []

        for n, connection0 in enumerate(self.Connections):
            for m, connection1 in enumerate(self.Connections):
                if m == n:
                    continue

                union = connection1.Added.union(connection0.Added)

                if not union.is_empty:
                    logging.debug('Connection merging')
                    if connection1[0] == connection0[0]:
                        Set = (connection1[1], connection0[1])
                        new = Connection(*Set, Shift=self.virtual_shift)
                        NewConnections.append(new)
                        continue

                    if connection1[1] == connection0[0]:
                        Set = (connection1[0], connection0[1])
                        new = Connection(*Set, Shift=self.virtual_shift)
                        NewConnections.append(new)
                        continue

                    if connection1[0] == connection0[1]:
                        Set = (connection1[1], connection0[0])
                        new = Connection(*Set, Shift=self.virtual_shift)
                        NewConnections.append(new)
                        continue

                    if connection1[1] == connection0[1]:
                        Set = (connection1[0], connection0[0])
                        new = Connection(*Set, Shift=self.virtual_shift)
                        NewConnections.append(new)
                        continue

    def compute_added_section(self) -> None:
        Added = []

        for n, connection in enumerate(self.Connections):
            NewAdded = connection.Added

            Added.append(NewAdded)

        self._added_section = Utils.Union(*Added) - Utils.Union(*self.fiber_list)
        self._added_section = _buffer.GeometryCollection(self._added_section).remove_non_polygon()
        self._added_section.Area = self._added_section.area
        self._added_section.facecolor = 'green'

    def compute_removed_section(self) -> None:
        Removed = []
        for connection in self.Connections:
            Removed.append(connection.Removed)

        self._removed_section = Utils.Union(*Removed)
        self._removed_section = self._removed_section
        self._removed_section.Area = len(self.fiber_list) * self.fiber_list[0].area - Utils.Union(*self.fiber_list).area
        self._removed_section.facecolor = 'red'

    def get_max_distance(self) -> float:
        return numpy.max([f.get_max_distance() for f in self.fiber_list])

    @property
    def fiber_list(self) -> list:
        if self._fiber_list is None:
            self.populate_fiber_list()
        return self._fiber_list

    def add_fiber_ring(self, *Rings):
        for Ring in Rings:
            self._fiber_rings.append(Ring)

    def add_custom_fiber(self, *Custom):
        for fiber in Custom:
            self.custom_fiber.append(fiber)

    def optimize_geometry(self, bounds: tuple = (0, 1000)):
        self.initialize_connections()

        res = minimize_scalar(self.get_cost_value, bounds=bounds, method='bounded', options={'xatol': self.tolerance})

        return _buffer.Polygon(self.get_optimized_geometry(virtual_shift=res.x))

    def compute_core_position(self):
        for connection in self.Connections:
            connection.OptimizeCorePosition()

    def populate_fiber_list(self):
        self._fiber_list = []

        for Ring in self._fiber_rings:
            for fiber in Ring.Fibers:
                self._fiber_list.append(fiber)

        for fiber in self.custom_fiber:
            self._fiber_list.append(fiber)

        for n, fiber in enumerate(self._fiber_list):
            fiber.Name = f' Fiber {n}'

    def get_optimized_geometry(self, virtual_shift):
        Coupler = Utils.Union(*self.fiber_list, self.added_section)

        if isinstance(Coupler, geo.GeometryCollection):
            Coupler = _buffer.GeometryCollection(Coupler.geoms).clean()

        self.compute_core_position()

        return Coupler

    def initialize_connections(self) -> None:
        self.Connections = []

        for fibers in self.iterate_over_connected_fibers():
            connection = Connection(*fibers)
            self.Connections.append(connection)

    def shift_connections(self, Shift) -> None:
        for connection in self.Connections:
            connection.Shift = Shift
            connection.topology = self.topology

        self._initialize_()

    def get_cost_value(self, virtual_shift: float) -> float:
        self.virtual_shift = virtual_shift
        self.shift_connections(Shift=virtual_shift)

        Added = self.added_section.Area
        Removed = self.removed_section.Area
        Cost = abs(Added - Removed)

        logging.debug(f' Fusing optimization: {virtual_shift = :.2f} \t -> \t{Added = :.2f} \t -> {Removed = :.2f} \t -> {Cost = :.2f}')

        return Cost

    def iterate_over_connected_fibers(self) -> tuple:
        for Fiber0, Fiber1 in combinations(self.fiber_list, 2):
            if Fiber0.intersection(Fiber1).is_empty:
                continue
            else:
                yield Fiber0, Fiber1

    def get_rasterized_mesh(self,
                            coordinate: numpy.ndarray = None,
                            shape: list = [100, 100]) -> numpy.ndarray:

        if coordinate is None:
            xMin, yMin, xMax, yMax = self.Object.bounds
            x, y = numpy.mgrid[xMin:xMax:complex(shape[0]), yMin:yMax:complex(shape[1])]
            coordinate = numpy.vstack((x.flatten(), y.flatten())).T

        if isinstance(self.Object, Iterable):
            raster = []
            for polygone in self.Object.geoms:
                polygone = _buffer.Polygon(polygone)
                Exterior = Path(list(polygone.exterior.coords))

                Exterior = polygone.__raster__(coordinate)

                raster.append(Exterior.astype(float))

                Exterior = numpy.sum(raster, axis=0)

        else:
            Exterior = self.Object.__raster__(coordinate).reshape(shape)

        self.Raster = Exterior

        return self.Raster

    def Plot(self,
             show_fibers: bool = True,
             show_added: bool = True,
             show_removed: bool = True,
             **kwargs) -> Scene2D:

        Fig = Scene2D(unit_size=(6, 6))

        ax = Axis(row=0,
                  col=0,
                  x_label=r'x',
                  y_label=r'y',
                  show_grid=True,
                  equal=True)

        Fig.AddAxes(ax)._generate_axis_()

        self.Object._render_(ax)

        if show_fibers:
            for fiber in self.fiber_list:
                fiber._render_(ax)

        if show_added:
            self.added_section._render_(ax)

        if show_removed:
            self.removed_section._render_(ax)

        return Fig

    def rotate(self, *args, **kwargs):
        self.Object = self.Object.rotate(*args, **kwargs)


#  -

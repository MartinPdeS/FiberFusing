import numpy
import logging
from dataclasses import dataclass
from collections.abc import Iterable

from matplotlib.path import Path
from itertools import combinations
from scipy.optimize import minimize_scalar
import shapely.geometry as geo

from MPSPlots.Render2D import Scene2D, Axis
from FiberFusing import Utils
from FiberFusing.Connection import Connection
import FiberFusing._buffer as _buffer

logging.basicConfig(level=logging.INFO)


ORIGIN = _buffer.Point([0, 0])
RESOLUTION = 68


@dataclass
class BaseFused():
    fiber_radius: float
    """ Radius of the fiber to be used, all fibers in the structure have the same radius. """
    fusion_degree: float
    """ Value describe the fusion degree of the structure the higher the value to more fused are the fibers [0, 1]. """
    index: float
    """ Refractive index of the cladding structure. """
    tolerance: float = 1e-2
    """ Tolerance on the optimization problem which aim to minimize the difference between added and removed area of the heuristic algorithm. """
    gradient: object = None
    """ Not implemented yet. """

    def __post_init__(self):
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
    def cores(self) -> list:
        return [f.core for f in self.fiber_list]

    @property
    def added_section(self) -> _buffer.Polygon:
        if self._added_section is None:
            self.compute_added_section()
        return self._added_section

    @property
    def removed_section(self) -> _buffer.Polygon:
        if self._removed_section is None:
            self.compute_removed_section()
        return self._removed_section

    @property
    def topology(self) -> str:
        if self._topology is None:
            self.compute_topology()
        return self._topology

    def compute_topology(self) -> None:
        Limit = []
        for connection in self.Connections:
            Limit.append(connection.limit_added_area)

        OverallLimit = Utils.Union(*Limit) - Utils.Union(*self.fiber_list)
        self.compute_removed_section()

        self._topology = 'convex' if self.total_removed_area > OverallLimit.area else 'concave'

    def merge_connections(self) -> None:
        NewConnections = []

        for n, connection0 in enumerate(self.Connections):
            for m, connection1 in enumerate(self.Connections):
                if m == n:
                    continue

                union = connection1.added_section.union(connection0.added_section)

                if not union.is_empty:
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
        added_section = []

        for n, connection in enumerate(self.Connections):
            Newadded_section = connection.added_section

            added_section.append(Newadded_section)

        self._added_section = Utils.Union(*added_section) - Utils.Union(*self.fiber_list)
        self._added_section = _buffer.GeometryCollection(self._added_section, facecolor='green').remove_non_polygon()
        self._added_section.Area = self._added_section.area
        self.total_added_area = self._added_section.area

    def compute_removed_section(self) -> None:
        removed_section = []
        for connection in self.Connections:
            removed_section.append(connection.removed_section)

        self._removed_section = Utils.Union(*removed_section)
        self._removed_section = self._removed_section
        self._removed_section.facecolor = 'red'
        self.total_removed_area = len(self.fiber_list) * self.fiber_list[0].area - Utils.Union(*self.fiber_list).area

    def get_max_distance(self) -> float:
        return numpy.max([f.get_max_distance() for f in self.fiber_list])

    @property
    def fiber_list(self) -> list:
        if self._fiber_list is None:
            self.populate_fiber_list()
        return self._fiber_list

    def add_fiber_ring(self, *Rings) -> None:
        for Ring in Rings:
            self._fiber_rings.append(Ring)

    def add_custom_fiber(self, *Custom) -> None:
        for fiber in Custom:
            self.custom_fiber.append(fiber)

    def optimize_geometry(self, bounds: tuple = (0, 1000)) -> _buffer.Polygon:
        self.initialize_connections()

        res = minimize_scalar(self.get_cost_value, bounds=bounds, method='bounded', options={'xatol': self.tolerance})

        return _buffer.Polygon(self.get_optimized_geometry(virtual_shift=res.x))

    def compute_core_position(self) -> None:
        for connection in self.Connections:
            connection.optimize_core_position()

    def populate_fiber_list(self) -> None:
        self._fiber_list = []

        for Ring in self._fiber_rings:
            for fiber in Ring.Fibers:
                self._fiber_list.append(fiber)

        for fiber in self.custom_fiber:
            self._fiber_list.append(fiber)

        for n, fiber in enumerate(self._fiber_list):
            fiber.name = f' Fiber {n}'

    def get_optimized_geometry(self, virtual_shift) -> _buffer.Polygon:
        opt_geometry = Utils.Union(*self.fiber_list, self.added_section)

        if isinstance(opt_geometry, geo.GeometryCollection):
            opt_geometry = _buffer.GeometryCollection(opt_geometry.geoms).clean()

        self.compute_core_position()

        return opt_geometry

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

        self.compute_added_section()
        added_section = self.total_added_area
        removed_section = self.total_removed_area
        cost = abs(added_section - removed_section)

        logging.debug(f' Fusing optimization: {virtual_shift = :.2f} \t -> \t{added_section = :.2f} \t -> {removed_section = :.2f} \t -> {cost = :.2f}')

        return cost

    def iterate_over_connected_fibers(self) -> tuple:
        for Fiber0, Fiber1 in combinations(self.fiber_list, 2):
            if Fiber0.intersection(Fiber1).is_empty:
                continue
            else:
                yield Fiber0, Fiber1

    def get_rasterized_mesh(self, coordinate: numpy.ndarray, n_x: int, n_y: int) -> numpy.ndarray:
        if isinstance(self.Object, Iterable):
            raster = []
            for polygone in self.Object.geoms:
                polygone = _buffer.Polygon(polygone)
                Exterior = Path(list(polygone.exterior.coords))

                Exterior = polygone.__raster__(coordinate).reshape([n_y, n_x])

                raster.append(Exterior.astype(float))

                Exterior = numpy.sum(raster, axis=0)

        else:
            Exterior = self.Object.__raster__(coordinate).reshape([n_y, n_x])

        self.Raster = Exterior

        return self.Raster

    def Plot(self,
             show_fibers: bool = True,
             show_added: bool = True,
             show_removed: bool = True) -> Scene2D:

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

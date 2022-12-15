import numpy
import logging
from shapely.ops import split
from scipy.optimize import minimize_scalar

import FiberFusing._buffer as _buffer
from FiberFusing import Utils
from MPSPlots.Render2D import Scene2D, Axis


class Connection():
    def __init__(self, Fiber0, Fiber1, topology: str = None, Shift: float = None):
        self._topology = topology
        self.fiber_list = [Fiber0, Fiber1]
        self._shift = Shift
        self._center_line = None
        self._extended_center_line = None
        self._initialize_()

    def _initialize_(self):
        self._virtual_circles = None
        self._added_section = None
        self._removed = None
        self._mask = None

    @property
    def Shift(self):
        return self._shift

    @Shift.setter
    def Shift(self, value):
        self._shift = value
        self._initialize_()

    @property
    def topology(self):
        return self._topology

    @topology.setter
    def topology(self, Value):
        self._topology = Value

    def __repr__(self):
        return f"Connected fiber: {self._shift = } \n{self.topology = } \n{self.removed_section.Area = :.2f} \n{self.added_section.Area = :.2f} \n\n"

    def __getitem__(self, idx):
        return self.fiber_list[idx]

    def __setitem__(self, idx, Item):
        self.fiber_list[idx] = Item

    @property
    def virtual_circles(self,):
        if self._virtual_circles is None:
            self.compute_virtual_circles()
        return self._virtual_circles

    @property
    def mask(self,):
        if self._mask is None:
            self.compute_mask()
        return self._mask

    @property
    def added_section(self):
        if self._added_section is None:
            self.compute_added_section()
        return self._added_section

    @property
    def removed_section(self):
        if self._removed is None:
            self.compute_removed_section()
        return self._removed

    @property
    def limit_added_area(self):
        return self[0].union(self[1]).convex_hull - self[0] - self[1]

    def compute_removed_section(self) -> None:
        self._removed = _buffer.GeometryCollection(Utils.Intersection(*self))
        self._removed.Area = self[1].area + self[0].area - Utils.Union(*self).area

    def compute_topology(self) -> None:
        self._topology = 'convex' if self.removed_section.Area > self.limit_added_area.area else 'concave'

    def get_conscripted_circles(self, Type='exterior') -> _buffer.Circle:
        perpendicular_vector = self.extended_center_line.get_perpendicular().get_vector()

        Point = self.center_line.mid_point.translate(perpendicular_vector * self._shift)

        if Type.lower() in ['exterior', 'concave']:
            radius = numpy.sqrt(self._shift**2 + (self.center_line.length / 2)**2) - self[0].radius

        if Type.lower() in ['interior', 'convex']:
            radius = numpy.sqrt(self._shift**2 + (self.center_line.length / 2)**2) + self[0].radius

        return _buffer.Circle(center=Point, radius=radius, alpha=0.3, facecolor='black', name='virtual')

    def compute_virtual_circles(self) -> None:
        Circonscript0 = self.get_conscripted_circles(Type=self.topology)

        Circonscript1 = Circonscript0.rotate(angle=180, origin=self.center_line.mid_point)

        self._virtual_circles = Circonscript0, Circonscript1

    def get_connected_point(self) -> list:
        P0 = Utils.NearestPoints(self.virtual_circles[0], self[0])
        P1 = Utils.NearestPoints(self.virtual_circles[1], self[0])
        P2 = Utils.NearestPoints(self.virtual_circles[0], self[1])
        P3 = Utils.NearestPoints(self.virtual_circles[1], self[1])

        return [_buffer.Point(p) for p in [P0, P1, P2, P3]]

    def compute_mask(self) -> None:
        P0, P1, P2, P3 = self.get_connected_point()

        if self.topology.lower() == 'concave':
            mask = _buffer.Polygon(coordinate=[P0, P1, P3, P2])

            self._mask = mask - self.virtual_circles[0] - self.virtual_circles[1]

        elif self.topology.lower() == 'convex':
            mid_point = _buffer.LineString(coordinate=[self[0].center, self[1].center]).mid_point

            mask0 = _buffer.Polygon(coordinate=[mid_point, P0, P2]).scale(factor=1000, origin=mid_point)

            mask1 = _buffer.Polygon(coordinate=[mid_point, P1, P3]).scale(factor=1000, origin=mid_point)

            self._mask = Utils.Union(mask0, mask1) & Utils.Union(*self.virtual_circles)

        self._mask = _buffer.Polygon(instance=self._mask)

    def compute_added_section(self) -> None:
        if self.topology == 'convex':
            _added_section = (self.mask - self[0] - self[1]) & Utils.Intersection(*self.virtual_circles)

        elif self.topology == 'concave':
            _added_section = self.mask - self[0] - self[1] - Utils.Union(*self.virtual_circles)

        self._added_section = _buffer.GeometryCollection(_added_section).remove_non_polygon()
        self._added_section.Area = _added_section.area

    def __render__(self,
                 ax,
                 show_fiber: bool = True,
                 show_mask: bool = False,
                 show_virtual: bool = False,
                 show_added: bool = False,
                 show_removed: bool = False) -> None:

        if show_fiber:
            for fiber in self:
                fiber._render_(ax)

        if show_mask:
            self.mask._render_(ax)

        if show_virtual:
            self.virtual_circles[0]._render_(ax)
            self.virtual_circles[1]._render_(ax)

        if show_added:
            self.added_section._render_(ax)

        if show_removed:
            self.removed_section._render_(ax)

    @property
    def center_line(self) -> _buffer.LineString:
        if self._center_line is None:
            self.compute_center_line()
        return self._center_line

    def compute_center_line(self) -> None:
        self._center_line = _buffer.LineString(coordinate=[self[0].center, self[1].center])

    @property
    def extended_center_line(self) -> _buffer.LineString:
        if self._extended_center_line is None:
            self.compute_extended_center_line()
        return self._extended_center_line

    def compute_extended_center_line(self) -> None:
        line = self.center_line.MakeLength(2 * self[0].radius + 2 * self[1].radius)
        self._extended_center_line = line.extend(factor=2)

    @property
    def total_area(self) -> _buffer.Polygon:
        return Utils.Union(*self, self.added_section)

    def split_geometry(self, Geometry, Position) -> _buffer.Polygon:
        line0 = self.extended_center_line.centering(center=_buffer.Point(Position))

        line = line0.rotate(angle=90).extend(factor=2)

        temp_geo = Utils.Union(Geometry)

        if isinstance(temp_geo, _buffer.GeometryCollection):
            temp_geo = temp_geo.keep_only_largest_polygon()

        split_geometry = split(temp_geo, line).geoms

        split_geometry = split_geometry[0] if split_geometry[0].area < split_geometry[1].area else split_geometry[1]

        return _buffer.Polygon(instance=split_geometry)

    def compute_core_shift(self, x: float = 0.5) -> float:

        P0, P1 = self.extended_center_line.boundary

        _, C1 = self[0].center, self[1].center

        Position = self.extended_center_line.get_position_parametrisation(x)

        ExternalPart = self.split_geometry(Geometry=self.total_area, Position=Position)

        Cost = abs(ExternalPart.area - self[0].area / 2)

        self.core_shift = (Position - C1)

        logging.debug(f' Core positioning optimization: {x = :+.2f} \t -> \t{Cost = :<10.2f} -> \t\t{self.core_shift = }')

        return Cost

    def optimize_core_position(self) -> None:
        minimize_scalar(self.compute_core_shift, bounds=(0.50001, 0.99), method='bounded', options={'xatol': 0.001})
        self[0].core.translate(-self.core_shift)
        self[1].core.translate(self.core_shift)

    def Plot(self) -> Scene2D:
        figure = Scene2D(unit_size=(6, 6))

        ax = Axis(Row=0,
                  Col=0,
                  xLabel=r'x distance',
                  yLabel=r'y distance',
                  Legend=False,
                  Grid=True,
                  Equal=True,)

        figure.AddAxes(ax)
        figure.GenerateAxis()

        self[0]._render_(ax)
        self[1]._render_(ax)

        self.added_section._render_(ax)

        return figure


# -

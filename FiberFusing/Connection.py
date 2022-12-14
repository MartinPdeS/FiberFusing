import numpy
import logging
from shapely.ops import split
from scipy.optimize import minimize_scalar

import FiberFusing._buffer as _buffer
from FiberFusing.Utils import Union, Intersection, NearestPoints
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
        return f"Connected fiber: {self._shift = } \n{self.topology = } \n{self.Removed.Area = :.2f} \n{self.Added.Area = :.2f} \n\n"

    def __getitem__(self, idx):
        return self.fiber_list[idx]

    def __setitem__(self, idx, Item):
        self.fiber_list[idx] = Item

    @property
    def virtual_circle(self,):
        if self._virtual_circles is None:
            self.compute_virtual_circles()
        return self._virtual_circles

    @property
    def Mask(self,):
        if self._mask is None:
            self.compute_mask()
        return self._mask

    @property
    def Added(self):
        if self._added_section is None:
            self.compute_added_section()
        return self._added_section

    @property
    def Removed(self):
        if self._removed is None:
            self.compute_removed_section()
        return self._removed

    @property
    def limit_added_area(self):
        return self[0].union(self[1]).convex_hull - self[0] - self[1]

    def compute_removed_section(self):
        self._removed = Intersection(*self)
        self._removed.Area = self[1].area + self[0].area - Union(*self).area

    def compute_topology(self) -> None:
        self._topology = 'convex' if self.Removed.Area > self.limit_added_area.area else 'concave'

    def get_conscripted_circles(self, Type='Exterior') -> _buffer.Circle:
        perpendicular_vector = self.extended_center_line.Perpendicular.Vector

        Point = self.center_line.mid_point.translate(perpendicular_vector * self._shift)

        if Type.lower() in ['exterior', 'concave']:
            radius = numpy.sqrt(self._shift**2 + (self.center_line.length / 2)**2) - self[0].radius

        if Type.lower() in ['interior', 'convex']:
            radius = numpy.sqrt(self._shift**2 + (self.center_line.length / 2)**2) + self[0].radius

        return _buffer.Circle(center=Point, radius=radius)

    def compute_virtual_circles(self) -> None:
        Circonscript0 = self.get_conscripted_circles(Type=self.topology)

        Circonscript1 = Circonscript0.rotate(angle=180, origin=self.center_line.mid_point)

        self._virtual_circles = Circonscript0, Circonscript1

    def get_connected_point(self) -> tuple:
        P0 = NearestPoints(self.virtual_circle[0], self[0])
        P1 = NearestPoints(self.virtual_circle[1], self[0])
        P2 = NearestPoints(self.virtual_circle[0], self[1])
        P3 = NearestPoints(self.virtual_circle[1], self[1])

        return P0, P1, P2, P3

    def compute_mask(self) -> None:
        P0, P1, P2, P3 = self.get_connected_point()

        if self.topology == 'concave':
            Mask = _buffer.Polygon([P0, P1, P3, P2])

            self._mask = Mask - self.virtual_circle[0] - self.virtual_circle[1]

        elif self.topology == 'convex':
            mid_point = _buffer.LineString([self[0].center, self[1].center]).mid_point

            mask0 = _buffer.Polygon([mid_point, P0, P2]).scale(factor=1000, origin=mid_point)

            mask1 = _buffer.Polygon([mid_point, P1, P3]).scale(factor=1000, origin=mid_point)

            self._mask = Union(mask0, mask1) & Union(*self.virtual_circle)

        self._mask = _buffer.Polygon(self._mask)

    def compute_added_section(self) -> None:
        if self.topology == 'convex':
            _added_section = (self.Mask - self[0] - self[1]) & Intersection(*self.virtual_circle)

        elif self.topology == 'concave':
            _added_section = self.Mask - self[0] - self[1] - Union(*self.virtual_circle)

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
            self.Mask._render_(ax)

        if show_virtual:
            self.virtual_circle[0]._render_(ax)
            self.virtual_circle[1]._render_(ax)

        if show_added:
            self.Added._render_(ax)

        if show_removed:
            self.Removed._render_(ax)

    @property
    def center_line(self):
        if self._center_line is None:
            self.compute_center_line()
        return self._center_line

    def compute_center_line(self) -> None:
        self._center_line = _buffer.LineString([self[0].center, self[1].center])

    @property
    def extended_center_line(self):
        if self._extended_center_line is None:
            self.compute_extended_center_line()
        return self._extended_center_line

    def compute_extended_center_line(self) -> None:
        line = self.center_line.MakeLength(2 * self[0].radius + 2 * self[1].radius)
        self._extended_center_line = _buffer.LineString(line.intersection(Union(*self)))

    @property
    def TotalArea(self):
        return Union(*self, self.Added)

    def Split(self, Geometry, Position) -> _buffer.Polygon:
        line = self.extended_center_line.centering(center=_buffer.Point(Position))

        line = line.rotate(angle=90).Extend(factor=2)

        split_geometry = split(Geometry, line).geoms

        split_geometry = split_geometry[0] if split_geometry[0].area < split_geometry[1].area else split_geometry[1]

        return _buffer.Polygon(split_geometry)

    def compute_core_shift(self, x: float = 0.5) -> float:

        P0, P1 = self.extended_center_line.boundary

        _, C1 = self[0].center, self[1].center

        Position = self.extended_center_line.get_position_parametrisation(x)

        ExternalPart = self.Split(Geometry=self.TotalArea, Position=Position)

        Cost = abs(ExternalPart.area - self[0].area / 2)

        self.core_shift = (Position - C1)

        logging.debug(f' Core positioning optimization: {x = :+.2f} \t -> \t{Cost = :<10.2f} -> \t\t{self.core_shift = }')

        return Cost

    def optimize_core_position(self) -> None:
        minimize_scalar(self.compute_core_shift, bounds=(0.50001, 0.99), method='bounded', options={'xatol': 0.001})
        self[0].core.translate(-self.core_shift)
        self[1].core.translate(self.core_shift)

    def Plot(self) -> Scene2D:
        Figure = Scene2D('FiberFusing figure', UnitSize=(6, 6))

        ax = Axis(Row=0,
                  Col=0,
                  xLabel=r'x distance',
                  yLabel=r'y distance',
                  Title=f'Debug',
                  Legend=False,
                  Grid=True,
                  Equal=True,)

        Figure.AddAxes(ax)
        Figure.GenerateAxis()

        self[0]._render_(ax)
        self[1]._render_(ax)

        self.Added._render_(ax)

        return figure


# -

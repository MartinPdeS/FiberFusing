import numpy
import logging
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
        self._removed.Area = self[1].area + self[0].area - Utils.Union(*self, as_composition=True).area

    def compute_topology(self) -> None:
        self._topology = 'convex' if self.removed_section.Area > self.limit_added_area.area else 'concave'

    def get_conscripted_circles(self, Type='exterior') -> _buffer.CircleComposition:
        perpendicular_vector = self.extended_center_line.copy().get_perpendicular().get_vector()

        point = self.center_line.mid_point.translate(perpendicular_vector * self._shift)

        if Type.lower() in ['exterior', 'concave']:
            radius = numpy.sqrt(self._shift**2 + (self.center_line.length / 2)**2) - self[0].radius

        if Type.lower() in ['interior', 'convex']:
            radius = numpy.sqrt(self._shift**2 + (self.center_line.length / 2)**2) + self[0].radius

        return _buffer.CircleComposition(position=point, radius=radius, alpha=0.3, facecolor='black', name='virtual')

    def compute_virtual_circles(self) -> None:
        Circonscript0 = self.get_conscripted_circles(Type=self.topology)

        Circonscript1 = Circonscript0.copy()

        Circonscript1.rotate(angle=180, origin=self.center_line.mid_point)

        self._virtual_circles = Circonscript0, Circonscript1

    def get_connected_point(self) -> list:
        P0 = Utils.NearestPoints(self.virtual_circles[0], self[0])
        P1 = Utils.NearestPoints(self.virtual_circles[1], self[0])
        P2 = Utils.NearestPoints(self.virtual_circles[0], self[1])
        P3 = Utils.NearestPoints(self.virtual_circles[1], self[1])

        return [_buffer.PointComposition(position=(p.x, p.y)) for p in [P0, P1, P2, P3]]

    def compute_mask(self) -> None:
        P0, P1, P2, P3 = self.get_connected_point()

        if self.topology.lower() == 'concave':

            mask = _buffer.PolygonComposition(coordinates=[P0._shapely_object, P1._shapely_object, P3._shapely_object, P2._shapely_object])

            self._mask = (mask - self.virtual_circles[0] - self.virtual_circles[1])

        elif self.topology.lower() == 'convex':
            mid_point = _buffer.LineStringComposition(coordinates=[self[0].center, self[1].center]).mid_point

            mask0 = _buffer.PolygonComposition(coordinates=[mid_point._shapely_object, P0._shapely_object, P2._shapely_object]).scale(factor=1000, origin=mid_point._shapely_object)

            mask1 = _buffer.PolygonComposition(coordinates=[mid_point._shapely_object, P1._shapely_object, P3._shapely_object]).scale(factor=1000, origin=mid_point._shapely_object)

            self._mask = (Utils.Union(mask0, mask1, as_composition=True) & Utils.Union(*self.virtual_circles, as_composition=True))

        # self._mask = _buffer.PolygonComposition(instance=self._mask)

    def compute_added_section(self) -> None:
        if self.topology == 'convex':
            self._added_section = (self.mask - self[0] - self[1]) & (self.virtual_circles[0].intersection(self.virtual_circles[1]))

        elif self.topology == 'concave':
            self._added_section = self.mask - self[0] - self[1] - (self.virtual_circles[0].union(self.virtual_circles[1]))

        self._added_section.Area = self._added_section.area

    def _render_(self,
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
    def center_line(self) -> _buffer.LineStringComposition:
        if self._center_line is None:
            self.compute_center_line()
        return self._center_line

    def compute_center_line(self) -> None:
        self._center_line = _buffer.LineStringComposition(coordinates=[self[0].center, self[1].center])

    @property
    def extended_center_line(self) -> _buffer.LineStringComposition:
        if self._extended_center_line is None:
            self.compute_extended_center_line()
        return self._extended_center_line

    def compute_extended_center_line(self) -> None:
        line = self.center_line.copy()
        line.make_length(2 * self[0].radius + 2 * self[1].radius)
        self._extended_center_line = line.extend(factor=2)
        self._extended_center_line.intersect(Utils.Union(*self, as_composition=True))

    @property
    def total_area(self) -> _buffer.PolygonComposition:
        return Utils.Union(*self, self.added_section, as_composition=True)

    def split_geometry(self, Geometry, position) -> _buffer.PolygonComposition:
        line = self.extended_center_line.copy()

        line.centering(center=position).rotate(angle=90).extend(factor=2)

        external_part = Utils.Union(Geometry, as_composition=True).remove_non_polygon()

        return external_part.split_with_line(line=line, return_type='smallest')

    def compute_core_shift(self, x: float = 0.5) -> float:
        _, C1 = self[0].core, self[1].core

        position = self.extended_center_line.get_position_parametrisation(x)

        external_part = self.split_geometry(Geometry=self.total_area, position=position)

        Cost = abs(external_part.area - self[0].area / 2)

        self.core_shift = (position - C1)

        logging.debug(f' Core positioning optimization: {x = :+.2f} \t -> \t{Cost = :<10.2f} -> \t\t{self.core_shift = }')

        return Cost

    def optimize_core_position(self) -> None:
        self[0].core = self[0].position
        self[1].core = self[1].position

        minimize_scalar(self.compute_core_shift, bounds=(0.50001, 0.99), method='bounded', options={'xatol': 0.001})
        self[0].core.translate(-self.core_shift)
        self[1].core.translate(self.core_shift)

    def plot(self) -> Scene2D:
        figure = Scene2D(unit_size=(6, 6))

        ax = Axis(row=0,
                  col=0,
                  x_label=r'x distance',
                  y_label=r'y distance',
                  legend=False,
                  show_grid=True,
                  equal=True,)

        figure.add_axes(ax)
        figure._generate_axis_()

        self[0]._render_(ax)
        self[1]._render_(ax)

        self.added_section._render_(ax)

        return figure


# -

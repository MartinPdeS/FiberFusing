import numpy
import logging
from shapely.ops import split
from scipy.optimize import minimize_scalar

import FiberFusing.Buffer as Buffer
import FiberFusing._buffer as _buffer
from FiberFusing.Utils import Union, Intersection, NearestPoints
from MPSPlots.Render2D import Scene2D, Axis


class Connection():
    def __init__(self, Fiber0, Fiber1, topology: str = None, Shift: float = None):
        self._topology = topology
        self.Fibers = [Fiber0, Fiber1]
        self._Shift = Shift
        self._centerLine = None
        self._extended_center_line = None
        self.Initialize()

    def Initialize(self):
        self._Virtual = None
        self._Added = None
        self._Removed = None
        self._Mask = None

    @property
    def Shift(self):
        return self._Shift

    @Shift.setter
    def Shift(self, Value):
        self._Shift = Value
        self.Initialize()

    @property
    def topology(self):
        return self._topology

    @topology.setter
    def topology(self, Value):
        self._topology = Value

    def __repr__(self):
        return f"Connected fiber: {self._Shift = } \n{self.topology = } \n{self.Removed.Area = :.2f} \n{self.Added.Area = :.2f} \n\n"

    def __getitem__(self, idx):
        return self.Fibers[idx]

    def __setitem__(self, idx, Item):
        self.Fibers[idx] = Item

    @property
    def Virtual(self,):
        if self._Virtual is None:
            self.compute_virtual_circles()
        return self._Virtual

    @property
    def Mask(self,):
        if self._Mask is None:
            self.compute_mask()
        return self._Mask

    @property
    def Added(self):
        if self._Added is None:
            self.compute_added_section()
        return self._Added

    @property
    def Removed(self):
        if self._Removed is None:
            self.compute_removed_section()
        return self._Removed

    @property
    def get_limit_added_area(self):
        return self[0].union(self[1]).convex_hull - self[0] - self[1]

    def compute_removed_section(self):
        self._Removed = Intersection(*self)
        self._Removed.Area = self[1].area + self[0].area - Union(*self).area
        self._Removed.facecolors = 'k'

    def Computetopology(self):
        self._topology = 'convex' if self.Removed.Area > self.get_limit_added_area.area else 'concave'

    def get_conscripted_circles(self, Type='Exterior'):
        PerpendicularVector = self.extended_center_line.Perpendicular.Vector

        Point = self.centerLine.MidPoint.Shift(PerpendicularVector * self._Shift)

        if Type in ['Exterior', 'concave']:
            Radius = numpy.sqrt(self._Shift**2 + (self.centerLine.length / 2)**2) - self[0].radius

        if Type in ['Interior', 'convex']:
            Radius = numpy.sqrt(self._Shift**2 + (self.centerLine.length / 2)**2) + self[0].radius

        return Point.Buffer(Radius)

    def compute_virtual_circles(self):

        Circonscript0 = self.get_conscripted_circles(Type=self.topology)

        Circonscript1 = Circonscript0.Rotate(angle=180, Origin=self.centerLine.MidPoint)

        self._Virtual = Circonscript0, Circonscript1

    def get_connected_point(self):
        P0 = NearestPoints(self.Virtual[0], self[0])
        P1 = NearestPoints(self.Virtual[1], self[0])
        P2 = NearestPoints(self.Virtual[0], self[1])
        P3 = NearestPoints(self.Virtual[1], self[1])

        return P0, P1, P2, P3

    def compute_mask(self) -> None:
        P0, P1, P2, P3 = self.get_connected_point()

        if self.topology == 'concave':
            Mask = Buffer.Polygon([P0, P1, P3, P2])

            self._Mask = Mask - self.Virtual[0] - self.Virtual[1]

        elif self.topology == 'convex':
            MidPoint = Buffer.Line([self[0].center, self[1].center]).MidPoint

            mask0 = _buffer.Polygon([MidPoint, P0, P2]).scale(factor=1000, origin=MidPoint)

            mask1 = _buffer.Polygon([MidPoint, P1, P3]).scale(factor=1000, origin=MidPoint)

            self._Mask = Union(mask0, mask1) & Union(*self.Virtual)

        self._Mask = Buffer.to_buffer(self._Mask)

    def compute_added_section(self):
        if self.topology == 'convex':
            self._Added = (self.Mask - self[0] - self[1]) & Intersection(*self.Virtual)

        elif self.topology == 'concave':
            self._Added = self.Mask - self[0] - self[1] - Union(*self.Virtual)

        self._Added = Buffer.to_buffer(self._Added, Area=self._Added.area).Clean()

    def compute_removed_section(self) -> None:
        a = Union(*self.Fibers)
        self._Removed = Intersection(*self)
        self._Removed.Area = self[1].area + self[0].area - Union(*self.Fibers).area
        self._Removed.facecolor = 'r'

    def __plot__(self, ax,
                       Fibers: bool = True,
                       Mask: bool = False,
                        Virtual: bool = False,
                        Added: bool = False,
                        Removed: bool = False,
                        **kwargs):

        if Fibers:
            for fiber in self:
                fiber._render_(ax)

        if Mask:
            self.Mask._render_(ax)

        if Virtual:
            self.Virtual[0]._render_(ax)
            self.Virtual[1]._render_(ax)

        if Added:
            self.Added._render_(ax)

        if Removed:
            self.Removed._render_(ax)

    @property
    def centerLine(self):
        if self._centerLine is None:
            self.compute_center_line()
        return self._centerLine

    def compute_center_line(self) -> None:
        self._centerLine = Buffer.Line([self[0].center, self[1].center])

    @property
    def extended_center_line(self):
        if self._extended_center_line is None:
            self.compute_extended_center_line()
        return self._extended_center_line

    def compute_extended_center_line(self):
        Line = self.centerLine.MakeLength(2 * self[0].radius + 2 * self[1].radius)
        self._extended_center_line = Buffer.Line(Line.intersection(Union(*self)))

    @property
    def TotalArea(self):
        return Union(*self, self.Added)

    def Split(self, Geometry, Position):

        Line = self.extended_center_line.centering(center=Buffer.Point(Position))

        Line = Line.Rotate(angle=90)

        Splitted = split(Geometry, Line).geoms

        Splitted = Splitted[0] if Splitted[0].area < Splitted[1].area else Splitted[1]

        return Buffer.Polygon(Splitted)

    def ComputeCoreShift(self, x: float = 0.5):

        P0, P1 = self.extended_center_line.boundary

        C0, C1 = self[0].center, self[1].center

        Position = self.extended_center_line.GetPosition(x)

        ExternalPart = self.Split(Geometry=self.TotalArea, Position=Position)

        Cost = abs(ExternalPart.area - self[0].area / 2)

        self.CoreShift = (Position - C1)

        logging.debug(f' Core positioning optimization: {x = :+.2f} \t -> \t{Cost = :<10.2f} -> \t\t{self.CoreShift = }')

        return Cost

    def OptimizeCorePosition(self):
        res = minimize_scalar(self.ComputeCoreShift, bounds=(0.50001, 0.99), method='bounded', options={'xatol': 0.001})
        self[0].core.translate(-self.CoreShift)
        self[1].core.translate(self.CoreShift)

    def Plot(self):
        Figure = Scene2D('FiberFusing figure', UnitSize=(6,6))

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

        Figure.Show()


# -

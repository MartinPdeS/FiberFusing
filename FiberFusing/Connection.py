import numpy, logging
from shapely.ops import split
from scipy.optimize import minimize_scalar

import FiberFusing.Buffer as Buffer
from FiberFusing.Utils import Union, Intersection, NearestPoints
import MPSPlots.Plots as Plots

class Connection():
    def __init__(self, Fiber0, Fiber1, Topology: str=None, Shift: float=None):
        self._Topology = Topology
        self.Fibers = [Fiber0, Fiber1]
        self._Shift = Shift
        self._CenterLine = None
        self._ExtendedCenterLine = None
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
    def Topology(self):
        return self._Topology


    @Topology.setter
    def Topology(self, Value):
        self._Topology = Value



    def __repr__(self):
        return f"Connected fiber: {self._Shift = } \n{self.Topology = } \n{self.Removed.Area = :.2f} \n{self.Added.Area = :.2f} \n\n"


    def __getitem__(self, idx):
        return self.Fibers[idx]

    def __setitem__(self, idx, Item):
        self.Fibers[idx] = Item

    @property
    def Virtual(self,):
        if self._Virtual is None:
            self.ComputeVirtual()
        return self._Virtual


    @property
    def Mask(self,):
        if self._Mask is None:
            self.ComputeMask()
        return self._Mask


    @property
    def Added(self):
        if self._Added is None:
            self.ComputeAdded()
        return self._Added

    @property
    def Removed(self):
        if self._Removed is None:
            self.ComputeRemoved()
        return self._Removed


    @property
    def LimitAdded(self):
        return self[0].union(self[1]).convex_hull - self[0] - self[1]


    def ComputeRemoved(self):
        self._Removed = Intersection( *self )
        self._Removed.Area = self[1].area + self[0].area - Union(*self).area
        self._Removed.facecolors = 'k'


    def ComputeTopology(self):
        self._Topology = 'convex' if self.Removed.Area > self.LimitAdded.area else 'concave'
   

    def GetConscriptedCircle(self, Type='Exterior'):
        PerpendicularVector = self.ExtendedCenterLine.Perpendicular.Vector

        Point = self.CenterLine.MidPoint.Shift( PerpendicularVector * self._Shift)

        if Type in ['Exterior', 'concave']:
            Radius = numpy.sqrt( self._Shift**2 +  (self.CenterLine.length/2)**2 ) - self[0].Radius

        if Type in ['Interior', 'convex']:
            Radius = numpy.sqrt( self._Shift**2 + (self.CenterLine.length/2)**2 ) + self[0].Radius

        return Point.Buffer(Radius)


    def ComputeVirtual(self):

        Circonscript0 = self.GetConscriptedCircle(Type=self.Topology)

        Circonscript1 = Circonscript0.Rotate(Angle=180, Origin=self.CenterLine.MidPoint)

        self._Virtual = Circonscript0, Circonscript1


    def GetConnectedPoint(self):
        P0 = NearestPoints(self.Virtual[0], self[0])
        P1 = NearestPoints(self.Virtual[1], self[0])
        P2 = NearestPoints(self.Virtual[0], self[1])
        P3 = NearestPoints(self.Virtual[1], self[1])

        return P0, P1, P2, P3


    def ComputeMask(self):
        P0, P1, P2, P3 = self.GetConnectedPoint()

        if self.Topology == 'concave':
            Mask = Buffer.Polygon([P0, P1, P3, P2])

            self._Mask = Mask - self.Virtual[0] - self.Virtual[1]


        elif self.Topology == 'convex':
            MidPoint = Buffer.Line([self[0].Center, self[1].Center]).MidPoint

            mask0 = Buffer.Polygon([MidPoint, P0, P2]).Scale(Factor=1000, Origin=MidPoint)

            mask1 = Buffer.Polygon([MidPoint, P1, P3]).Scale(Factor=1000, Origin=MidPoint)

            self._Mask = Union( mask0, mask1 ) & Union( *self.Virtual )

        self._Mask = Buffer.ToBuffer(self._Mask)


    def ComputeAdded(self):
        if self.Topology == 'convex':
            self._Added = ( self.Mask - self[0] - self[1] ) & Intersection(*self.Virtual)

        elif self.Topology == 'concave':
            self._Added = self.Mask - self[0] - self[1] - Union(*self.Virtual)
 
        self._Added = Buffer.ToBuffer( self._Added, Area=self._Added.area ).Clean()


    def ComputeRemoved(self):
        a = Union(*self.Fibers)
        self._Removed = Intersection( *self )
        self._Removed.Area = self[1].area + self[0].area - Union(*self.Fibers).area
        self._Removed.facecolor = 'r'


    def __plot__(self, ax, 
                       Fibers: bool=True, 
                       Mask: bool=False, 
                        Virtual: bool=False, 
                        Added: bool=False, 
                        Removed: bool=False,
                        **kwargs):

        if Fibers:
            for fiber in self:
                fiber.__render__(ax)

        if Mask:
            self.Mask.__render__(ax)

        if Virtual:
            self.Virtual[0].__render__(ax)
            self.Virtual[1].__render__(ax)

        if Added:
            self.Added.__render__(ax)

        if Removed:
            self.Removed.__render__(ax)


    @property
    def CenterLine(self):
        if self._CenterLine is None:
            self.ComputeCenterLine()
        return self._CenterLine


    def ComputeCenterLine(self):
        self._CenterLine = Buffer.Line([self[0].Center, self[1].Center])


    @property
    def ExtendedCenterLine(self):
        if self._ExtendedCenterLine is None:
            self.ComputeExtendedCenterLine()
        return self._ExtendedCenterLine


    def ComputeExtendedCenterLine(self):
        Line = self.CenterLine.MakeLength(2*self[0].Radius + 2*self[1].Radius)
        self._ExtendedCenterLine = Buffer.Line( Line.intersection( Union(*self) ) )


    @property
    def TotalArea(self):
        return Union(*self, self.Added)


    def Split(self, Geometry, Position):

        Line = self.ExtendedCenterLine.Centering(Center=Buffer.Point(Position))

        Line = Line.Rotate(Angle=90)

        Splitted = split(Geometry, Line).geoms

        Splitted = Splitted[0] if Splitted[0].area < Splitted[1].area else Splitted[1]
        
        return Buffer.Polygon(Splitted)



    def ComputeCoreShift(self, x: float=0.5):

        P0, P1 = self.ExtendedCenterLine.boundary

        C0, C1 = self[0].Center, self[1].Center

        Position = self.ExtendedCenterLine.GetPosition(x)

        ExternalPart = self.Split(Geometry=self.TotalArea, Position=Position)

        Cost = abs(ExternalPart.area - self[0].Area/2)

        self.CoreShift = (Position-C1)

        logging.debug(f' Core positioning optimization: {x = :+.2f} \t -> \t{Cost = :<10.2f} -> \t\t{self.CoreShift = }')

        return Cost



    def OptimizeCorePosition(self):
        res = minimize_scalar(self.ComputeCoreShift, bounds=(0.50001, 0.99) , method='bounded', options={'xatol': 0.001})

        self[0].Core -= self.CoreShift
        self[1].Core += self.CoreShift



    def Plot(self):
        Figure = Plots.Scene('FiberFusing figure', UnitSize=(6,6))

        ax = Plots.Axis(Row              = 0,
                        Col              = 0,
                        xLabel           = r'x distance',
                        yLabel           = r'y distance',
                        Title            = f'Debug',
                        Legend           = False,
                        Grid             = True,
                        Equal            = True,)

        Figure.AddAxes(ax)
        Figure.GenerateAxis()

        self[0].__render__(ax)
        self[1].__render__(ax)

        self.Added.__render__(ax)

        Figure.Show()


















# -

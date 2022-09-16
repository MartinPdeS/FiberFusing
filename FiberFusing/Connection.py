import numpy, logging
from shapely.ops import split
from scipy.optimize import minimize_scalar

from FiberFusing.Utils import Union, Intersection, NearestPoints, Rotate, _Fiber
from FiberFusing.Buffer import Buffer, BufferPoint, BufferPolygon, BufferLine

import FiberFusing.Plotting.Plots as Plots

class Connection():
    def __init__(self, Fiber0, Fiber1):
        self.Fibers = [Fiber0, Fiber1]
        self._Shift = None
        self.Initialize()


    def Initialize(self, Topology: str=None):
        self._Topology = Topology
        self._Virtual = None
        self._Added = None
        self._Removed = None
        self._Mask = None
        self[0].CorePosition = self[0].Center
        self[1].CorePosition = self[1].Center


    def SetShift(self, Shift, Topology: str=None):
        self._Shift = Shift
        self.Initialize(Topology=Topology)


    def __repr__(self):
        return f"{self._Shift = } \n{self.Topology = } \n{self.Removed.Area = :.2f} \n{self.Added.Area = :.2f} \n\n"


    def __getitem__(self, idx):
        return self.Fibers[idx]

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
    def Topology(self):
        if self._Topology is None:
            self.ComputeTopology()
        return self._Topology


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
        self._Removed.Color = 'k'


    def ComputeTopology(self):
        self._Topology = 'convex' if self.Removed.Area > self.LimitAdded.area else 'concave'
   

    def ComputeVirtual(self):
        ParallelLine = BufferLine([self[0].Center, self[1].Center] )

        PerpendicularLine = ParallelLine.GetBissectrice().Extend(factor=30)

        CoreDistance = self[0].Center.Distance(self[1].Center)

        Point = ParallelLine.MidPoint.Shift(PerpendicularLine.Vector * self._Shift)

        if self.Topology == 'convex':
            Radius = numpy.sqrt( self._Shift**2 + (CoreDistance/2)**2 ) + self[0].Radius

        if self.Topology == 'concave':
            Radius = numpy.sqrt( self._Shift**2 +  (CoreDistance/2)**2 ) - self[0].Radius

        Circonscript0 = Point.Buffer(Radius)

        Circonscript1 = Rotate(Object=Circonscript0, Angle=[180], Origin=ParallelLine.MidPoint)[0]

        Circonscript0 = BufferPolygon(Circonscript0, Color='r', Alpha=0.1, Name=' Virtual 0')
        Circonscript1 = BufferPolygon(Circonscript1, Color='r', Alpha=0.1, Name=' Virtual 0')

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
            Mask = BufferPolygon([P0, P1, P3, P2])

            self._Mask = Mask - self.Virtual[0] - self.Virtual[1]

        elif self.Topology == 'convex':
            MidPoint = BufferLine([self[0].Center, self[1].Center]).MidPoint

            mask0 = BufferPolygon([MidPoint, P0, P2]).Scale(Factor=10, Origin=MidPoint)

            mask1 = BufferPolygon([MidPoint, P1, P3]).Scale(Factor=10, Origin=MidPoint)

            self._Mask = Union( mask0, mask1 ) & Union( *self.Virtual )

        self._Mask = Buffer(self._Mask, Color='k')


    def ComputeAdded(self):
        if self.Topology == 'convex':
            self._Added = ( self.Mask - self[0] - self[1] ) & Intersection(*self.Virtual)

        elif self.Topology == 'concave':
            self._Added = self.Mask - self[0] - self[1] - Union(*self.Virtual)
 
        self._Added = Buffer( self._Added, Color='k', Area=self._Added.area )


    def ComputeRemoved(self):
        self._Removed = Intersection( *self )
        self._Removed.Area = self[1].area + self[0].area - Union(*self.Fibers).area
        self._Removed.Color = 'k'


    def __plot__(self, ax, Fibers: bool=True, 
                        Mask: bool=False, 
                        Virtual: bool=False, 
                        Added: bool=False, 
                        Removed: bool=False,
                        **kwargs):
        if Fibers:
            for fiber in self:
                fiber.__plot__(ax)

        if Mask:
            self.Mask.__plot__(ax)

        if Virtual:
            self.Virtual[0].__plot__(ax)
            self.Virtual[1].__plot__(ax)

        if Added:
            self.Added.__plot__(ax)

        if Removed:
            self.Removed.__plot__(ax)


    @property
    def CoreLine(self):
        return BufferLine([self[0].Center, self[1].Center])


    @property
    def TotalArea(self):
        return Union(*self, self.Added)


    def Split(self, Geometry, Position):
        Radial = self.CoreLine

        Line = Radial.Centering(Center=BufferPoint(Position))

        Line = Line.Rotate(Angle=90).MakeLength(self[0].Radius*5)

        return [ Buffer( geo, Color='r' ) for geo in split(Geometry, Line).geoms ]


    def UpdateCorePosition(self):
        self[0].UpdateCorePosition()
        self[1].UpdateCorePosition()


    def ComputeCoreShift(self, x: float=0.5):
        
        P0 = self[0].Center.ToNumpy()
        P1 = self[1].Center.ToNumpy()

        Position = P0 - x * (P0-P1)

        ExternalPart  =  self.Split(Geometry=self.TotalArea, Position=Position)[1]

        Cost = abs(ExternalPart.area - self[0].Area/2)

        CoreShift = Position-P0

        logging.info(f' {x = :+.2f} \t -> \t{Cost = :.2f} -> \t\t{CoreShift = }')

        self[0].CoreShift += CoreShift
        self[1].CoreShift += CoreShift
        self.CoreShift = BufferPoint(CoreShift)
        # Plots.PlotShapely(*self, self.TotalArea, ExternalPart)

        return Cost


    def OptimizeCorePosition(self):
        res = minimize_scalar(self.ComputeCoreShift, bounds=(-2, 2) , method='bounded', options={'xatol': 0.001})
        print(self.CoreShift)

    def Plot(self, **kwargs):
        Fig = Plots.Scene('SuPyMode Figure', UnitSize=(6,6))
        Colorbar = Plots.ColorBar(Discreet=True, Position='right')

        ax = Plots.Axis(Row              = 0,
                  Col              = 0,
                  xLabel           = r'x',
                  yLabel           = r'y',
                  Title            = f'Debug',
                  Legend           = False,
                  Grid             = False,
                  Equal            = True,
                  Colorbar         = None,
                  xScale           = 'linear',
                  yScale           = 'linear')

        self.__plot__(ax, **kwargs)

        self.CoreLine.__plot__(ax)

        temp = self.GetExternalMask()
        temp.__plot__(ax)


        Fig.AddAxes(ax)

        Fig.Show()


















# -

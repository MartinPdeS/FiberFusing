import numpy, logging
from typing import Union as TypeUnion
from dataclasses import dataclass

from matplotlib.path import Path
from itertools import combinations
from scipy.optimize import minimize_scalar
from shapely.geometry import GeometryCollection, LineString, Point


from SuPyMode.Plotting.Plots import Scene, Axis, Mesh, Contour, ColorBar
from SuPyMode.Geometry.Rings import FiberRing
from SuPyMode.Geometry.Connection import Connection
from SuPyMode.Geometry.Utils import ( Buffer,
                                      BufferPoint, 
                                      BufferPolygon, 
                                      BufferMultiPolygon, 
                                      Union)





@dataclass
class BaseFused():
    FiberRadius: float
    Fusion: float
    Angle: float
    Index: float
    debug: bool
    Gradient: object = None
    Tolerance: float = 1e-2

    def __repr__(self):
        return f" {self.Topology}"

    def __post_init__(self):
        self.Angle = numpy.asarray(self.Angle)
        self.N = len(self.Angle)
        self.Initialize()
        self._Fibers = None


    def Initialize(self):
        self._Rings = []
        self._Hole = None
        self._Topology = None
        self._Added = None
        self._Removed = None
        self._Centers = None
        self._CoreShift = None


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
    def Topology(self):
        if self._Topology is None:
            self.ComputeTopology()
        return self._Topology


    def ComputeTopology(self) -> None:
        Limit = []
        for connection in self.Connections:
            Limit.append(connection.LimitAdded)

        OverallLimit = Union(*Limit)
        
        self._Topology = 'convex' if self.Removed.Area > OverallLimit.area else 'concave'


    def ComputeAdded(self) -> None:
        Added = []
        for connection in self.Connections:
            Added.append(connection.Added)

        self._Added = Union(*Added)
        self._Added.Area = self._Added.area


    def ComputeRemoved(self) -> None:
        Removed = []
        for connection in self.Connections:
            Removed.append(connection.Removed)

        self._Removed = Union(*Removed)
        self._Removed.Area = len(self.Fibers) * self.Fibers[0].area - Union(*self.Fibers).area


    def GetMaxDistance(self) -> float:
        return numpy.max( [ f.GetMaxDistance() for f in self.Fibers ] )


    @property
    def Fibers(self):
        if self._Fibers is None:
            self.ComputeFibers()
        return self._Fibers


    @property
    def Hole(self):
        if self._Hole is None:
            self.ComputeHole()
        return self._Hole


    @property
    def CoreShift(self):
        if self._CoreShift is None:
            self.ComputeCoreShift()
        return self._CoreShift


    def AddRing(self, *Rings):
        for Ring in Rings:
            self._Rings.append(Ring)


    def OptimizeGeometry(self):
        self.InitializeConnections()

        res = minimize_scalar(self.ComputeCost, bounds=(0, 1000) , method='bounded', options={'xatol': self.Tolerance})

        return self.BuildCoupler(VirtualShift=res.x)


    def ComputeHole(self):
        self._Hole = Buffer( Union( *self.Fibers ).convex_hull - Union( *self.Fibers, self.Added ) )


    def ComputeFibers(self):
        self._Fibers = []
        
        n = 0

        for Ring in self._Rings:
            for Fiber in Ring.Fibers:
                self._Fibers.append(Fiber)
                n += 1


    def BuildCoupler(self, VirtualShift):
        Coupler = Union(*self.Fibers, self.Added)

        if isinstance(Coupler, GeometryCollection):
            Coupler = BufferMultiPolygon( [P for P in Coupler.geoms if not isinstance(P, TypeUnion[BufferPoint, Point, LineString] )] )

        return Coupler
  

    def InitializeConnections(self):
        self.Connections = []

        for fibers in self.IterateOverConnectedFibers():
            connection = Connection( *fibers)
            self.Connections.append( connection )



    def ShiftConnections(self, Shift):
        for connection in self.Connections:
            connection.SetShift(Shift=Shift, Topology=self.Topology)

        self.Initialize()


    def ComputeCost(self, VirtualShift):
        self.ShiftConnections(Shift=VirtualShift)

        Added = self.Added.Area
        Removed = self.Removed.Area
        Cost = abs(Added - Removed)

        logging.info(f' {VirtualShift = :.2f} \t -> {Added = :.2f} \t {Removed = :.2f} \t{Cost = :.2f}')
        
        return Cost


    def IterateOverConnectedFibers(self):
        for Fiber0, Fiber1 in combinations(self.Fibers, 2):
            if Fiber0.intersection(Fiber1).is_empty: 
                continue
            else:
                yield Fiber0, Fiber1


    def CleanGeometry(self, Object):
        if isinstance(Object, BufferPolygon ):
            return Object

        else:
            MaxArea = numpy.max( [P.area for P in Object.geoms] )

            return BufferMultiPolygon( [P for P in Object.geoms if P.area == MaxArea] )



    def Rasterize(self, Coordinate: numpy.ndarray, Shape: list):

        if isinstance(self.Object, BufferPolygon):
            Exterior = Path(list( self.Object.exterior.coords))

            Exterior = Exterior.contains_points(Coordinate).reshape(Shape)

            Exterior = Exterior.astype(float)

        if isinstance(self.Object, BufferMultiPolygon):
            raster = []
            for polygone in self.Object.geoms:
                Exterior = Path(list( polygone.exterior.coords))

                Exterior = Exterior.contains_points(Coordinate).reshape(Shape)

                raster.append(Exterior.astype(float))

                Exterior = numpy.sum(raster, axis=0)

        if self.Hole is not None:
            Interior = Path(list( self.Hole.exterior.coords))
            Interior = numpy.logical_not( Interior.contains_points(Coordinate).reshape(Shape) )
            Exterior = numpy.logical_and( Exterior, Interior )

        self.Raster = Exterior


    def Plot(self, **kwargs):
        Fig = Scene('SuPyMode Figure', UnitSize=(6,6))
        Colorbar = ColorBar(Discreet=True, Position='right')

        ax = Axis(Row              = 0,
                  Col              = 0,
                  xLabel           = r'x',
                  yLabel           = r'y',
                  Title            = f'{self.Topology = }',
                  Legend           = False,
                  Grid             = False,
                  Equal            = True,
                  Colorbar         = Colorbar,
                  xScale           = 'linear',
                  yScale           = 'linear')

        if 'Base' in kwargs:
            self.Object._Plot(ax)

        for connection in self.Connections:
            connection._Plot(ax, **kwargs)

        Fig.AddAxes(ax)

        Fig.Show()





class Circle(BaseFused):
    def __init__(self, Position: list, Radius: float, Index: float=None, debug='INFO', Gradient=None):

        self.Points   = Position
        self.FiberRadius   = Radius
        self.Index    = Index
        self.Raster   = None
        self.Object   = BufferPolygon( BufferPoint(Position).Buffer(self.FiberRadius) )
        self.C        = [BufferPoint(Position)]
        Name          = ''
        self.Initialize()
        self._Hole = None


    def Rasterize(self, Coordinate: numpy.ndarray, Shape: list):

        Exterior = Path(list( self.Object.exterior.coords))

        Exterior = Exterior.contains_points(Coordinate).reshape(Shape)

        Exterior = Exterior.astype(float)

        self.Raster = Exterior


class BackGround(BaseFused):
    def __init__(self, Radius: float=1000, Index: float=1., debug: str='INFO'):
        self.Position = [0,0]
        self.FiberRadius   = Radius
        self.Index    = Index
        self.Raster   = None
        self.Object   = BufferPolygon( BufferPoint(self.Position).Buffer(self.FiberRadius) )
        self.C        = [BufferPoint(self.Position)]
        Name          = ''
        self.Initialize()
        self._Hole = None


    def Rasterize(self, Coordinate: numpy.ndarray, Shape: list):

        Exterior = Path(list( self.Object.exterior.coords))

        Exterior = Exterior.contains_points(Coordinate).reshape(Shape)

        Exterior = Exterior.astype(float)

        self.Raster = Exterior



















#  - 

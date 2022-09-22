import numpy, logging
from dataclasses import dataclass

from matplotlib.path import Path
from itertools import combinations
from scipy.optimize import minimize_scalar
import shapely.geometry as geo

import FiberFusing.Plotting.Plots as Plots
import FiberFusing.Utils as Utils
from FiberFusing.Connection import Connection
import FiberFusing.Buffer as Buffer






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
    def Cores(self):
        return [f.Core for f in self.Fibers]

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

        OverallLimit = Utils.Union(*Limit)
        
        self._Topology = 'convex' if self.Removed.Area > OverallLimit.area else 'concave'


    def ComputeAdded(self) -> None:
        Added = []
        for connection in self.Connections:
            Added.append(connection.Added)

        self._Added = Utils.Union(*Added) - Utils.Union(*self.Fibers)
        self._Added = Buffer.ToBuffer(self._Added, Color='g').Clean()
        self._Added.Area = self._Added.area



    def ComputeRemoved(self) -> None:
        Removed = []
        for connection in self.Connections:
            Removed.append(connection.Removed)

        self._Removed = Utils.Union(*Removed)
        self._Removed.Area = len(self.Fibers) * self.Fibers[0].area - Utils.Union(*self.Fibers).area
        self._Removed.Color = 'r'


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


    def AddRing(self, *Rings):
        for Ring in Rings:
            self._Rings.append(Ring)


    def OptimizeGeometry(self):
        self.InitializeConnections()

        res = minimize_scalar(self.ComputeCost, bounds=(0, 1000) , method='bounded', options={'xatol': self.Tolerance})

        return self.BuildCoupler(VirtualShift=res.x)


    def ComputeCorePosition(self):

        for connection in self.Connections:
            connection.Fibers_ = self.Fibers
            logging.info('\n\nNew connection\n')
            connection.OptimizeCorePosition()


    def ComputeHole(self):
        self._Hole = Buffer( Utils.Union( *self.Fibers ).convex_hull - Utils.Union( *self.Fibers, self.Added ) )


    def ComputeFibers(self):
        self._Fibers = []
        
        n = 0

        for Ring in self._Rings:
            for Fiber in Ring.Fibers:
                self._Fibers.append(Fiber)
                n += 1


    def BuildCoupler(self, VirtualShift):
        Coupler = Utils.Union(*self.Fibers, self.Added)

        if isinstance(Coupler, geo.GeometryCollection):
            Coupler = Buffer.MultiPolygon( [P for P in Coupler.geoms if not isinstance(P, (geo.Point, geo.LineString) )] )

        self.ComputeCorePosition()

        return Coupler
  

    def InitializeConnections(self):
        self.Connections = []

        for fibers in self.IterateOverConnectedFibers():
            connection = Connection( *fibers)
            self.Connections.append( connection )



    def ShiftConnections(self, Shift):
        for connection in self.Connections:
            connection.Shift = Shift
            connection.Topology = self.Topology

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
        if isinstance(Object, Buffer.Polygon ):
            return Object

        else:
            MaxArea = numpy.max( [P.area for P in Object.geoms] )

            return Buffer.MultiPolygon( [P for P in Object.geoms if P.area == MaxArea] )



    def Rasterize(self, Coordinate: numpy.ndarray, Shape: list):

        if isinstance(self.Object, Buffer.Polygon):
            Exterior = Path(list( self.Object.exterior.coords))

            Exterior = Exterior.contains_points(Coordinate).reshape(Shape)

            Exterior = Exterior.astype(float)

        if isinstance(self.Object, Buffer.MultiPolygon):
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
        Fig = Plots.Scene('SuPyMode Figure', UnitSize=(6,6))

        ax = Plots.Axis(Row      = 0,
                        Col      = 0,
                        xLabel   = r'x',
                        yLabel   = r'y',
                        Title    = f'{self.Topology = }',
                        Grid     = True,
                        Equal    = True)

        Fig.AddAxes(ax).GenerateAxis()

        if 'Base' in kwargs:
            self.Object.__render__(ax)

        if 'Fibers' in kwargs:
            for fiber in self.Fibers:
                fiber.__render__(ax)

        if 'Added' in kwargs:
            self.Added.__render__(ax)

        if 'Removed' in kwargs:
            self.Removed.__render__(ax)

        Fig.Show()





class Circle(BaseFused):
    def __init__(self, Position: list, Radius: float, Index: float=None, debug='INFO', Gradient=None):

        self.Points   = Position
        self.FiberRadius   = Radius
        self.Index    = Index
        self.Raster   = None
        self.Object   = Buffer.Polygon( Buffer.Point(Position).Buffer(self.FiberRadius) )
        self.C        = [Buffer.Point(Position)]
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
        self.Object   = Buffer.Polygon( Buffer.Point(self.Position).Buffer(self.FiberRadius) )
        self.C        = [Buffer.Point(self.Position)]
        Name          = ''
        self.Initialize()
        self._Hole = None


    def Rasterize(self, Coordinate: numpy.ndarray, Shape: list):

        Exterior = Path(list( self.Object.exterior.coords))

        Exterior = Exterior.contains_points(Coordinate).reshape(Shape)

        Exterior = Exterior.astype(float)

        self.Raster = Exterior



















#  - 

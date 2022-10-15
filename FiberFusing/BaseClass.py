import numpy, logging
from dataclasses import dataclass

from collections.abc import Iterable
from shapely import affinity
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from matplotlib.collections  import PatchCollection
from itertools import combinations
from scipy.optimize import minimize_scalar
import shapely.geometry as geo

import MPSPlots.Plots as Plots
import FiberFusing.Utils as Utils
from FiberFusing.Connection import Connection
import FiberFusing.Buffer as Buffer

logging.basicConfig(level=logging.INFO)


ORIGIN = Buffer.Point([0,0])
RESOLUTION = 68

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
        logging.info("Setting up the structure geometry...")
        self.Angle = numpy.asarray(self.Angle)
        self.N = len(self.Angle)
        self.Initialize()
        self._Fibers = None


    def Initialize(self):
        self._Rings = []
        self._CustomFibers = []
        self._Hole = None
        self._Topology = None
        self._Added = None
        self._Removed = None
        self._Centers = None
        self._CoreShift = None


    def __render__(self, Ax):
        path = Path.make_compound_path(
            Path(numpy.asarray(self.Object.exterior.coords)[:, :2]),
            *[Path(numpy.asarray(ring.coords)[:, :2]) for ring in self.Object.interiors])

        patch = PathPatch(path, facecolor='lightblue', alpha=0.4, edgecolor='k')
        collection = PatchCollection([patch], facecolor='lightblue', alpha=0.3, edgecolor='k')
        
        Ax._ax.add_collection(collection, autolim=True)
        Ax._ax.autoscale_view()


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

        OverallLimit = Utils.Union(*Limit) - Utils.Union(*self.Fibers)

        self._Topology = 'convex' if self.Removed.Area > OverallLimit.area else 'concave'


    def MergeConnections(self) -> None:
        NewConnections = []

        for n, connection0 in enumerate(self.Connections):
            for m, connection1 in enumerate(self.Connections):
                if m==n: continue

                union = connection1.Added.union(connection0.Added)

                if not union.is_empty:
                    logging.debug('Connection merging')
                    if connection1[0] == connection0[0]:
                        Set = (connection1[1], connection0[1])
                        new = Connection( *Set, Shift = self.VirtualShift)
                        NewConnections.append(new)
                        continue

                    if connection1[1] == connection0[0]:
                        Set = (connection1[0], connection0[1])
                        new = Connection( *Set, Shift = self.VirtualShift)
                        NewConnections.append(new)
                        continue

                    if connection1[0] == connection0[1]:
                        Set = (connection1[1], connection0[0])
                        new = Connection( *Set, Shift = self.VirtualShift)
                        NewConnections.append(new)
                        continue


                    if connection1[1] == connection0[1]:
                        Set = (connection1[0], connection0[0])
                        new = Connection( *Set, Shift = self.VirtualShift)
                        NewConnections.append(new)
                        continue


    def ComputeAdded(self) -> None:
        Added = []

        for n, connection in enumerate(self.Connections):
            NewAdded = connection.Added

            Added.append(NewAdded)

        self._Added = Utils.Union(*Added) - Utils.Union(*self.Fibers)
        self._Added = Buffer.ToBuffer(self._Added, facecolor='g').Clean()
        self._Added.Area = self._Added.area



    def ComputeRemoved(self) -> None:
        Removed = []
        for connection in self.Connections:
            Removed.append(connection.Removed)

        self._Removed = Utils.Union(*Removed)
        self._Removed.Area = len(self.Fibers) * self.Fibers[0].area - Utils.Union(*self.Fibers).area

        self._Removed.facecolor = 'r'


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


    def AddCustom(self, *Custom):
        for fiber in Custom:
            self._CustomFibers.append(fiber)


    def OptimizeGeometry(self):
        self.InitializeConnections()

        res = minimize_scalar(self.ComputeCost, bounds=(0, 1000) , method='bounded', options={'xatol': self.Tolerance})

        return self.BuildCoupler(VirtualShift=res.x)


    def ComputeCorePosition(self):
        for connection in self.Connections:
            connection.OptimizeCorePosition()


    def ComputeFibers(self):
        self._Fibers = []

        for Ring in self._Rings:
            for fiber in Ring.Fibers:
                self._Fibers.append(fiber)

        for fiber in self._CustomFibers:
            self._Fibers.append(fiber)

        for n, fiber in enumerate(self._Fibers):
            fiber.Name = f' Fiber {n}'


    def BuildCoupler(self, VirtualShift):
        Coupler = Utils.Union(*self.Fibers, self.Added)

        if isinstance(Coupler, geo.GeometryCollection):
            Coupler = Buffer.MultiPolygon( [Buffer.Polygon(P) for P in Coupler.geoms if not isinstance(P, (geo.Point, geo.LineString) )] )

        self.ComputeCorePosition()

        return Coupler
  

    def InitializeConnections(self):
        self.Connections = []

        for fibers in self.IterateOverConnectedFibers():
            connection = Connection( *fibers )
            self.Connections.append( connection )



    def ShiftConnections(self, Shift):
        for connection in self.Connections:
            connection.Shift = Shift
            connection.Topology = self.Topology

        self.Initialize()


    def ComputeCost(self, VirtualShift):
        self.VirtualShift = VirtualShift
        self.ShiftConnections(Shift=VirtualShift)

        Added = self.Added.Area
        Removed = self.Removed.Area
        Cost = abs(Added - Removed)

        logging.debug(f' Fusing optimization: {VirtualShift = :.2f} \t -> \t{Added = :.2f} \t -> {Removed = :.2f} \t -> {Cost = :.2f}')
        
        return Cost


    def IterateOverConnectedFibers(self):
        for Fiber0, Fiber1 in combinations(self.Fibers, 2):
            if Fiber0.intersection(Fiber1).is_empty: 
                continue
            else:
                yield Fiber0, Fiber1



    def Rasterize(self, Coordinate: numpy.ndarray=None, Shape: list=[100,100]):

        if Coordinate is None:
            xMin, yMin, xMax, yMax = self.Object.bounds
            x, y = numpy.mgrid[ xMin:xMax:complex(Shape[0]), yMin:yMax:complex(Shape[1]) ]
            Coordinate = numpy.vstack((x.flatten(), y.flatten())).T


        if isinstance(self.Object, Buffer.Polygon):
            Exterior = self.Object.__raster__(Coordinate).reshape(Shape)
   
        if isinstance(self.Object, Buffer.MultiPolygon):
            raster = []
            for polygone in self.Object.geoms:
                polygone = Buffer.Polygon(polygone)
                Exterior = Path(list( polygone.exterior.coords))

                Exterior = polygone.__raster__(Coordinate)

                raster.append(Exterior.astype(float))

                Exterior = numpy.sum(raster, axis=0)

        self.Raster = Exterior

        return self.Raster



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

        self.Object.__render__(ax)

        if 'Fibers' in kwargs:
            for fiber in self.Fibers:
                fiber.__render__(ax)

        if 'Added' in kwargs:
            self.Added.__render__(ax)

        if 'Removed' in kwargs:
            self.Removed.__render__(ax)

        Fig.Show()


    def Rotate(self, *args, **kwargs):
        self.Object = self.Object.Rotate(*args, **kwargs)






class BackGround(Buffer.Polygon):
    Name: str = 'BackGround'
    Index: float

    def __new__(cls, Radius: float=1000, Index: float=1):
        Instance = Buffer.Polygon.__new__(cls)
        return Instance

    def __init__(self, Radius: float=1000, Index: float=1):
        super().__init__( ORIGIN.buffer(Radius, resolution=RESOLUTION))

    def Rotate(self, *args, **kwargs):
        return self


    def Rasterize(self, Coordinate: numpy.ndarray, Shape: list):

        Exterior = Path(list( self.exterior.coords))

        Exterior = Exterior.contains_points(Coordinate).reshape(Shape)

        Exterior = Exterior.astype(float)

        self.Raster = Exterior







#  - 

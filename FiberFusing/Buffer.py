
import numpy
import shapely.geometry as geo
from shapely import affinity
from collections.abc import Iterable
from matplotlib.patches import PathPatch
from matplotlib.collections  import PatchCollection
from matplotlib.path import Path

import MPSPlots.Plots as Plots
import FiberFusing

RESOLUTION=128
ORIGIN = geo.Point([0,0])



def Normalize(Array):
    Array = numpy.asarray(Array)
    Norm = numpy.sqrt( numpy.sum(Array**2) )
    return Array/Norm


class BaseBuffer():
    Name: str = None
    facecolor: str = 'lightblue'
    alpha: float = 0.3
    Area = None

    Index: float=1
    marker: str = None

    Raster = None
    kwargs = {}


    def __init__(self, Object=None, Name=None, **kwargs):
        self.kwargs = kwargs

        for key, value in kwargs.items():
            setattr(self, key, value)

        if Object is None:
            super().__init__()
        else:
            super().__init__(Object)


    @property
    def convex_hull(self):
        return super().convex_hull


    def GetMaxDistance(self):
        x, y = self.exterior.xy
        x = numpy.asarray(x)
        y = numpy.asarray(y)
        return numpy.sqrt(x**2 + y**2).max()


    def Clean(self):
        return self

    def Scale(self, Factor: float, Origin: geo.Point=ORIGIN):
        o = affinity.scale( self, xfact=Factor, yfact=Factor, origin=Origin )
        return ToBuffer( Object=o, **self.kwargs )


    def Rotate(self, Angle, Origin=ORIGIN):
        if isinstance(Angle, Iterable):
            return [ self.Rotate(Angle=angle, Origin=Origin) for angle in Angle ] 
        else:
            return self.__class__( Object=affinity.rotate(self, Angle, origin=Origin), **self.kwargs ) 

    @property
    def Hole(self):
        return Polygon( self.exterior.coords ) - self


    def __render__(self, Ax):
        if self.is_empty: return

        path = Path.make_compound_path(
            Path(numpy.asarray(self.exterior.coords)[:, :2]),
            *[Path(numpy.asarray(ring.coords)[:, :2]) for ring in self.interiors])

        patch = PathPatch(path, facecolor=self.facecolor, alpha=self.alpha, edgecolor='k')
        collection = PatchCollection([patch], facecolor=self.facecolor, alpha=self.alpha, edgecolor='k')
        
        Ax._ax.add_collection(collection, autolim=True)
        Ax._ax.autoscale_view()
        if self.Name is not None:
            Ax._ax.text(self.centroid.x, self.centroid.y, self.Name)


class Polygon(BaseBuffer, geo.Polygon):  
    def __sub__(self, Other):
        return ToBuffer(super().__sub__(Other))


    def __add__(self, Other):
        return ToBuffer(super().__add__(Other))


    def __raster__(self, Coordinate):
        Exterior = Path(list( self.exterior.coords))

        Exterior = Exterior.contains_points(Coordinate)

        hole = self.Hole.contains_points(Coordinate)

        return Exterior.astype(int) - hole.astype(int)


    def contains_points(self, Coordinate):
        if self.is_empty:
            return  numpy.zeros(Coordinate.shape[0])
        else:
            Exterior = Path( list( self.exterior.coords) )
            return Exterior.contains_points(Coordinate).astype(bool)


class Point(BaseBuffer, geo.Point):
    alpha = 1
    facecolor = 'none'
    edgecolor = 'k'

    @property
    def Kwargs(self):
        return {'facecolor': self.facecolor, 'edgecolor': self.edgecolor, 'alpha': self.alpha, 'marker': self.marker}

    def __repr__(self):
        return f"Point: ({self.x:.2f}, {self.y:.2f})"

    def __neg__(self):
        return Point( [-self.x, -self.y], **self.Kwargs )


    def __sub__(self, Other):
        if isinstance(Other, geo.Point):
            return Point( [self.x-Other.x, self.y-Other.y], **self.Kwargs )

        if isinstance( Other, (list, numpy.ndarray) ):
            return Point( [self.x-Other[0], self.y-Other[1]], **self.Kwargs )

    def __add__(self, Other):
        if isinstance(Other, geo.Point):
            return Point( [self.x+Other.x, self.y+Other.y], **self.Kwargs )

        if isinstance( Other, (list, numpy.ndarray) ):
            return Point( [self.x+Other[0], self.y+Other[1]], **self.Kwargs )

    def __mul__(self, Factor: float):
        return Point( [self.x*Factor, self.y*Factor], **self.Kwargs )

    def __rmul__(self, Factor: float):
        return Point( [self.x*Factor, self.y*Factor], **self.Kwargs )

    def __truediv__(self, Factor: float):
        return Point( [self.x/Factor, self.y/Factor], **self.Kwargs )


    def Distance(self, Other=None):
        if Other is None:
            return numpy.sqrt( self.x**2 + self.y**2 ) 
        else:
            return numpy.sqrt( ( self.x - Other.x )**2 + ( self.y - Other.y )**2 ) 


    def Shift(self, Vector: list):
        x = self.x + Vector[0]
        y = self.y + Vector[1]
        return Point([x, y], **self.kwargs)


    def Buffer(self, Radius):
        return Circle(Radius=Radius, Center=self)


    def __render__(self, Ax):
        Ax._ax.text(self.x, self.y, self.Name)
        Ax._ax.scatter(self.x, self.y, s=60, **self.Kwargs )



class MultiPolygon(BaseBuffer, geo.MultiPolygon):
    def __render__(self, Ax):
        for polygone in self.geoms:
            Plots.PlotPolygon(Ax._ax, self, facecolor=self.facecolor, alpha=self.alpha, edgecolor='k')


    def contains_points(self, Coordinate):
        Init = numpy.zeros(Coordinate.shape[0])

        for polygon in self.geoms:
            Exterior = Path( list( polygon.exterior.coords) )
            Init += Exterior.contains_points(Coordinate)

        return Init.astype(bool)


class GeometryCollection(BaseBuffer, geo.GeometryCollection):
    def Clean(self):
        NewClean = [e for e in self.geoms if not isinstance(e, (geo.LineString, geo.Point) ) ]
        return GeometryCollection(NewClean)

    def __render__(self, Ax):
        for polygone in self:
            Plots.PlotPolygon(Ax._ax, self, facecolor=self.facecolor, alpha=self.alpha, edgecolor='k')


class Line(BaseBuffer, geo.LineString):
    linewidth: float = 2
    facecolor: str = 'k'

    @property
    def boundary(self):
        return ( Point( e ) for e in super().boundary.geoms )


    @property
    def MidPoint(self):
        P0, P1 = self.boundary
        return Point( [ (P0.x+P1.x)/2, (P0.y+P1.y)/2 ], **self.kwargs )


    def GetPosition(self, x):
        P0, P1 = self.boundary
        return P0 - (P0-P1)*x

    def GetBissectrice(self):
        return Line( affinity.rotate(self, 90, origin=self.MidPoint), **self.kwargs )


    def MakeLength(self, Length: float):
        P0, P1 = self.boundary
        Distance = numpy.sqrt( (P0.x-P1.x)**2 + (P0.y-P1.y)**2 )
        Factor = Length/Distance
        return self.Extend(factor=Factor)


    def Shift(self, Vector: list):
        P0, P1 = self.boundary

        P2 = Point(P0).Shift(Vector=Vector)
        P3 = Point(P1).Shift(Vector=Vector)

        return Line([P2, P3], **self.kwargs)


    def Centering(self, Center):
        P0, P1 = self.boundary

        MidPoint = self.MidPoint
        xShift = Center.x - MidPoint.x
        yShift = Center.y - MidPoint.y
        Vector = [xShift, yShift]

        P2 = Point(P0).Shift(Vector=Vector)
        P3 = Point(P1).Shift(Vector=Vector)

        return Line([P2, P3])


    @property
    def Perpendicular(self):
        return Line(  self.Rotate(90, Origin=self.MidPoint) )



    def Extend(self, factor: float=1):
         return Line( affinity.scale(self, xfact=factor, yfact=factor, origin=self.MidPoint), **self.kwargs )


    def Rotate(self, Angle, Origin=None):
        if Origin is None:
            Origin = self.MidPoint
        return Line( affinity.rotate(self, Angle, origin=Origin ), **self.kwargs )


    @property
    def Vector(self):
        P0, P1 = self.boundary

        dy = P0.y-P1.y
        dx = P0.x-P1.x
        if dx == 0:
            return numpy.asarray([0, 1])
        else:
            return Normalize([1, dy/dx])

    def __render__(self, Ax):
        Ax._ax.plot(*self.xy, color='k', alpha=self.alpha)
        if self.Name is not None:
            Ax._ax.text(self.centroid.x, self.centroid.y, self.Name)




class Circle(Polygon):
    Radius: float=None
    Center: Point=None

    def __new__(cls, Radius: float, Center: Point, Name: str = ''):
        Instance = Polygon.__new__(cls)
        return Instance

    def __init__(self, Radius: float, Center: Point, Name: str = ''):
        self.Radius = Radius
        self.Name = Name
        self.Center = Point(Center)

        super(Circle, self).__init__(self.Center.buffer(Radius, resolution=RESOLUTION))


    def __str__(self):
        return f" Center: {self.Center} \t Radius: {self.Radius}"


    @property
    def Area(self):
        return numpy.pi * self.Radius**2


    def Plot(self, Figure=None, Ax=None, Return=False, Show=True):
        if Ax is None:
            Figure = Plots.Scene('FiberFusing figure', UnitSize=(6,6))
            Ax = Plots.Axis(Row=0, Col=0, xLabel='x', yLabel='y', Colorbar=False, Equal=True)
            Figure.AddAxes(Ax)
            Figure.GenerateAxis()

        
 
        self.__render__(Ax)

        if Return: 
            return Figure, Ax

        if Show:
            Figure.Show()


    def GetConscriptedFiber(self, Other=None, Type='Interior', Rotate: bool=False):

        if Other is None:
            return FiberFusing.Fiber.Fiber(Radius=self.Radius, Center=self.Center+[0, 2*self.Radius])

        else:
            CenterLine = Line( [self.Center, Other.Center] ) 

            Shift = numpy.sqrt( (self.Radius + Other.Radius)**2 - (CenterLine.length/2)**2)

            Point = CenterLine.MidPoint.Shift( CenterLine.Perpendicular.Vector * Shift)

            if Type in ['Exterior', 'concave']:
                Radius = numpy.sqrt( Shift**2 +  (CenterLine.length/2)**2 ) - self.Radius

            if Type in ['Interior', 'convex']:
                Radius = numpy.sqrt( Shift**2 + (CenterLine.length/2)**2 ) + self.Radius

            if Rotate:
                return FiberFusing.Fiber.Fiber(Radius=self.Radius, Center=Point, **self.kwargs).Rotate(Angle=180, Origin=CenterLine.MidPoint)

            else:
                return FiberFusing.Fiber.Fiber(Radius=self.Radius, Center=Point, **self.kwargs)



    def __render__(self, Ax):
        super().__render__(Ax)

        self.Center.__render__(Ax)


    def Rotate(self, Angle: float, Origin: Point=None):
        Origin = self.centroid if Origin is None else Origin
        return self.__class__(Radius=self.Radius, Center=self.Center.Rotate(Angle, Origin=Origin), Name=self.Name)


    def ScaleCenter(self, Factor: float):
        NewCenter = self.Center.Scale(Factor=Factor, Origin=ORIGIN)
        return self.__class__(Radius=self.Radius, Center=NewCenter)



class ToBuffer():
    def __new__(self, Object, **kwargs):
        if isinstance(Object, list):
            return Point(Object, **kwargs)
        
        if isinstance(Object, geo.Polygon):
            return Polygon(Object, **kwargs)
        
        if isinstance(Object, geo.MultiPolygon):
            return MultiPolygon(Object, **kwargs)

        if isinstance(Object, geo.GeometryCollection):
            return GeometryCollection(Object, **kwargs)

        if isinstance(Object, geo.LineString):
            return Line(Object, **kwargs)

        if isinstance(Object, geo.Point):
            return Point(Object, **kwargs)















# - 

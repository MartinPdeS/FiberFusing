
import numpy
import shapely.geometry as geo
from shapely import affinity

import FiberFusing.Plotting.Plots as Plots

def Normalize(Array):
    Array = numpy.asarray(Array)
    Norm = numpy.sqrt( numpy.sum(Array**2) )
    return Array/Norm


class BaseBuffer():
    Center = None
    Area = None
    Core = None
    Index = None
    CoreShift = numpy.array([0.,0.])
    Raster = None
    kwargs = {}


    def __init__(self, Object=None, *args, **kwargs):
        self.kwargs = kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

        if Object is None:
            super().__init__()
        else:
            super().__init__(Object)


    @property
    def convex_hull(self):
        return ToBuffer(self.convex_hull)


    def GetMaxDistance(self):
        x, y = self.exterior.xy
        x = numpy.asarray(x)
        y = numpy.asarray(y)
        return numpy.sqrt(x**2 + y**2).max()


    def Clean(self):
        return self


class Polygon(BaseBuffer, geo.Polygon):  
    Name: str = None
    facecolor: str = 'lightblue'
    alpha: float = 0.3
    Radius: float = None


    @property
    def PlotKwargs(self):
        return {'alpha': self.alpha, 
                'facecolor': self.facecolor}


    def __self__(self, Object):
        if isinstance(Object, list) and all([isinstance(e, geo.Point) for e in Object]):
            super().__init__( [(p.x, p.y) for p in Object ] )

        if isinstance(Object, geo.Polygon):
            super().__init__(Object)


    def __sub__(self, Other):
        return ToBuffer(super().__sub__(Other))


    def __add__(self, Other):
        return ToBuffer(super().__add__(Other))


    @property
    def convex_hull(self):
        return ToBuffer(super().convex_hull)
        

    def Rotate(self, Angle, Origin=[0,0]):
        return Polygon( affinity.rotate(self, Angle, origin=Origin ), **self.kwargs )
        

    def Scale(self, Factor: float, Origin: list = [0,0]):
        return Polygon( affinity.scale( self, xfact=Factor, yfact=Factor, origin=Point(Origin) ), **self.kwargs )


    def __render__(self, Ax):
        Plots.PlotPolygon(Ax._ax, self, **self.PlotKwargs, edgecolor='k')


class Point(BaseBuffer, geo.Point):
    Name: str = ''
    marker: str = 'o'
    size: float = 60
    alpha = 1
    facecolors = 'none'
    color = 'k'

    def __repr__(self):
        return f"Point: ({self.x:.2f}, {self.y:.2f})"

    def __neg__(self):
        return Point( [-self.x, -self.y] )


    def __sub__(self, Other):
        if isinstance(Other, geo.Point):
            return Point( [self.x-Other.x, self.y-Other.y] )

        if isinstance( Other, (list, numpy.ndarray) ):
            return Point( [self.x-Other[0], self.y-Other[1]] )

    def __add__(self, Other):
        if isinstance(Other, geo.Point):
            return Point( [self.x+Other.x, self.y+Other.y] )

        if isinstance( Other, (list, numpy.ndarray) ):
            return Point( [self.x+Other[0], self.y+Other[1]] )


    def __mul__(self, Factor):
        return Point( [self.x*Factor, self.y*Factor] )

    @property
    def PlotKwargs(self):
        return {'marker': self.marker,
                's': self.size,
                'alpha': self.alpha,
                'facecolors': self.facecolors,
                'color': self.color}


    def ToNumpy(self):
        return numpy.array( [ self.x, self.y ] )


    def Distance(self, Other=None):
        if Other is None:
            return numpy.sqrt( self.x**2 + self.y**2 ) 
        else:
            return numpy.sqrt( ( self.x - Other.x )**2 + ( self.y - Other.y )**2 ) 


    def Shift(self, Vector: list):
        x = self.x + Vector[0]
        y = self.y + Vector[1]
        return Point([x, y], **self.kwargs)


    def Rotate(self, Angle, Origin=[0,0]):
        return Point( affinity.rotate(self, Angle, origin=Origin), **self.kwargs )

    def Buffer(self, Radius):
        Circle = Polygon( self.buffer(Radius, resolution=256), **self.kwargs )
        Circle.Radius = Radius
        Circle.Center = self
        return Circle


    def __render__(self, Ax):
        Ax._ax.text(self.x, self.y, self.Name)
        Ax._ax.scatter(self.x, self.y, **self.PlotKwargs)



class MultiPolygon(BaseBuffer, geo.MultiPolygon):
    Name = None
    Color = 'lightblue'
    Alpha = 0.3


    def Rotate(self, Angle, Origin=[0,0]):
        return MultiPolygon( affinity.rotate(self, Angle, origin=Origin ) )


    def Scale(self, Factor: float, Origin: list = [0,0]):
        return MultiPolygon( affinity.scale(self, xfact=Factor, yfact=Factor, origin=Point(Origin) ), **self.kwargs )
        

    def __render__(self, Ax):
        for polygone in self.geoms:
            Plots.PlotPolygon(Ax._ax, polygone, facecolor=self.Color, edgecolor='k', alpha=self.Alpha)



class GeometryCollection(BaseBuffer, geo.GeometryCollection):
    Name = None
    Color = 'lightblue'
    Alpha = 0.3

    @property
    def PlotKwargs(self):
        return {'alpha': self.Alpha,
                'color': self.Color}


    def Rotate(self, Angle, Origin=[0,0]):
        return BufferGeometryCollection( affinity.rotate(self, Angle, origin=Origin ) )

    def __render__(self, Ax):
        for polygone in self.geoms:
            ToBuffer(polygone, **self.kwargs).__render__(Ax)


    def Clean(self):
        NewClean = [e for e in self.geoms if not isinstance(e, (geo.LineString, geo.Point) ) ]
        return GeometryCollection(NewClean)



    def __render__(self, Ax):
        for polygone in self:
            Plots.PlotPolygon(Ax._ax, polygone, **self.PlotKwargs, edgecolor='k')


class Line(BaseBuffer, geo.LineString):
    linewidth = 2
    color = 'b'
    alpha = 0.3


    @property
    def PlotKwargs(self):
        return {'linewidth': self.linewidth, 
                'color': self.color,
                'alpha': self.alpha}


    @property
    def boundary(self):
        return ( Point( e ) for e in super().boundary.geoms )


    @property
    def MidPoint(self):
        P0, P1 = self.boundary
        return Point( [ (P0.x+P1.x)/2, (P0.y+P1.y)/2 ], **self.kwargs )


    def GetPosition(self, x):
        P0, P1 = self.boundary
        return P0 - x * (P0-P1)

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
        Ax._ax.plot(*self.xy, **self.PlotKwargs)


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

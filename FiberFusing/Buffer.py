
import numpy

from shapely.geometry import Point, MultiPolygon, Polygon, GeometryCollection, box, LineString
from shapely import affinity

import FiberFusing.Plotting.Plots as Plots

def Normalize(Array):
    Array = numpy.asarray(Array)
    Norm = numpy.sqrt( numpy.sum(Array**2) )
    return Array/Norm

class ExtraParameters():
    Center = None
    Area = None
    Alpha = 0.3
    Index = None
    Hole = None
    Color = None
    Radius = None
    Gradient = None
    CoreShift = numpy.array([0.,0.])
    Raster = None
    CorePosition = None
    Name = ''
    Name = ''


    @property
    def convex_hull(self):
        return Buffer(self.convex_hull)

    def GetMaxDistance(self):
        x, y = self.exterior.xy
        x = numpy.asarray(x)
        y = numpy.asarray(y)
        return numpy.sqrt(x**2 + y**2).max()


    def __plot__(self, ax):
        artist = Plots.AddShapely(Object=self, Alpha=0.1)
        ax.AddArtist(artist)

    def Plot(self):
        Fig = Plots.Scene('SuPyMode Figure', UnitSize=(6,6))
        Colorbar = Plots.ColorBar(Discreet=True, Position='right')

        ax = Plots.Axis(Row              = 0,
                  Col              = 0,
                  xLabel           = r'x',
                  yLabel           = r'y',
                  Title            = f'',
                  Legend           = False,
                  Grid             = False,
                  Equal            = True,
                  Colorbar         = Colorbar,
                  xScale           = 'linear',
                  yScale           = 'linear')

        self.__plot__(ax)

        Fig.AddAxes(ax)

        Fig.Show()


class BufferPolygon(Polygon, ExtraParameters):  
    def __init__(self, Object=None, *args, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

        if Object is None:
            super().__init__()
        else:
            super().__init__(Object)



    def __self__(self, Object):
        if isinstance(Object, list) and all([isinstance(e, Point) for e in Object]):
            super().__init__( [(p.x, p.y) for p in Object ] )

        if isinstance(Object, Polygon):
            super().__init__(Object)


    def __sub__(self, Other):
        return Buffer(super().__sub__(Other))

    def __add__(self, Other):
        return Buffer(super().__add__(Other))


    @property
    def convex_hull(self):
        return Buffer(super().convex_hull)
        

    def Rotate(self, Angle, Origin=[0,0]):
        return BufferPolygon( affinity.rotate(self, Angle, origin=Origin ) )
        

    def Scale(self, Factor: float, Origin: list = [0,0]):
        return BufferPolygon( affinity.scale( self, xfact=Factor, yfact=Factor, origin=Point(Origin) ) )



class BufferPoint(Point, ExtraParameters):    
    def __init__(self, Object=None, *args, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

        if Object is None:
            super().__init__()
        else:
            super().__init__(Object)

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
        return BufferPoint([x, y])

    def Rotate(self, Angle, Origin=[0,0]):
        return BufferPoint( affinity.rotate(self, Angle, origin=Origin ) )

    def Buffer(self, Radius):
        Circle = BufferPolygon( self.buffer(Radius, resolution=256) )
        Circle.Radius = Radius
        Circle.Center = self
        return Circle




class BufferMultiPolygon(MultiPolygon, ExtraParameters):
    def __init__(self, Object=None, *args, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

        if Object is None:
            super().__init__()
        else:
            super().__init__(Object)


    def Rotate(self, Angle, Origin=[0,0]):
        return BufferMultiPolygon( affinity.rotate(self, Angle, origin=Origin ) )

    def Scale(self, Factor: float, Origin: list = [0,0]):
        return BufferMultiPolygon( affinity.scale( self, xfact=Factor, yfact=Factor, origin=Point(Origin) ) )
        

class BufferGeometryCollection(GeometryCollection, ExtraParameters):
    def __init__(self, Object=None, *args, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

        if Object is None:
            super().__init__()
        else:
            super().__init__(Object)

    def Rotate(self, Angle, Origin=[0,0]):
        return BufferGeometryCollection( affinity.rotate(self, Angle, origin=Origin ) )


class BufferLine(LineString, ExtraParameters):
    def __init__(self, Object):
        super().__init__(Object)

    @property
    def MidPoint(self):
        P0, P1 = self.boundary.geoms

        return BufferPoint( [ (P0.x+P1.x)/2, (P0.y+P1.y)/2 ] )


    def GetBissectrice(self):
        return BufferLine( affinity.rotate(self, 90, origin=self.MidPoint) )


    def MakeLength(self, Length: float):
        P0, P1 = self.boundary.geoms
        Distance = numpy.sqrt( (P0.x-P1.x)**2 + (P0.y-P1.y)**2 )
        Factor = Length/Distance
        return self.Extend(factor=Factor)

    def Shift(self, Vector: list):
        P0, P1 = self.boundary.geoms

        P2 = BufferPoint(P0).Shift(Vector=Vector)
        P3 = BufferPoint(P1).Shift(Vector=Vector)

        return BufferLine([P2, P3])


    def Centering(self, Center):
        P0, P1 = self.boundary.geoms

        MidPoint = self.MidPoint
        xShift = Center.x - MidPoint.x
        yShift = Center.y - MidPoint.y
        Vector = [xShift, yShift]

        P2 = BufferPoint(P0).Shift(Vector=Vector)
        P3 = BufferPoint(P1).Shift(Vector=Vector)

        return BufferLine([P2, P3])


    def Extend(self, factor: float=1):
         return BufferLine( affinity.scale(self, xfact=factor, yfact=factor, origin=self.MidPoint) )

    def Rotate(self, Angle, Origin=None):
        if Origin is None:
            Origin = self.MidPoint
        return BufferLine( affinity.rotate(self, Angle, origin=Origin ) )


    @property
    def Vector(self):
        P0, P1 = self.boundary.geoms

        dy = P0.y-P1.y
        dx = P0.x-P1.x
        if dx == 0:
            return numpy.asarray([0, 1])
        else:
            return Normalize([1, dy/dx])



class Buffer():
    def __new__(self, Object, **kwargs):
        if isinstance(Object, list):
            return BufferPoint(Object, **kwargs)
        
        if isinstance(Object, Polygon):
            return BufferPolygon(Object, **kwargs)
        
        if isinstance(Object, MultiPolygon):
            return BufferMultiPolygon(Object, **kwargs)

        if isinstance(Object, GeometryCollection):
            return BufferGeometryCollection(Object, **kwargs)

        if isinstance(Object, LineString):
            return BufferLine(Object, **kwargs)

        if isinstance(Object, Point):
            return BufferPoint(Object, **kwargs)

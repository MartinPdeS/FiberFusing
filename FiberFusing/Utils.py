
import numpy, logging
from typing import Union as UnionType

from shapely.geometry import Point, Polygon
from shapely import affinity

from shapely.ops import nearest_points, unary_union

from FiberFusing.Buffer import Buffer, BufferPoint, BufferPolygon, BufferMultiPolygon, BufferLine
import FiberFusing.Plotting.Plots as Plots

logging.basicConfig(level=logging.INFO)


def ToList(Object):
    Object = numpy.array(Object)
    if numpy.atleast_1d(Object) is Object:
        return Object

    else:
        return numpy.expand_dims(Object, axis=0)


def NearestPoints(Object0, Object1):
    if isinstance(Object0, UnionType[Polygon, BufferPolygon] ):
        P = nearest_points(Object0.exterior, Object1.exterior)
        return BufferPoint(P[0])
        # return [ BufferPoint(p) for p in P ]


def GetBoundaries(Objects):
    Objects = ToList(Objects)
    return unary_union(Objects).bounds


def Union(*Objects):
    Output = BufferPolygon()
    for geo in Objects:
        Output = Output.union(geo)

    return Buffer(Output)


def Intersection(*Objects):
    Output = Objects[0]
    for geo in Objects[1:]:
        Output = Output.intersection(geo)

    return Buffer(Output)




def Rotate(Object=None, Angle=0, Origin=(0,0)):
    Angle = ToList(Angle)
    rotated = tuple( Buffer(affinity.rotate(Object, angle, origin=Origin ) ) for angle in Angle )

    return rotated




class _Fiber(BufferPolygon):
    def __new__(cls, Radius: float, Center: list, Name: str = ''):
        Instance = Polygon.__new__(cls)
        return Instance

    def __init__(self, Radius: float, Center: list, Name: str = ''):
        self.Radius = Radius
        self.Name = Name
        self.Center = BufferPoint(Center)
        self.Core = Center
        circle = Point(Center).buffer(Radius, resolution=256)
        super(_Fiber, self).__init__(circle)


    def UpdateCorePosition(self):
        print(self.CorePosition)
        self.CorePosition += self.CoreShift


    def MaxDistance(self, Origin=Point([0,0])):
        x, y = self.exterior.xy
        x = numpy.asarray(x)
        y = numpy.asarray(y)

        x0 = Origin.x
        y0 = Origin.y

        return numpy.sqrt((x-x0)**2 + (y-y0)**2).max()


    def GetRemoved(self, Other):
        Removed = BufferPolygon(self.intersection(Other))
        Removed.Area = Other.area + self.area - Union(self, Other).area
        Removed.Color = 'k'
        return Removed


    def GetRadialLine(self):
        C0 = BufferPoint([0,0])
        return BufferLine([C0, self.Center])


    def GetRadialMask(self):
        Radial = self.GetRadialLine()
        P0  = BufferPoint([0,0]).Rotate(Angle=90, Origin=Radial.boundary[1])
        P1  = BufferPoint([0,0]).Rotate(Angle=-90, Origin=Radial.boundary[1])
        P2  = self.Center.Rotate(Angle=-90, Origin=P0)
        P3  = self.Center.Rotate(Angle=90, Origin=P1)

        Mask = BufferPolygon([P0, P1, P3, P2], Color='k')

        return Mask


    @property
    def Area(self):
        return numpy.pi * self.Radius**2

        








#



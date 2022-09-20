
import numpy, logging
import matplotlib.pyplot as plt
from typing import Union as UnionType

from shapely.geometry import Point, Polygon
from shapely import affinity

from shapely.ops import nearest_points, unary_union

import FiberFusing.Buffer as Buffer 
import FiberFusing.Plotting.Plots as Plots

logging.basicConfig(level=logging.INFO)


def ToList(Object):
    Object = numpy.array(Object)
    if numpy.atleast_1d(Object) is Object:
        return Object

    else:
        return numpy.expand_dims(Object, axis=0)


def NearestPoints(Object0, Object1):
    if isinstance(Object0, UnionType[Polygon, Buffer.Polygon] ):
        P = nearest_points(Object0.exterior, Object1.exterior)
        return Buffer.Point(P[0])



def GetBoundaries(Objects):
    Objects = ToList(Objects)
    return unary_union(Objects).bounds


def Union(*Objects):
    Output = Buffer.Polygon()
    for geo in Objects:
        Output = Output.union(geo)

    return Buffer.ToBuffer(Output)


def Intersection(*Objects):
    Output = Objects[0]
    for geo in Objects[1:]:
        Output = Output.intersection(geo)

    return Buffer.ToBuffer(Output)




def Rotate(Object=None, Angle=0, Origin=(0,0)):
    Angle = ToList(Angle)
    rotated = tuple( Buffer.ToBuffer(affinity.rotate(Object, angle, origin=Origin ) ) for angle in Angle )

    return rotated




class _Fiber(Buffer.Polygon):
    def __new__(cls, Radius: float, Center: list, Name: str = ''):
        Instance = Polygon.__new__(cls)
        return Instance

    def __init__(self, Radius: float, Center: list, Name: str = ''):
        self.Radius = Radius
        self.Name = Name
        self.Center = Buffer.Point(Center, marker='o', Name='')
        self.Core = Buffer.Point(Center, marker='o', Name='')
        self.CorePosition = numpy.array( [self.Center.x, self.Center.y] )
        circle = Point(Center).buffer(Radius, resolution=256)
        super(_Fiber, self).__init__(circle)


    def UpdateCorePosition(self):
        self.CorePosition += self.CoreShift
        self.Core = Buffer.Point(self.CorePosition, Name='')


    def ShiftCore(self, Shift: numpy.ndarray):
        self.CorePosition += Shift
        self.Core.Shift(Shift)


    def MaxDistance(self, Origin=Point([0,0])):
        x, y = self.exterior.xy
        x = numpy.asarray(x)
        y = numpy.asarray(y)

        x0 = Origin.x
        y0 = Origin.y

        return numpy.sqrt((x-x0)**2 + (y-y0)**2).max()


    def GetRemoved(self, Other):
        Removed = Buffer.Polygon(self.intersection(Other))
        Removed.Area = Other.area + self.area - Union(self, Other).area
        Removed.Color = 'k'
        return Removed


    def GetRadialLine(self):
        C0 = Buffer.Point([0,0])
        return Buffer.Line([C0, self.Center])


    def GetRadialMask(self):
        Radial = self.GetRadialLine()
        P0  = Buffer.Point([0,0]).Rotate(Angle=90, Origin=Radial.boundary[1])
        P1  = Buffer.Point([0,0]).Rotate(Angle=-90, Origin=Radial.boundary[1])
        P2  = self.Center.Rotate(Angle=-90, Origin=P0)
        P3  = self.Center.Rotate(Angle=90, Origin=P1)

        Mask = Buffer.Polygon([P0, P1, P3, P2], Color='k')

        return Mask


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



    def __render__(self, Ax):
        super().__render__(Ax)

        self.Core.__render__(Ax)
        self.Center.__render__(Ax)

        # if self.Center != self.Core:
        #     self.Center.__render__(Ax)








#



import numpy

from dataclasses import dataclass

from FiberFusing.Utils import Rotate, _Fiber
import FiberFusing.Buffer as Buffer

class FiberRing():
    def __init__(self, Angles, Fusion, FiberRadius):
        self.FiberRadius = FiberRadius
        self.Fusion = Fusion
        self.Angles = Angles
        self.NFiber = len(Angles)

        self._Fibers = None
        self._CoreShift = None
        self._Centers = None
        self._MaxDistance = None


    @property
    def MaxDistance(self):
        if self._MaxDistance is None:
            self.ComputeMaxDistance()
        return self._MaxDistance


    @property
    def Fibers(self):
        if self._Fibers is None:
            self.ComputeFibers()
        return self._Fibers


    @property
    def Centers(self):
        if self._Centers is None:
            self.ComputeCenters()
        return self._Centers


    @property
    def CoreShift(self):
        if self._CoreShift is None:
            self.ComputeCoreShift()
        return self._CoreShift


    def AddRing(self, Ring):
        P0 = Buffer.Point([0, Layer*self.CoreShift])
        Points = Rotate(Object=P0, Angle=Angle)
        self._Centers = [*self._Centers, *Points]


    def ComputeFibers(self):

        self._Fibers = []

        for n, point in enumerate(self.Centers):
            Fiber = _Fiber( Radius=self.FiberRadius, Center=point, Name=f' Fiber {n}')
            self._Fibers.append( Fiber )


    def ComputeCoreShift(self):
        if self.NFiber == 1:
            self._CoreShift = 0
            return

        else:
            alpha    = (2 - self.NFiber) * numpy.pi / ( 2 * self.NFiber)

            self._CoreShift = ( 1 + numpy.cos(alpha) ) - numpy.sqrt(self.NFiber) * numpy.cos(alpha)

            self._CoreShift =  ( self.FiberRadius - ( self._CoreShift * self.FiberRadius ) * self.Fusion)

            self._CoreShift *= 1 / ( numpy.cos(alpha) )


    def ComputeCenters(self):
        self._Centers = Rotate( Object=Buffer.Point([0, self.CoreShift]), Angle=self.Angles, Origin=[0,0] )


    def ComputeMaxDistance(self):
        x, y = self.Fibers[0].exterior.xy
        x = numpy.asarray(x)
        y = numpy.asarray(y)

        self._MaxDistance = numpy.sqrt(x**2 + y**2).max()

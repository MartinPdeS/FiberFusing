
from dataclasses import dataclass
import numpy

from FiberFusing.Geometry.Utils import BufferMultiPolygon, Buffer, Rotate, BufferPolygon, BufferPoint
from FiberFusing.Geometry.BaseClass import BaseFused, PlotShapely


class Fused7(BaseFused):

    def __init__(self, FiberRadius, Fusion, Index, debug='INFO', Gradient=None):
        super().__init__(FiberRadius  = FiberRadius,
                         Fusion  = Fusion,
                         Angle   = numpy.linspace(0,360, 9, endpoint=False),
                         Index   = Index,
                         debug   = debug)


    def ComputeCenters(self):
        self._Centers = []
        self.AddRing(Radius=self.CoreShift, Angle=numpy.linspace(0,360, 9, endpoint=False))
        self.AddRing(Radius=self.CoreShift, Angle=numpy.linspace(0,360, 3, endpoint=False))
        # self.AddRing(Layer=0, Angle=numpy.linspace(0,360, 3, endpoint=False))





if __name__ == '__main__':
    a = Fused7(FiberRadius=62.5, Fusion=0.1, Index=1)
    a.Plot(Fibers=True, Added=False, Removed=False, Circles=False, Mask=True, Base=True)

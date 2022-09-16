
import numpy
from dataclasses import dataclass

from FiberFusing.Geometry.Utils import BufferMultiPolygon, Buffer, Rotate, BufferPolygon, BufferPoint
from FiberFusing.Geometry.BaseClass import BaseFused, FiberRing


class Fused3(BaseFused):
    def __init__(self, FiberRadius, Fusion, Index, debug='INFO', Gradient=None):
        super().__init__(FiberRadius  = FiberRadius,
                         Fusion       = Fusion,
                         Angle        = numpy.linspace(0,360, 3, endpoint=False),
                         Index        = Index,
                         debug        = debug)

        Ring0 = FiberRing(Angles=self.Angle, Fusion=self.Fusion, FiberRadius=self.FiberRadius)

        self.AddRing( Ring0 )

        self.Object = self.OptimizeGeometry()



if __name__ == '__main__':
    a = Fused3(FiberRadius=60, Fusion=0.7, Index=1)
    a.Plot(Fibers=True, Added=True, Removed=False, Virtual=False, Mask=False)


from dataclasses import dataclass
import numpy

from FiberFusing.Geometry.Utils import BufferMultiPolygon, Buffer, Rotate, BufferPolygon, BufferPoint
from FiberFusing.Geometry.BaseClass import BaseFused, FiberRing


class Fused7(BaseFused):

    def __init__(self, FiberRadius, Fusion, Index, debug='INFO', Gradient=None):
        super().__init__(FiberRadius  = FiberRadius,
                         Fusion       = Fusion,
                         Angle        = numpy.linspace(0,360, 6, endpoint=False),
                         Index        = Index,
                         debug        = debug)

        Ring0 = FiberRing(Angles=self.Angle, Fusion=self.Fusion, FiberRadius=self.FiberRadius)
        Ring1 = FiberRing(Angles=[0], Fusion=self.Fusion, FiberRadius=self.FiberRadius)

        self.AddRing( Ring0, Ring1 )

        self.Object = self.OptimizeGeometry()


if __name__ == '__main__':
    a = Fused7(FiberRadius=62.5, Fusion=0.2, Index=1)
    a.Plot(Base=True)

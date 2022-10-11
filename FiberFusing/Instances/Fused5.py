
import numpy
from dataclasses import dataclass

from FiberFusing.BaseClass import BaseFused
from FiberFusing.Rings import FiberRing


class Fused5(BaseFused):
    def __init__(self, FiberRadius, Fusion, Index, debug='INFO', Gradient=None):
        super().__init__(FiberRadius  = FiberRadius,
                         Fusion       = Fusion,
                         Angle        = numpy.linspace(0,360, 5, endpoint=False),
                         Index        = Index,
                         debug        = debug)

        Ring0 = FiberRing(Angles=self.Angle, Fusion=self.Fusion, FiberRadius=self.FiberRadius)

        self.AddRing( Ring0 )

        self.Object = self.OptimizeGeometry()



if __name__ == '__main__':
    a = Fused5(FiberRadius=60, Fusion=1, Index=1)
    a.Plot(Fibers=True, Added=True, Removed=False, Virtual=False, Mask=False)

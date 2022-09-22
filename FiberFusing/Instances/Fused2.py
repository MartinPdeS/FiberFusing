
import numpy
from dataclasses import dataclass

from FiberFusing.BaseClass import BaseFused
from FiberFusing.Rings import FiberRing


class Fused2(BaseFused):
    def __init__(self, FiberRadius, Fusion, Index, debug='INFO', Gradient=None):
        super().__init__(FiberRadius  = FiberRadius,
                         Fusion       = Fusion,
                         Angle        = numpy.linspace(0,360, 2, endpoint=False),
                         Index        = Index,
                         debug        = debug)

        assert 0 <= Fusion <= 1, "Fusion degree has to be in the range [0, 1]"
        Ring0 = FiberRing(Angles=self.Angle, Fusion=self.Fusion, FiberRadius=self.FiberRadius)

        self.AddRing( Ring0 )

        self.Object = self.OptimizeGeometry()



if __name__ == '__main__':
    a = Fused2(FiberRadius=60, Fusion=0.3, Index=1)
    a.Plot(Fibers=True, Added=True, Removed=True, Virtual=True, Mask=False)


import numpy
from dataclasses import dataclass

from FiberFusing.BaseClass import BaseFused
from FiberFusing.Rings import FiberRing


class Fused7(BaseFused):
    def __init__(self, FiberRadius, Fusion, Index, debug='INFO', Gradient=None):
        super().__init__(FiberRadius  = FiberRadius,
                         Fusion       = Fusion,
                         Angle        = numpy.linspace(0,360, 6, endpoint=False),
                         Index        = Index,
                         debug        = debug)

        assert 0 <= Fusion <= 0.65, "Fusion degree has to be in the range [0, 0.65]"
        Ring0 = FiberRing(Angles=self.Angle, Fusion=self.Fusion, FiberRadius=self.FiberRadius)
        Ring1 = FiberRing(Angles=[0], Fusion=self.Fusion, FiberRadius=self.FiberRadius)

        self.AddRing( Ring0, Ring1 )

        self.Object = self.OptimizeGeometry()



if __name__ == '__main__':
    a = Fused7(FiberRadius=60, Fusion=0.60, Index=1)
    a.Plot(Fibers=True, Added=True, Removed=True, Virtual=False, Mask=False)
    


import numpy
from dataclasses import dataclass

from FiberFusing.BaseClass import BaseFused
from FiberFusing.Rings import FiberRing


class Fused4(BaseFused):
    def __init__(self, FiberRadius, Fusion, Index, debug='INFO', Gradient=None):
        FusionRange = [0,1]
        super().__init__(FiberRadius  = FiberRadius,
                         Fusion       = Fusion,
                         Angle        = numpy.linspace(0,360, 4, endpoint=False),
                         Index        = Index,
                         debug        = debug)

        assert FusionRange[0] <= Fusion <= FusionRange[1], f"Fusion degree has to be in the range {FusionRange}"

        Ring0 = FiberRing(Angles=self.Angle, Fusion=self.Fusion, FiberRadius=self.FiberRadius)

        self.AddRing( Ring0 )

        self.Object = self.OptimizeGeometry()



if __name__ == '__main__':
    a = Fused4(FiberRadius=62.5, Fusion=1, Index=1)
    a.Plot(Fibers=False, Added=True, Removed=False, Virtual=False, Mask=False)

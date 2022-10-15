
import numpy
from dataclasses import dataclass

from FiberFusing.BaseClass import BaseFused
from FiberFusing.Rings import FiberRing


class Fused19(BaseFused):
    def __init__(self, FiberRadius, Fusion, Index, debug='INFO', Gradient=None):
        super().__init__(FiberRadius  = FiberRadius,
                         Fusion       = Fusion,
                         Angle        = numpy.linspace(0,360, 7, endpoint=False),
                         Index        = Index,
                         debug        = debug)

        Ring0 = FiberRing(Angles= numpy.linspace(0,360, 6, endpoint=False), Fusion=self.Fusion, FiberRadius=self.FiberRadius)
        Ring1 = FiberRing(Angles=[0], Fusion=self.Fusion, FiberRadius=self.FiberRadius)
        Ring2 = FiberRing(Angles= numpy.linspace(0,360, 12, endpoint=False)+180/12, Fusion=self.Fusion, FiberRadius=self.FiberRadius)

        self.AddRing( Ring0, Ring1, Ring2 )
        
        self.Object = self.OptimizeGeometry()



if __name__ == '__main__':
    a = Fused19(FiberRadius=60, Fusion=0.3, Index=1)
    a.Plot(Fibers=True, Added=True, Removed=False, Virtual=False, Mask=False)

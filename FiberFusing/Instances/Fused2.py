

import numpy
from dataclasses import dataclass

from FiberFusing.Geometry.Utils import BufferPolygon, Rotate, Buffer, BufferPoint
from FiberFusing.Geometry.BaseClass import BaseFused

class Fused2(BaseFused):
    def __init__(self, FiberRadius, Fusion, Index, debug='INFO', Gradient=None):
        super().__init__(FiberRadius  = FiberRadius,
                         Fusion       = Fusion,
                         Angle        = [0, 180],
                         Index        = Index,
                         debug        = debug)


    def ComputeCenters(self):
        self._Centers = []
        self.AddRing(Layer=1, Angle=numpy.linspace(0,360, 2, endpoint=False))


if __name__ == '__main__':
    a = Fused2(FiberRadius=60, Fusion=0.2, Index=1)
    a.Plot(Added=True, Removed=True, Circles=True, Mask=True, Base=True)

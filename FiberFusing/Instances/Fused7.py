import numpy

from FiberFusing.BaseClass import BaseFused
from FiberFusing.Rings import FiberRing


class Fused7(BaseFused):
    def __init__(self,
                 fiber_radius: float,
                 fusion_degree: float,
                 index: float,
                 core_position_scrambling: float = 0):

        super().__init__(fiber_radius=fiber_radius,
                         fusion_degree=fusion_degree,
                         index=index,
                         core_position_scrambling=core_position_scrambling)

        assert 0 <= fusion_degree <= 0.65, "Fusion degree has to be in the range [0, 0.65]"

        Ring0 = FiberRing(angle_list=numpy.linspace(0, 360, 6, endpoint=False),
                          fusion_degree=self.fusion_degree,
                          fiber_radius=self.fiber_radius)

        Ring1 = FiberRing(angle_list=[0],
                          fusion_degree=self.fusion_degree,
                          fiber_radius=self.fiber_radius)

        self.add_fiber_ring(Ring0, Ring1)

        self.Object = self.optimize_geometry()


if __name__ == '__main__':
    a = Fused7(fiber_radius=62.5, fusion_degree=0.6, index=1)
    a.Plot(Fibers=False, Added=True, Removed=False, Virtual=False, Mask=False).Show()

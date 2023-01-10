
import numpy

from FiberFusing.BaseClass import BaseFused
from FiberFusing.Rings import FiberRing


class Fused4(BaseFused):
    def __init__(self,
                 fiber_radius: float,
                 fusion_degree: float,
                 index: float,
                 core_position_scrambling: float = 0):

        super().__init__(fiber_radius=fiber_radius,
                         fusion_degree=fusion_degree,
                         index=index,
                         core_position_scrambling=core_position_scrambling)

        FusionRange = [0, 1]
        assert FusionRange[0] <= fusion_degree <= FusionRange[1], f"Fusion degree has to be in the range {FusionRange}"

        Ring0 = FiberRing(angle_list=numpy.linspace(0, 360, 4, endpoint=False),
                          fusion_degree=self.fusion_degree,
                          fiber_radius=self.fiber_radius)

        self.add_fiber_ring(Ring0)

        self.Object = self.optimize_geometry()


if __name__ == '__main__':
    a = Fused4(fiber_radius=62.5, fusion_degree=1, index=1)
    a.Plot(show_fibers=True, show_added=True, show_removed=True).Show()

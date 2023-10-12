#!/usr/bin/env python
# -*- coding: utf-8 -*-

from FiberFusing.baseclass import BaseFused


class FusedProfile_01x01(BaseFused):
    fusion_range = [0, .35]
    number_of_fibers = 1

    def __init__(self,
            fiber_radius: float,
            index: float,
            core_position_scrambling: float = 0.,
            fusion_degree: float = 0.8):

        super().__init__(index=index, fusion_degree=fusion_degree)

        self.add_center_fiber(fiber_radius=fiber_radius)

        self._clad_structure = self.fiber_list[0]

        self.randomize_core_position(randomize_position=core_position_scrambling)


if __name__ == '__main__':
    instance = FusedProfile_01x01(
        fiber_radius=62.5e-6,
        index=1,
        core_position_scrambling=0,
        fusion_degree=0.3
    )

    figure = instance.plot(
        show_structure=False,
        show_fibers=True,
        show_cores=False,
        show_added=True,
        show_removed=True
    )

    figure.show()

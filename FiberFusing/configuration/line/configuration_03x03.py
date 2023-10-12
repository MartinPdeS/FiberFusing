#!/usr/bin/env python
# -*- coding: utf-8 -*-

from FiberFusing.baseclass import BaseFused


class FusedProfile_03x03(BaseFused):
    fusion_range = [0, .35]
    number_of_fibers = 3

    def __init__(self,
            fiber_radius: float,
            index: float,
            core_position_scrambling: float = 0,
            fusion_degree: float = 0.3):

        super().__init__(index=index, fusion_degree=fusion_degree)

        self.add_fiber_line(
            number_of_fibers=3,
            fusion_degree=fusion_degree,
            fiber_radius=fiber_radius,
            compute_fusing=True
        )

        self.randomize_core_position(randomize_position=core_position_scrambling)


if __name__ == '__main__':
    instance = FusedProfile_03x03(
        fiber_radius=62.5e-6,
        index=1,
        core_position_scrambling=0,
        fusion_degree=0.3
    )

    figure = instance.plot(
        show_structure=False,
        show_fibers=True,
        show_shifted_cores=True,
        show_added=True,
        show_removed=True
    )

    figure.show()

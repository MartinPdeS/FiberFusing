#!/usr/bin/env python
# -*- coding: utf-8 -*-

from FiberFusing.baseclass import BaseFused


class FusedProfile_10x10(BaseFused):
    fusion_range = None
    number_of_fibers = 10

    def __init__(self,
            fiber_radius: float,
            index: float,
            fusion_degree: float = None,
            core_position_scrambling: float = 0):

        super().__init__(index=index, fusion_degree=fusion_degree)

        self.add_fiber_ring(
            number_of_fibers=7,
            fiber_radius=fiber_radius,
            scale_position=1.3,
            compute_fusing=False
        )

        self.add_fiber_ring(
            number_of_fibers=3,
            fiber_radius=fiber_radius,
            scale_position=1,
            angle_shift=25,
            position_shift=[0, 0],
            compute_fusing=False
        )

        self.randomize_core_position(randomize_position=core_position_scrambling)


if __name__ == '__main__':
    instance = FusedProfile_10x10(
        fiber_radius=62.5e-6,
        index=1
    )

    figure = instance.plot(
        show_structure=True,
        show_fibers=True,
        show_shifted_cores=False,
        show_added=False
    )

    figure.show()

# -

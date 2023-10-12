#!/usr/bin/env python
# -*- coding: utf-8 -*-

from FiberFusing.baseclass import BaseFused


class FusedProfile_04x04(BaseFused):
    fusion_range = [0, 0.4]
    number_of_fibers = 4

    def __init__(self,
            fiber_radius: float,
            index: float,
            fusion_degree: float = 0.3,
            core_position_scrambling: float = 0):

        super().__init__(index=index, fusion_degree=fusion_degree)

        self.add_fiber_ring(
            number_of_fibers=4,
            fusion_degree=fusion_degree,
            fiber_radius=fiber_radius,
            compute_fusing=True
        )

        self.randomize_core_position(randomize_position=core_position_scrambling)


if __name__ == '__main__':
    instance = FusedProfile_04x04(
        fiber_radius=62.5,
        fusion_degree=0.4,
        index=1
    )

    figure = instance.plot(
        show_structure=True,
        show_fibers=True,
        show_shifted_cores=True,
        show_added=True,
        show_removed=True
    )

    figure.show()

# -

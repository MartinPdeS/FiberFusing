#!/usr/bin/env python
# -*- coding: utf-8 -*-

from FiberFusing.baseclass import BaseFused


class FusedProfile_02x02(BaseFused):
    fusion_range = [0, 1]
    number_of_fibers = 2

    def __init__(self,
            fiber_radius: float,
            index: float,
            fusion_degree: float = None,
            core_position_scrambling: float = 0):

        fusion_degree = 0.7 if fusion_degree is None else fusion_degree
        super().__init__(index=index, fusion_degree=fusion_degree)

        self.add_fiber_ring(
            number_of_fibers=2,
            fusion_degree=fusion_degree,
            fiber_radius=fiber_radius,
            compute_fusing=True
        )

        self.randomize_core_position(randomize_position=core_position_scrambling)


if __name__ == '__main__':
    instance = FusedProfile_02x02(
        fiber_radius=62.5e-6,
        fusion_degree=0.6,
        index=1
    )

    figure = instance.plot(
        show_structure=False,
        show_fibers=True,
        show_shifted_cores=True,
        show_added=True,
        show_removed=True
    )

    figure.show()

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from FiberFusing.base_fused import BaseFused


class FusedProfile_05x05(BaseFused):
    fusion_range = [0, .35]
    number_of_fibers = 5

    def __post_init__(self):

        super().__post_init__()

        self.add_structure(
            structure_type='line',
            number_of_fibers=5,
            fusion_degree=self.parametrized_fusion_degree,
            fiber_radius=self.fiber_radius,
            compute_fusing=True
        )

        self.randomize_core_position(random_factor=self.core_position_scrambling)


if __name__ == '__main__':
    instance = FusedProfile_05x05(
        fiber_radius=62.5e-6,
        index=1,
        core_position_scrambling=0,
        fusion_degree=0.7
    )

    figure = instance.plot()

    figure.show()

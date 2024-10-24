#!/usr/bin/env python
# -*- coding: utf-8 -*-

from FiberFusing.base_fused import BaseFused


class FusedProfile_04x04(BaseFused):
    fusion_range = [0, .35]
    number_of_fibers = 4

    def __post_init__(self):

        super().__post_init__()

        self.add_structure(
            structure_type='line',
            number_of_fibers=4,
            fusion_degree=self.parametrized_fusion_degree,
            fiber_radius=self.fiber_radius,
            compute_fusing=True
        )

        self.randomize_core_position(random_factor=self.core_position_scrambling)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from FiberFusing.base_fused import BaseFused


class FusedProfile_12x12(BaseFused):
    fusion_range = None
    number_of_fibers = 12

    def __post_init__(self):

        super().__post_init__()

        self.add_structure(
            structure_type='ring',
            number_of_fibers=3,
            fusion_degree=self.parametrized_fusion_degree,
            fiber_radius=self.fiber_radius,
            scale_position=1.0,
            angle_shift=0,
            compute_fusing=False
        )

        self.add_structure(
            structure_type='ring',
            number_of_fibers=9,
            fusion_degree=self.parametrized_fusion_degree,
            fiber_radius=self.fiber_radius,
            scale_position=1.05,
            compute_fusing=False,
            angle_shift=20,
        )

        self.randomize_core_position(random_factor=self.core_position_scrambling)

        self.scale_position(factor=self.scale_down_position)

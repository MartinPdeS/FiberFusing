#!/usr/bin/env python
# -*- coding: utf-8 -*-

from FiberFusing.base_fused import BaseFused


class FusedProfile_19x19(BaseFused):
    fusion_range = None
    number_of_fibers = 19

    def __post_init__(self):

        super().__post_init__()

        self.add_structure(
            structure_type='ring',
            number_of_fibers=6,
            fusion_degree=self.parametrized_fusion_degree,
            fiber_radius=self.fiber_radius,
            scale_position=1.0,
            angle_shift=0,
            compute_fusing=False
        )

        self.add_structure(
            structure_type='ring',
            number_of_fibers=12,
            fusion_degree=self.parametrized_fusion_degree,
            fiber_radius=self.fiber_radius,
            scale_position=1.00,
            compute_fusing=False,
            angle_shift=15,
        )

        self.add_center_fiber(fiber_radius=self.fiber_radius)

        self.randomize_core_position(random_factor=self.core_position_scrambling)

        self.scale_position(factor=self.scale_down_position)

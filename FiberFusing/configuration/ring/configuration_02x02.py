#!/usr/bin/env python
# -*- coding: utf-8 -*-

from FiberFusing.base_fused import BaseFused


class FusedProfile_02x02(BaseFused):
    fusion_range = [0, 1]
    number_of_fibers = 2

    def initialize_structure(self):
        self.add_structure(
            structure_type='ring',
            number_of_fibers=2,
            fusion_degree=self.parametrized_fusion_degree,
            fiber_radius=self.fiber_radius,
            compute_fusing=True
        )

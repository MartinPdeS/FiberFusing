#!/usr/bin/env python
# -*- coding: utf-8 -*-

from FiberFusing.base_fused import BaseFused


class FusedProfile_07x07(BaseFused):
    fusion_range = [0, 0.3]
    number_of_fibers = 7

    def __post_init__(self):

        super().__post_init__()

        self.add_structure(
            structure_type='ring',
            number_of_fibers=6,
            fusion_degree=self.parametrized_fusion_degree,
            fiber_radius=self.fiber_radius,
            compute_fusing=True
        )

        self.add_center_fiber(fiber_radius=self.fiber_radius)

        self.randomize_core_position(random_factor=self.core_position_scrambling)


if __name__ == '__main__':
    instance = FusedProfile_07x07(
        fiber_radius=62.5e-6,
        fusion_degree=0.3,
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

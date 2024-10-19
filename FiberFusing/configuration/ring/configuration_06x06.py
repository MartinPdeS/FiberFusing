#!/usr/bin/env python
# -*- coding: utf-8 -*-

from FiberFusing.base_fused import BaseFused


class FusedProfile_06x06(BaseFused):
    fusion_range = [0, 0.45]
    number_of_fibers = 6

    def __post_init__(self):

        super().__post_init__()

        self.add_structure(
            structure_type='ring',
            number_of_fibers=6,
            fusion_degree=self.parametrized_fusion_degree,
            fiber_radius=self.fiber_radius,
            compute_fusing=True
        )

        self.randomize_core_position(random_factor=self.core_position_scrambling)


if __name__ == '__main__':
    instance = FusedProfile_06x06(
        fiber_radius=62.5,
        fusion_degree=0.45,
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

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from FiberFusing.baseclass import BaseFused


class FusedProfile_02x02(BaseFused):
    fusion_range = [0, 1]
    number_of_fibers = 2

    def __post_init__(self):

        super().__post_init__()

        self.add_structure(
            structure_type='ring',
            number_of_fibers=2,
            fusion_degree=self.parametrized_fusion_degree,
            fiber_radius=self.fiber_radius,
            compute_fusing=True
        )

        self.randomize_core_position(random_factor=self.core_position_scrambling)


if __name__ == '__main__':
    instance = FusedProfile_02x02(
        fiber_radius=62.5e-6,
        fusion_degree=0.6,
        index=1
    )

    figure = instance.plot()

    figure.show()

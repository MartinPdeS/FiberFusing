#!/usr/bin/env python
# -*- coding: utf-8 -*-

from FiberFusing.base_fused import BaseFused


class FusedProfile_01x01(BaseFused):
    fusion_range = None
    number_of_fibers = 1

    def __post_init__(self):
        super().__post_init__()

        self.add_center_fiber(fiber_radius=self.fiber_radius)

        self._clad_structure = self.fiber_list[0]

        self.randomize_core_position(random_factor=self.core_position_scrambling)


if __name__ == '__main__':
    instance = FusedProfile_01x01(
        fiber_radius=62.5e-6,
        index=1,
        core_position_scrambling=2e-6
    )

    figure = instance.plot()

    figure.show()

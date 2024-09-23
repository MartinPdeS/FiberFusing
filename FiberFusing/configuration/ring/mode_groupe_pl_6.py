#!/usr/bin/env python
# -*- coding: utf-8 -*-

from FiberFusing.base_fused import BaseFused
import logging


class FusedModeGroupePhotonicLantern6(BaseFused):
    def __init__(self,
                 fiber_radius: float,
                 index: float,
                 fusion_degree: float = None,
                 core_position_scrambling: float = 0):

        if fusion_degree is not None:
            logging.warning(f"This instance: {self.__class__} do not take fusion_degree as argument.")

        super().__init__(index=index)

        self.add_fiber_ring(
            number_of_fibers=5,
            fiber_radius=125e-6 / 2,
            scale_position=0.93,
            angle_shift=0,
            compute_fusing=True
        )

        self.add_center_fiber(fiber_radius=180e-6)

        self.randomize_core_position(randomize_position=core_position_scrambling)


if __name__ == '__main__':
    instance = FusedModeGroupePhotonicLantern6(
        fiber_radius=62.5e-6,
        index=1
    )

    figure = instance.plot(
        show_structure=True,
        show_fibers=True,
        show_cores=True,
        show_added=False
    )

    figure.show()

# -

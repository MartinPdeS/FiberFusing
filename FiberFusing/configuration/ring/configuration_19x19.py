#!/usr/bin/env python
# -*- coding: utf-8 -*-

from FiberFusing.baseclass import BaseFused
import logging


class FusedProfile_19x19(BaseFused):
    fusion_range = None
    number_of_fibers = 19

    def __init__(self,
            fiber_radius: float,
            index: float,
            scale_down: float = 1,
            fusion_degree: float = None,
            core_position_scrambling: float = 0):

        if fusion_degree is not None:
            logging.warning(f"This instance: {self.__class__} do not take fusion_degree as argument.")

        super().__init__(index=index)

        self.add_fiber_ring(
            number_of_fibers=6,
            fusion_degree=0,
            fiber_radius=fiber_radius,
            compute_fusing=False
        )

        self.add_fiber_ring(
            number_of_fibers=12,
            fusion_degree=0,
            fiber_radius=fiber_radius,
            angle_shift=15,
            compute_fusing=False
        )

        self.add_center_fiber(fiber_radius=fiber_radius)

        print(dir(self))

        self.randomize_core_position(randomize_position=core_position_scrambling)

        self.scale_position(factor=scale_down)


if __name__ == '__main__':
    instance = FusedProfile_19x19(
        fiber_radius=62.5,
        index=1,
        scale_down=1
    )

    figure = instance.plot(
        show_structure=False,
        show_fibers=True,
        show_shifted_cores=False
    )

    figure.show()

    # -

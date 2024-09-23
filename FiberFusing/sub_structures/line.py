#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Built-in imports
import numpy
from dataclasses import dataclass

# Local imports
import FiberFusing as ff
from FiberFusing.utility.connection_optimization import ConnectionOptimization
from FiberFusing.sub_structures.base_class import BaseClass


@dataclass
class FiberLine(ConnectionOptimization, BaseClass):
    number_of_fibers: int
    """ Number of fiber in the ring """
    fiber_radius: float
    """ Radius of the radius of the rings, same for every ringe here """
    rotation_angle: float = 0
    """ Shift angle for the ring configuration """
    tolerance_factor: float = 1e-10

    def __post_init__(self):
        core_positions = self.compute_unfused_positions()

        self.compute_fiber_list(centers=core_positions)

    def compute_unfused_positions(self) -> list:
        """
        Computing the core center with a a certain distance from the origin  (0, 0).

        :param      distance_from_center:  The distance from center
        :type       distance_from_center:  float
        """

        core_positions = numpy.arange(self.number_of_fibers).astype(float)

        core_positions -= core_positions.mean()

        core_positions *= 2 * self.fiber_radius

        rotation_angle = numpy.deg2rad(self.rotation_angle)

        core_positions = [
            (numpy.cos(rotation_angle) * pos, numpy.sin(rotation_angle) * pos) for pos in core_positions
        ]

        core_positions = [
            ff.Point(position=position) for position in core_positions
        ]

        return core_positions


if __name__ == '__main__':
    fiber_line = FiberLine(
        number_of_fibers=4,
        fiber_radius=62e-6,
        tolerance_factor=1e-10,
        rotation_angle=90
    )

    fiber_line.set_fusion_degree(0.7)

    fiber_line.init_connected_fibers()

    fiber_line.compute_optimal_structure()

    figure = fiber_line.plot(
        show_fused=True,
        show_removed=True,
        show_added=True
    )

    figure.show()

# -

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
class FiberRing(ConnectionOptimization, BaseClass):
    number_of_fibers: int
    """ Number of fiber in the ring """
    fiber_radius: float
    """ Radius of the radius of the rings, same for every ringe here """
    angle_shift: float = 0
    """ Shift angle for the ring configuration """
    tolerance_factor: float = 1e-10

    def __post_init__(self):
        self.angle_list = numpy.linspace(0, 360, self.number_of_fibers, endpoint=False)
        self.angle_list += self.angle_shift
        self.delta_angle = (self.angle_list[1] - self.angle_list[0])

        centers = self.compute_unfused_positions(distance_from_center="not-fused")
        self.compute_fiber_list(centers=centers)

    def compute_unfused_positions(self, distance_from_center="not-fused") -> list:
        """
        Computing the core center with a a certain distance from the origin  (0, 0).

        :param      distance_from_center:  The distance from center
        :type       distance_from_center:  float
        """

        factor = numpy.sqrt(2 / (1 - numpy.cos(numpy.deg2rad(self.delta_angle))))

        distance_from_center = factor * self.fiber_radius

        first_core = ff.Point(position=[0, distance_from_center])

        core_position = [
            first_core.rotate(angle=angle, origin=[0, 0]) for angle in self.angle_list
        ]

        return core_position


if __name__ == '__main__':
    fiber_ring = FiberRing(
        number_of_fibers=2,
        fiber_radius=62.5e-6,
        angle_shift=20,
        tolerance_factor=1e-10
    )

    fiber_ring.set_fusion_degree(0.6)

    fiber_ring.init_connected_fibers()

    fiber_ring.compute_optimal_structure()

    figure = fiber_ring.plot(
        show_fused=True,
        show_removed=True,
        show_added=True
    )

    figure.show()

# -

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy

# Local imports
from FiberFusing.buffer import Circle
from FiberFusing import utils

# Other imports
from MPSPlots.render2D import SceneList


class BaseClass():
    @property
    def fused_structure(self):
        return utils.Union(*self.fiber_list, self.added_section)

    @property
    def unfused_structure(self):
        return utils.Union(*self.fiber_list)

    def initialize_cores(self):
        for fiber in self.fiber_list:
            fiber.shifted_core = fiber.center

    def get_scaling_factor_from_fusion_degree(self, fusion_degree: float) -> float:
        """
        Gets equivalent scaling factor from fusion degree value.

        :param      fusion_degree:  The fusion degree
        :type       fusion_degree:  float

        :returns:   The scaling factor.
        :rtype:     float
        """
        factor = 1 - fusion_degree * (2 - numpy.sqrt(2))

        distance_between_cores = 2 * self.fiber_radius * factor

        scaling_factor = distance_between_cores / (2 * self.fiber_radius)

        return scaling_factor

    def set_fusion_degree(self, fusion_degree: float) -> None:
        """
        Changing the fiber position according to the fusion degree
        as it is described the Suzanne Lacroix article.
        Article name: "Modeling of symmetric 2 x 2 fused-fiber couplers"

        :param      fusion_degree:  Value describe the fusion degree of the structure the higher the value to more fused are the fibers [0, 1].
        :type       fusion_degree:  float
        """
        scaling_factor = self.get_scaling_factor_from_fusion_degree(fusion_degree=fusion_degree)

        self.scale_position(factor=scaling_factor)

    def plot(
            self,
            show_fibers: bool = True,
            show_added: bool = False,
            show_removed: bool = False,
            show_fused: bool = False,
            show_unfused: bool = False) -> SceneList:
        """
        Return the figure showing different parts of the structures

        :param      show_fibers:   show the fibers in the plot
        :type       show_fibers:   bool
        :param      show_added:    show the added [green] section in the plot
        :type       show_added:    bool
        :param      show_removed:  show the removed [red] section in the plot
        :type       show_removed:  bool
        :param      show_fused:    show the fused section in the plot
        :type       show_fused:    bool
        :param      show_unfused:  show the unfused section in the plot
        :type       show_unfused:  bool

        :returns:   The scene list.
        :rtype:     SceneList
        """
        figure = SceneList(unit_size=(6, 6))

        ax = figure.append_ax(
            x_label=r'x',
            y_label=r'y',
            show_grid=True,
            equal_limits=False,
        )

        if show_fibers:
            for fiber in self.fiber_list:
                fiber._render_on_ax_(ax)

        if show_added:
            for connection in self.connected_fibers:
                connection.added_section._render_on_ax_(ax, facecolor='green')

        if show_removed:
            for connection in self.connected_fibers:
                connection.removed_section._render_on_ax_(ax, facecolor='red')

        if show_fused:
            self.fused_structure._render_on_ax_(ax=ax)

        if show_unfused:
            self.unfused_structure._render_on_ax_(ax=ax)

        return figure

    def scale_position(self, factor: float) -> None:
        """
        Scale down the distance between each cores.

        :param      factor:  The scaling factor
        :type       factor:  float
        """
        for fiber in self.fiber_list:
            fiber.scale_position(factor=factor)

    def shift_position(self, shift: list) -> None:
        """
        Scale down the distance between each cores.

        :param      factor:  The scaling factor
        :type       factor:  float
        """
        for fiber in self.fiber_list:
            fiber.shift_position(shift=shift)

    def compute_fiber_list(self, centers: list) -> None:
        self.fiber_list = []

        for idx, point in enumerate(centers):
            fiber_circle = Circle(radius=self.fiber_radius, position=(point.x, point.y))

            self.fiber_list.append(fiber_circle)

# -

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy

from FiberFusing.coordinate_system import CoordinateSystem
from FiberFusing.utility.overlay_structure_on_mesh import OverlayStructureBaseClass
from FiberFusing import Circle


class NameSpace():
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class BackGround(OverlayStructureBaseClass):
    def __init__(self, index, radius: float = 1000, position: tuple = (0, 0)):
        self.index = index
        self.position = position
        self.radius = radius

        polygon = Circle(
            position=self.position,
            radius=self.radius,
            index=self.index
        )

        self.structure_list = [
            NameSpace(index=self.index, polygon=polygon, name='background')
        ]

    @property
    def refractive_index_list(self) -> list:
        return [self.index]

    def overlay_structures_on_mesh(self, mesh: numpy.ndarray, coordinate_system: CoordinateSystem) -> numpy.ndarray:
        """
        Return a mesh overlaying all the structures in the order they were defined.

        :param      coordinate_system:  The coordinates axis
        :type       coordinate_system:  Axis

        :returns:   The raster mesh of the structures.
        :rtype:     numpy.ndarray
        """
        return self._overlay_structure_on_mesh_(
            structure_list=self.structure_list,
            mesh=mesh,
            coordinate_system=coordinate_system
        )


# -

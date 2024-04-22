#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy

from FiberFusing.coordinate_system import CoordinateSystem
from FiberFusing.utility.overlay_structure_on_mesh import OverlayStructureBaseClass
from FiberFusing import Circle


class NameSpace:
    """
    A flexible class that allows the dynamic addition of attributes via keyword arguments.
    """

    def __init__(self, **kwargs):
        """
        Initializes an instance with attributes specified by the keyword arguments.

        :param kwargs: Arbitrary keyword arguments to set as attributes.
        """
        for key, value in kwargs.items():
            setattr(self, key, value)


class BackGround(OverlayStructureBaseClass):
    """
    Represents a background structure to be overlayed on a mesh, characterized by a circular shape.

    Attributes:
        index (float): Refractive index of the background.
        radius (float): Radius of the circular structure.
        position (tuple): A tuple (x, y) specifying the position of the circle's center.
        structure_list (list): List of namespaces containing structure data.
    """

    def __init__(self, index: float, radius: float = 1000.0, position: tuple = (0, 0)):
        """
        Initializes a background structure with a specified index, and optionally a radius and position.

        :param index: Refractive index of the background.
        :param radius: Radius of the circle, default is 1000.
        :param position: Cartesian coordinates as a tuple (x, y) for the circle's center, default is (0, 0).
        """
        self.index = index
        self.radius = radius
        self.position = position

        # Create the circular structure
        polygon = Circle(position=self.position, radius=self.radius, index=self.index)
        self.structure_list = [NameSpace(index=self.index, polygon=polygon, name='background')]

    @property
    def refractive_index_list(self) -> list:
        """Returns the list of refractive indices for the structures."""
        return [self.index]

    def overlay_structures_on_mesh(self, mesh: numpy.ndarray, coordinate_system: CoordinateSystem) -> numpy.ndarray:
        """
        Overlays all the structures onto the given mesh using the specified coordinate system.

        :param mesh: A numpy ndarray representing the mesh to overlay on.
        :param coordinate_system: The coordinate system to use for overlaying.
        :returns: A numpy ndarray with the structures overlayed onto the original mesh.
        """
        return self._overlay_structure_on_mesh_(
            structure_list=self.structure_list,
            mesh=mesh,
            coordinate_system=coordinate_system
        )


# -

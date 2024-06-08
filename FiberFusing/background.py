#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Tuple, Optional
from pydantic.dataclasses import dataclass
from pydantic import ConfigDict

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


@dataclass(config=ConfigDict(extra='forbid'), kw_only=True)
class BackGround(OverlayStructureBaseClass):
    """
    Represents a background structure to be overlayed on a mesh, characterized by a circular shape.

    Attributes:
        index (float): Refractive index of the background.
        radius (float): Radius of the circular structure. Defaults to 1000.
        position (Optional[Tuple[float, float]]): A tuple (x, y) specifying the position of the circle's center. Defaults to (0, 0).
        structure_list (list): List of namespaces containing structure data.
    """

    index: float
    radius: float = 1000
    position: Optional[Tuple[float, float]] = (0, 0)

    def __post_init__(self):
        """
        Initializes the background structure by creating a circular polygon.
        """
        # Create the circular structure
        polygon = Circle(
            position=self.position,
            radius=self.radius,
            index=self.index
        )

        background = NameSpace(index=self.index, polygon=polygon, name='background')
        self.structure_list = [background]

    @property
    def refractive_index_list(self) -> list:
        """
        Returns the list of refractive indices for the structures.

        Returns:
            list: A list containing the refractive index of the background.
        """
        return [self.index]

    def overlay_structures_on_mesh(self, mesh: numpy.ndarray, coordinate_system: CoordinateSystem) -> numpy.ndarray:
        """
        Overlays all the structures onto the given mesh using the specified coordinate system.

        Args:
            mesh (numpy.ndarray): A numpy ndarray representing the mesh to overlay on.
            coordinate_system (CoordinateSystem): The coordinate system to use for overlaying.

        Returns:
            numpy.ndarray: A numpy ndarray with the structures overlayed onto the original mesh.
        """
        return self._overlay_structure_on_mesh_(
            structure_list=self.structure_list,
            mesh=mesh,
            coordinate_system=coordinate_system
        )


# -

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Tuple, Optional
from pydantic.dataclasses import dataclass
from pydantic import ConfigDict
import numpy as np

from FiberFusing.coordinate_system import CoordinateSystem
from FiberFusing.helper import OverlayStructureBaseClass
from FiberFusing import Circle


class NameSpace:
    """
    A flexible class that allows dynamic addition of attributes via keyword arguments.
    """
    def __init__(self, **kwargs):
        """
        Initializes an instance with attributes specified by keyword arguments.

        Parameters
        ----------
        **kwargs : dict
            Arbitrary keyword arguments to set as attributes.
        """
        self.__dict__.update(kwargs)


@dataclass(config=ConfigDict(extra='forbid', kw_only=True))
class BackGround(OverlayStructureBaseClass):
    """
    Represents a background structure overlayed on a mesh, characterized by a circular shape.

    Attributes
    ----------
    index : float
        Refractive index of the background.
    radius : float, optional
        Radius of the circular structure, by default 1000.
    position : Optional[Tuple[float, float]], optional
        A tuple (x, y) specifying the position of the circle's center, by default (0, 0).
    """

    index: float
    radius: float = 1000
    position: Optional[Tuple[float, float]] = (0, 0)

    def __post_init__(self):
        """
        Initializes the background structure by creating a circular polygon.
        """
        polygon = Circle(position=self.position, radius=self.radius, index=self.index)
        self.structure_list = [NameSpace(index=self.index, polygon=polygon, name='background')]

    @property
    def refractive_index_list(self) -> list:
        """
        Returns the list of refractive indices for the structures.

        Returns
        -------
        list
            A list containing the refractive index of the background.
        """
        return [self.index]

    def overlay_structures_on_mesh(self, mesh: np.ndarray, coordinate_system: CoordinateSystem) -> np.ndarray:
        """
        Overlays all structures onto the given mesh using the specified coordinate system.

        Parameters
        ----------
        mesh : np.ndarray
            The mesh to overlay structures onto.
        coordinate_system : CoordinateSystem
            The coordinate system used for overlaying.

        Returns
        -------
        np.ndarray
            A numpy ndarray with the structures overlayed onto the original mesh.
        """
        return self._overlay_structure_on_mesh_(
            structure_list=self.structure_list,
            mesh=mesh,
            coordinate_system=coordinate_system
        )

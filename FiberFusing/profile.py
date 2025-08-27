#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import Union, Optional, List, Dict, Tuple
import matplotlib.pyplot as plt
import numpy as np
import logging
from FiberFusing.coordinate_system import CoordinateSystem
from FiberFusing.shapes.circle import Circle
from FiberFusing.structures import FiberLine, FiberRing
from FiberFusing.utils import union_geometries, NameSpace
from FiberFusing.helper import _plot_helper, OverlayStructureBaseClass
from enum import Enum

logging.basicConfig(level=logging.INFO)

class StructureType(Enum):
    CIRCULAR = "circular"
    LINEAR = "linear"

class Profile(OverlayStructureBaseClass):
    """
    Base class for managing the fusion of optical fiber structures, allowing customization of fiber properties
    and spatial configuration. This class facilitates the dynamic assembly of fiber optics structures and automates
    the overlay of these structures on a given mesh.

    Parameters
    ----------
    tolerance_factor : float, optional
        A tolerance value used in optimization algorithms to balance the area difference between added and removed
        sections during the fusion process. Default is 1e-2.
    scale_down_position : float, optional
        Scaling factor to adjust the overall size of the assembly. Default is 1.
    """

    def __init__(self, tolerance_factor: Optional[float] = 1e-2, scale_down_position: Optional[float] = 1):
        """
        Initialize the fiber and core lists and other structures immediately after the dataclass fields
        have been populated.
        """
        self.tolerance_factor = tolerance_factor

        self.scale_down_position = scale_down_position

        self._initialize_parameters()

    def _initialize_parameters(self) -> None:
        self.fiber_list = []
        self.core_list = []
        self._clad_structure = None
        self.structure_list = []
        self.removed_section_list = []
        self.added_section_list = []

    def randomize_core_positions(self, random_factor: float = 0) -> "Profile":
        """
        Randomize the position of fiber cores to simulate real-world imperfections.

        Parameters
        ----------
        random_factor : float, optional
            Factor determining the randomness in position. Default is 0.

        Returns
        -------
        Profile
            The updated Profile instance.
        """
        if random_factor == 0:
            return self

        logging.info("Randomizing core positions.")
        for fiber in self.fiber_list:
            fiber.shifted_core = fiber.core
            random_shift = np.random.rand(2) * random_factor
            fiber.shifted_core.translate(random_shift, in_place=True)

        return self

    @property
    def fusion_degree(self) -> float:
        return self._fusion_degree

    @fusion_degree.setter
    def fusion_degree(self, value: float | str) -> None:
        if isinstance(value, str) and value.lower() == 'auto':
            if self.fusion_range is not None:
                value = 0.8
                self._fusion_degree = value
                self.parametrized_fusion_degree = self.fusion_range[0] * (1 - value) + value * self.fusion_range[-1]
            else:
                self._fusion_degree = self.parametrized_fusion_degree = None

        elif np.isscalar(value):
            assert 0 <= value <= 1, f"Fusion degree [{value}] must be within the range [0, 1]."
            self._fusion_degree = value
            self.parametrized_fusion_degree = self.fusion_range[0] * (1 - value) + value * self.fusion_range[-1]

        else:
            f"Input for fusion_degree [{value}] is invalid."

        self._initialize_parameters()

    @property
    def clad_structure(self):
        """
        Get the clad structure, computing it if necessary.

        Returns
        -------
        Polygon
            The union of all structures in the assembly.
        """
        if self._clad_structure is None:
            self._clad_structure = union_geometries(*self.structure_list)
        return self._clad_structure

    @property
    def structure_dictionary(self) -> Dict[str, Dict[str, object]]:
        """
        Get a dictionary representation of the structure.

        Returns
        -------
        dict
            A dictionary with the structure's name, refractive_index, and polygon.
        """
        return {'name': {'refractive_index': self.refractive_index, 'polygon': self.clad_structure}}

    def overlay_structures_on_mesh(self, mesh: np.ndarray, coordinate_system: CoordinateSystem) -> np.ndarray:
        """
        Apply the current fiber structure configuration onto a provided mesh.

        Parameters
        ----------
        mesh : np.ndarray
            The mesh on which to overlay the structure.
        coordinate_system : CoordinateSystem
            The coordinate system to use for the overlay.

        Returns
        -------
        np.ndarray
            The mesh with fiber structures overlaid.
        """
        structure_list = [NameSpace(refractive_index=self.refractive_index, polygon=self.clad_structure)]
        return self._overlay_structure_on_mesh_(
            structure_list=structure_list, mesh=mesh, coordinate_system=coordinate_system
        )

    def get_structure_max_min_boundaries(self) -> Tuple[float, float, float, float]:
        """
        Get the maximum and minimum boundaries of the clad structure.

        Returns
        -------
        tuple
            The bounding box of the clad structure.
        """
        return self.clad_structure.bounds

    def add_single_fiber(self, fiber_radius: float, position: Tuple[float, float] = (0, 0)) -> "Profile":
        """
        Add a single fiber to the structure at the specified position.

        Parameters
        ----------
        fiber_radius : float
            The radius of the fiber.
        position : tuple, optional
            The x, y coordinates for the fiber. Defaults to (0, 0).

        Returns
        -------
        Profile
            The updated Profile instance.
        """
        fiber = Circle(radius=fiber_radius, position=position)
        fiber.shifted_core = fiber.center

        self.structure_list.append(fiber)
        self.fiber_list.append(fiber)

        return self

    def add_center_fiber(self, fiber_radius: float) -> "Profile":
        """
        Add a single fiber at the center of the structure.

        Parameters
        ----------
        fiber_radius : float
            The radius of the fiber.

        Returns
        -------
        Profile
            The updated Profile instance.
        """
        return self.add_single_fiber(fiber_radius=fiber_radius, position=(0, 0))

    def add_center_structure(self, fiber_radius: float) -> "Profile":
        """
        Add a single structure of a given radius at the center of the structure.

        Parameters
        ----------
        fiber_radius : float
            The fiber radius.

        Returns
        -------
        Profile
            The updated Profile instance.
        """
        return self.add_single_fiber(fiber_radius=fiber_radius, position=(0, 0))

    def _add_structure_to_instance_(
        self,
        structure: Union[FiberRing, FiberLine],
        fusion_degree: float | None = None,
        scale_position: float = 1.0,
        position_shift: List[float] = [0, 0]
    ) -> "Profile":
        """
        Internal method to add a fiber structure to the instance.

        Parameters
        ----------
        structure : Union[FiberRing, FiberLine]
            The fiber structure to add.
        fusion_degree : float | None, optional
            The degree of fusion. Default is None which means no fusion is applied.
        scale_position : float, optional
            Factor to scale the position. Default is 1.0.
        position_shift : list of float, optional
            Shift vector for the position. Default is [0, 0].

        Returns
        -------
        Profile
            The updated Profile instance.
        """
        if fusion_degree is not None:
            structure.set_fusion_degree(fusion_degree=fusion_degree)

        structure.scale_position(factor=scale_position)
        structure.shift_position(shift=position_shift)
        structure.initialize_cores()

        self.fiber_list.extend(structure.fiber_list)

        if fusion_degree is not None:
            structure.init_connected_fibers()
            structure.compute_optimal_structure()
            self.removed_section_list.append(structure.removed_section)
            self.added_section_list.append(structure.added_section)
            self.structure_list.append(structure.fused_structure)
        else:
            self.structure_list.append(structure.unfused_structure)

        return self

    def add_structure(
        self,
        structure_type: str,
        number_of_fibers: int,
        fiber_radius: float,
        fusion_degree: float = 0.0,
        scale_position: float = 1.0,
        position_shift: List[float] = [0, 0],
        angle_shift: float = 0.0
    ) -> "Profile":
        """
        Add a predefined structure of fibers, such as a ring or line, with customizable properties and spatial configuration.

        Parameters
        ----------
        structure_type : str
            The type of structure to add ('ring' or 'line').
        number_of_fibers : int
            Number of fibers in the structure.
        fiber_radius : float
            Radius of each fiber in the structure.
        fusion_degree : float, optional
            The degree of fusion for this structure. Default is 0.0.
        scale_position : float, optional
            Factor to scale the position of each fiber. Default is 1.0.
        position_shift : list of float, optional
            A 2D vector [x, y] to shift the entire structure. Default is [0, 0].
        angle_shift : float, optional
            The angle by which to rotate the structure. Default is 0.0.

        Returns
        -------
        Profile
            The updated Profile instance.
        """

        match structure_type:
            case StructureType.CIRCULAR:
                structure = FiberRing(
                    number_of_fibers=number_of_fibers,
                    fiber_radius=fiber_radius,
                angle_shift=angle_shift
            )
            case StructureType.LINEAR:
                structure = FiberLine(
                    number_of_fibers=number_of_fibers,
                    fiber_radius=fiber_radius
                )
            case _:
                raise ValueError(f"Unsupported structure type: {structure_type}. Use 'circular' or 'linear'.")

        return self._add_structure_to_instance_(
            structure=structure,
            fusion_degree=fusion_degree,
            scale_position=scale_position,
            position_shift=position_shift
        )

    def add_custom_fiber(self, *fibers) -> None:
        """
        Add custom-defined fibers to the structure.

        Parameters
        ----------
        fibers : variable
            Custom fiber objects to be added.
        """
        self.fiber_list.extend(fibers)

    @property
    def cores(self) -> List:
        return [fiber.shifted_core for fiber in self.fiber_list]

    def get_core_positions(self) -> List[Tuple[float, float]]:
        """
        Get a list of core positions for all fibers in the structure.

        Returns
        -------
        list of tuple
            A list of core positions.
        """
        return [fiber.core for fiber in self.fiber_list]

    def get_rasterized_mesh(self, coordinate_system: CoordinateSystem) -> np.ndarray:
        """
        Generate a rasterized mesh of the structure.

        Parameters
        ----------
        coordinate_system : CoordinateSystem
            The coordinate system to use.

        Returns
        -------
        numpy.ndarray
            The rasterized mesh.
        """
        return self.clad_structure.get_rasterized_mesh(coordinate_system=coordinate_system)

    def rotate(self, angle: float) -> "Profile":
        """
        Rotate the entire structure, including fiber cores.

        Returns
        -------
        Profile
            The updated Profile instance.
        """
        for fiber in self.fiber_list:
            fiber.rotate(angle, in_place=True)
            fiber.core.rotate(angle, in_place=True)
            fiber.shifted_core.rotate(angle, in_place=True)
            fiber.center.rotate(angle, in_place=True)

        self.clad_structure.rotate(angle, in_place=True)

        for element in self.removed_section_list:
            element.rotate(angle, in_place=True)

        for element in self.added_section_list:
            element.rotate(angle, in_place=True)

        return self

    def translate(self, shift: Tuple[float, float]) -> "Profile":
        """
        Translate the entire structure, including fiber cores.

        Returns
        -------
        Profile
            The updated Profile instance.
        """
        for fiber in self.fiber_list:
            fiber.translate(shift, in_place=True)
            fiber.core.translate(shift, in_place=True)
            fiber.shifted_core.translate(shift, in_place=True)
            fiber.center.translate(shift, in_place=True)

        self.clad_structure.translate(shift, in_place=True)

        for element in self.removed_section_list:
            element.translate(shift, in_place=True)

        for element in self.added_section_list:
            element.translate(shift, in_place=True)

        return self

    def scale_position(self, factor: float) -> "Profile":
        """
        Scale the positions of fibers in the structure.

        Parameters
        ----------
        factor : float
            Scaling factor for the positions.

        Returns
        -------
        Profile
            The updated Profile instance.
        """
        for fiber in self.fiber_list:
            fiber.scale_position(factor=factor)

        return self

    @property
    def removed_section(self) -> object:
        return union_geometries(*self.removed_section_list)

    @property
    def added_section(self) -> object:
        return union_geometries(*self.added_section_list)

    @_plot_helper
    def plot(
            self,
            ax: plt.Axis = None,
            show_structure: bool = True,
            show_centers: bool = False,
            show_cores: bool = True,
            show_added: bool = True,
            show_fibers: bool = False,
            show_removed: bool = True) -> None:
        """
        Plot the structure using matplotlib.

        Parameters
        ----------
        ax : matplotlib.axes.Axes
            The axis to render on.
        show_structure : bool, optional
            Whether to show the fused structure. Default is True.
        show_centers : bool, optional
            Whether to show the unfused fibers. Default is False.
        show_shifted_cores : bool, optional
            Whether to show the shifted cores. Default is True.
        show_added : bool, optional
            Whether to show added sections. Default is True.
        show_removed : bool, optional
            Whether to show removed sections. Default is True.
        """
        if show_structure:
            self.clad_structure.plot(ax, show=False)

        if show_fibers:
            for fiber in self.fiber_list:
                fiber.plot(ax, show=False)

        if show_added:
            self.added_section.plot(ax=ax, facecolor='green', show=False)

        if show_removed:
            self.removed_section.plot(ax=ax, facecolor='red', show=False)

        if show_cores:
            for idx, fiber in enumerate(self.fiber_list):
                fiber.shifted_core.plot(ax, marker='x', size=40, label=f'Core$_{idx}$', show=False)

        if show_centers:
            for idx, fiber in enumerate(self.fiber_list):
                fiber.center.plot(ax, marker='o', size=40, label=f'Center$_{idx}$', show=False)

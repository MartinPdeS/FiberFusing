#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import Union, Optional, List, Dict, Tuple
import matplotlib.pyplot as plt
import numpy as np
import logging
from dataclasses import dataclass
import shapely.geometry as geo
from FiberFusing.coordinate_system import CoordinateSystem
from FiberFusing.buffer import Circle
from FiberFusing.fiber_structure import FiberLine, FiberRing
from FiberFusing.utils import union_geometries
from FiberFusing.helper import _plot_helper, OverlayStructureBaseClass

logging.basicConfig(level=logging.INFO)


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


@dataclass
class BaseFused(OverlayStructureBaseClass):
    """
    Base class for managing the fusion of optical fiber structures, allowing customization of fiber properties
    and spatial configuration. This class facilitates the dynamic assembly of fiber optics structures and automates
    the overlay of these structures on a given mesh.

    Parameters
    ----------
    fiber_radius : float
        Radius of individual fibers in the structure.
    index : float
        Refractive index of the fibers' cladding.
    tolerance_factor : float, optional
        A tolerance value used in optimization algorithms to balance the area difference between added and removed
        sections during the fusion process. Default is 1e-2.
    fusion_degree : Union[float, str], optional
        Specifies the degree of fusion, ranging from 0 (no fusion) to 1 (full fusion), or 'auto' to automatically
        determine based on geometry. Default is 'auto'.
    core_position_scrambling : float, optional
        Introduces randomness to core positions to simulate practical imperfections. Default is 0.
    scale_down_position : float, optional
        Scaling factor to adjust the overall size of the assembly. Default is 1.
    """

    fiber_radius: float
    index: float
    tolerance_factor: Optional[float] = 1e-2
    fusion_degree: Optional[Union[float, str]] = 'auto'
    core_position_scrambling: Optional[float] = 0
    scale_down_position: Optional[float] = 1

    def __post_init__(self):
        """
        Initialize the fiber and core lists and other structures immediately after the dataclass fields
        have been populated.
        """
        self.fiber_list = []
        self.core_list = []
        self._clad_structure = None
        self.structure_list = []
        self.removed_section_list = []
        self.added_section_list = []

        self.compute_parametrized_fusion_degree()

    def compute_parametrized_fusion_degree(self) -> None:
        """
        Calculate and set the fusion degree adjusted to the specific requirements of the structure's geometry.

        If 'auto' is provided for fusion_degree, a default value is set based on the geometry's constraints.

        Returns
        -------
        None
        """
        if isinstance(self.fusion_degree, str) and self.fusion_degree.lower() == 'auto':
            self.fusion_degree = 0.8 if self.fusion_range is not None else None

        self.assert_fusion_degree()

        if self.fusion_degree is not None:
            self.parametrized_fusion_degree = (
                self.fusion_range[0] * (1 - self.fusion_degree) +
                self.fusion_degree * self.fusion_range[-1]
            )
        else:
            self.parametrized_fusion_degree = None

    def assert_fusion_degree(self) -> None:
        """
        Validate the fusion degree to ensure it lies within acceptable bounds.

        Raises
        ------
        ValueError
            If the fusion degree is not a scalar when required, or is out of the acceptable bounds [0, 1].
        TypeError
            If the fusion degree is required but None is provided.
        """
        if self.fusion_range is None:
            if self.fusion_degree is not None:
                raise ValueError(
                    f"This instance of {self.__class__.__name__} does not accept 'fusion_degree' as an argument."
                )
        else:
            if not np.isscalar(self.fusion_degree):
                raise TypeError(
                    f"Fusion degree [{self.fusion_degree}] must be a scalar value."
                )

            if not 0 <= self.fusion_degree <= 1:
                raise ValueError(
                    f"Fusion degree [{self.fusion_degree}] must be within the range [0, 1]."
                )

    @property
    def refractive_index_list(self) -> List[float]:
        """
        Get a list containing the refractive index of the fiber cladding.

        Returns
        -------
        List[float]
            A list with the cladding refractive index.
        """
        return [self.index]

    @property
    def is_multi(self) -> bool:
        """
        Check if the clad structure is a MultiPolygon.

        Returns
        -------
        bool
            True if the clad structure is a MultiPolygon, otherwise False.
        """
        return isinstance(self.clad_structure._shapely_object, geo.MultiPolygon)

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
            A dictionary with the structure's name, index, and polygon.
        """
        return {'name': {'index': self.index, 'polygon': self.clad_structure}}

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
        structure_list = [NameSpace(index=self.index, polygon=self.clad_structure)]
        return self._overlay_structure_on_mesh_(
            structure_list=structure_list, mesh=mesh, coordinate_system=coordinate_system
        )

    def get_shapely_object(self):
        """
        Get the Shapely object representing the clad structure.

        Returns
        -------
        shapely.geometry.BaseGeometry
            The Shapely object of the clad structure.
        """
        return self.clad_structure._shapely_object

    @property
    def bounds(self) -> Tuple[float, float, float, float]:
        """
        Get the boundaries of the clad structure.

        Returns
        -------
        tuple
            The bounding box of the clad structure.
        """
        return self.clad_structure.bounds

    def get_structure_max_min_boundaries(self) -> Tuple[float, float, float, float]:
        """
        Get the maximum and minimum boundaries of the clad structure.

        Returns
        -------
        tuple
            The bounding box of the clad structure.
        """
        return self.clad_structure.bounds

    @property
    def center(self) -> Tuple[float, float]:
        """
        Get the center of the clad structure.

        Returns
        -------
        tuple
            The center coordinates of the clad structure.
        """
        return self.clad_structure.center

    @property
    def fiber(self) -> List[Circle]:
        """
        Get a list of all fibers in the structure.

        Returns
        -------
        list
            A list of all fiber objects in the structure.
        """
        return self.fiber_list

    @property
    def cores(self) -> List[Tuple[float, float]]:
        """
        Get a list of core positions.

        Returns
        -------
        list
            A list of coordinates representing core positions.
        """
        return [fiber.core for fiber in self.fiber_list]

    def add_single_fiber(self, fiber_radius: float, position: Tuple[float, float] = (0, 0)) -> "BaseFused":
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
        BaseFused
            The updated BaseFused instance.
        """
        fiber = Circle(radius=fiber_radius, position=position)
        fiber.shifted_core = fiber.center

        self.structure_list.append(fiber)
        self.fiber_list.append(fiber)

        return self

    def add_center_fiber(self, fiber_radius: float) -> "BaseFused":
        """
        Add a single fiber at the center of the structure.

        Parameters
        ----------
        fiber_radius : float
            The radius of the fiber.

        Returns
        -------
        BaseFused
            The updated BaseFused instance.
        """
        return self.add_single_fiber(fiber_radius=fiber_radius, position=(0, 0))

    def add_center_structure(self, fiber_radius: float) -> "BaseFused":
        """
        Add a single structure of a given radius at the center of the structure.

        Parameters
        ----------
        fiber_radius : float
            The fiber radius.

        Returns
        -------
        BaseFused
            The updated BaseFused instance.
        """
        return self.add_single_fiber(fiber_radius=fiber_radius, position=(0, 0))

    def _add_structure_to_instance_(
        self,
        structure: Union[FiberRing, FiberLine],
        fusion_degree: float = 0.0,
        scale_position: float = 1.0,
        position_shift: List[float] = [0, 0],
        compute_fusing: bool = False
    ) -> "BaseFused":
        """
        Internal method to add a fiber structure to the instance.

        Parameters
        ----------
        structure : Union[FiberRing, FiberLine]
            The fiber structure to add.
        fusion_degree : float, optional
            The degree of fusion. Default is 0.0.
        scale_position : float, optional
            Factor to scale the position. Default is 1.0.
        position_shift : list of float, optional
            Shift vector for the position. Default is [0, 0].
        compute_fusing : bool, optional
            Whether to compute the fusing operation. Default is False.

        Returns
        -------
        BaseFused
            The updated BaseFused instance.
        """
        if compute_fusing:
            structure.set_fusion_degree(fusion_degree=fusion_degree)

        structure.scale_position(factor=scale_position)
        structure.shift_position(shift=position_shift)
        structure.initialize_cores()

        self.fiber_list.extend(structure.fiber_list)

        if compute_fusing:
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
        compute_fusing: bool = False,
        angle_shift: float = 0.0
    ) -> "BaseFused":
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
        compute_fusing : bool, optional
            Whether to compute the fusing operation for the structure. Default is False.
        angle_shift : float, optional
            The angle by which to rotate the structure. Default is 0.0.

        Returns
        -------
        BaseFused
            The updated BaseFused instance.
        """

        if structure_type.lower() == 'ring':
            structure = FiberRing(
                number_of_fibers=number_of_fibers,
                fiber_radius=fiber_radius,
                angle_shift=angle_shift
            )
        else:
            structure = FiberLine(
                number_of_fibers=number_of_fibers,
                fiber_radius=fiber_radius,
            )

        return self._add_structure_to_instance_(
            structure=structure,
            fusion_degree=fusion_degree,
            scale_position=scale_position,
            position_shift=position_shift,
            compute_fusing=compute_fusing
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

    def get_core_positions(self) -> List[Tuple[float, float]]:
        """
        Get a list of core positions for all fibers in the structure.

        Returns
        -------
        list of tuple
            A list of core positions.
        """
        return [fiber.core for fiber in self.fiber_list]

    def randomize_core_position(self, random_factor: float = 0) -> "BaseFused":
        """
        Randomize the position of fiber cores to simulate real-world imperfections.

        Parameters
        ----------
        random_factor : float, optional
            Factor determining the randomness in position. Default is 0.

        Returns
        -------
        BaseFused
            The updated BaseFused instance.
        """
        if random_factor == 0:
            return self

        logging.info("Randomizing core positions.")
        for fiber in self.fiber_list:
            random_shift = np.random.rand(2) * random_factor
            fiber.core.translate(random_shift, in_place=True)

        return self

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

    def rotate(self, *args, **kwargs) -> "BaseFused":
        """
        Rotate the entire structure, including fiber cores.

        Returns
        -------
        BaseFused
            The updated BaseFused instance.
        """
        for fiber in self.fiber_list:
            fiber.core.rotate(*args, **kwargs, in_place=True)

        self._clad_structure = self.clad_structure.rotate(*args, **kwargs)

        return self

    def shift(self, *args, **kwargs) -> "BaseFused":
        """
        Shift the entire structure, including fiber cores.

        Returns
        -------
        BaseFused
            The updated BaseFused instance.
        """
        for fiber in self.fiber_list:
            fiber.core.shift(*args, **kwargs, in_place=True)

        self._clad_structure = self.clad_structure.shift(*args, **kwargs)

        return self

    def scale_position(self, factor: float) -> "BaseFused":
        """
        Scale the positions of fibers in the structure.

        Parameters
        ----------
        factor : float
            Scaling factor for the positions.

        Returns
        -------
        BaseFused
            The updated BaseFused instance.
        """
        for fiber in self.fiber_list:
            fiber.scale_position(factor=factor)

        return self

    @_plot_helper
    def plot(
            self,
            ax: plt.Axis = None,
            show_structure: bool = True,
            show_centers: bool = False,
            show_cores: bool = True,
            show_added: bool = True,
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

        if show_added:
            added_section = union_geometries(*self.added_section_list)
            added_section.plot(ax=ax, facecolor='green', show=False)

        if show_removed:
            removed_section = union_geometries(*self.removed_section_list)
            removed_section.plot(ax=ax, facecolor='red', show=False)

        if show_cores:
            for idx, fiber in enumerate(self.fiber_list):
                fiber.shifted_core.plot(ax, marker='x', size=40, label=f'Core$_{idx}$', show=False)

        if show_centers:
            for idx, fiber in enumerate(self.fiber_list):
                fiber.center.plot(ax, marker='o', size=40, label=f'Center$_{idx}$', show=False)

        for fiber in self.fiber_list:
            fiber.plot(ax, show=False)

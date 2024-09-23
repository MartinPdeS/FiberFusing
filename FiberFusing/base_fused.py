#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import Union, Optional
import logging
from dataclasses import dataclass

# Third-party imports
import numpy
import shapely.geometry as geo

# Local imports
from FiberFusing import utils
from FiberFusing.utility.overlay_structure_on_mesh import OverlayStructureBaseClass
from FiberFusing.coordinate_system import CoordinateSystem
from FiberFusing.buffer import Circle
from FiberFusing.sub_structures.ring import FiberRing
from FiberFusing.sub_structures.line import FiberLine
import matplotlib.pyplot as plt
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
    Represents a base class for managing the fusion of optical fiber structures, allowing customization of fiber properties and spatial configuration. This class facilitates the dynamic assembly of fiber optics structures and automates the overlay of these structures on a given mesh.

    Attributes:
        fiber_radius (float): Radius of individual fibers in the structure.
        index (float): Refractive index of the fibers' cladding.
        tolerance_factor (float): A tolerance value used in optimization algorithms to balance the area difference between added and removed sections during the fusion process.
        fusion_degree (float | str): Specifies the degree of fusion, ranging from 0 (no fusion) to 1 (full fusion), or 'auto' to automatically determine based on geometry.
        core_position_scrambling (float): Introduces randomness to core positions to simulate practical imperfections.
        scale_down_position (float): Scaling factor to adjust the overall size of the assembly.
    """

    fiber_radius: float
    index: float
    tolerance_factor: Optional[float] = 1e-2
    fusion_degree: Optional[Union[float | str]] = 'auto'
    core_position_scrambling: Optional[float] = 0
    scale_down_position: Optional[float] = 1

    def __post_init__(self):
        """
        Initializes the fiber and core lists and any required structures immediately after the dataclass fields have been populated.
        """
        self.fiber_list = []
        self.core_list = []
        self._clad_structure = None
        self.structure_list = []
        self.removed_section_list = []
        self.added_section_list = []

        self.compute_parametrized_fusion_degree()

    def compute_parametrized_fusion_degree(self) -> float:
        """
        Calculates a fusion degree adjusted to the specific requirements of the structure's geometry.

        Returns:
            float: The adjusted fusion degree, mapping an abstract range [0, 1] to the actual usable range defined by the structure's physical constraints.
        """
        if str(self.fusion_degree).lower() == 'auto':
            self.fusion_degree = 0.8 if self.fusion_range is not None else None

        self.asserts_fusion_degree()

        if self.fusion_degree is not None:
            self.parametrized_fusion_degree = self.fusion_range[0] * (1 - self.fusion_degree) + self.fusion_degree * self.fusion_range[-1]
        else:
            self.parametrized_fusion_degree = None

    def asserts_fusion_degree(self) -> None:
        """
        Validates the fusion degree to ensure it lies within acceptable bounds.

        Raises:
            ValueError: If the fusion degree is not a scalar when required, or is out of the acceptable bounds [0, 1].
            TypeError: If the fusion degree is required but None is provided.
        """
        if self.fusion_range is None:
            if self.fusion_degree is not None:
                raise ValueError(f"This instance of {self.__class__.__name__} does not take 'fusion_degree' as an argument.")
        else:
            if not numpy.isscalar(self.fusion_degree):
                raise TypeError(f"Fusion degree: [{self.fusion_degree}] must be a scalar value.")

            if not 0 <= self.fusion_degree <= 1:
                raise ValueError(f"User provided fusion degree: {self.fusion_degree} must be in the range [0, 1].")

    @property
    def refractive_index_list(self) -> list[float]:
        """Return a list containing the refractive index of the fiber cladding."""
        return [self.index]

    @property
    def is_multi(self) -> bool:
        """Return True if the clad structure is a MultiPolygon."""
        return isinstance(self.clad_structure._shapely_object, geo.MultiPolygon)

    @property
    def clad_structure(self):
        """Return the clad structure, computing it if necessary."""
        if self._clad_structure is None:
            return utils.Union(*self.structure_list)
        return self._clad_structure

    @property
    def structure_dictionary(self) -> dict:
        """Return a dictionary representation of the structure."""
        return {'name': {'index': self.index, 'polygon': self.clad_structure}}

    def overlay_structures_on_mesh(self, mesh: numpy.ndarray, coordinate_system: CoordinateSystem) -> numpy.ndarray:
        """
        Apply the current fiber structure configuration onto a provided mesh.

        Parameters:
            mesh (numpy.ndarray): The mesh on which to overlay the structure.
            coordinate_system (CoordinateSystem): The coordinate system to use for the overlay.

        Returns:
            numpy.ndarray: The mesh with fiber structures overlaid.
        """
        structure_list = [NameSpace(index=self.index, polygon=self.clad_structure)]

        return self._overlay_structure_on_mesh_(
            structure_list=structure_list, mesh=mesh, coordinate_system=coordinate_system
        )

    def get_shapely_object(self):
        """Return the Shapely object representing the clad structure."""
        return self.clad_structure._shapely_object

    @property
    def bounds(self) -> tuple:
        """Return the boundaries of the clad structure."""
        return self.clad_structure.bounds

    def get_structure_max_min_boundaries(self) -> tuple:
        """Return the maximum and minimum boundaries of the clad structure."""
        return self.clad_structure.bounds

    @property
    def center(self):
        """Return the center of the clad structure."""
        return self.clad_structure.center

    @property
    def fiber(self) -> list:
        """Return a list of all fibers in the structure."""
        return self.fiber_list

    @property
    def cores(self) -> list:
        """Return a list of core positions."""
        return [fiber.core for fiber in self.fiber_list]

    def add_single_fiber(self, fiber_radius: float, position: tuple = (0, 0)) -> BaseFused:
        """
        Adds a single fiber to the structure at the specified position.

        Parameters:
            fiber_radius (float): The radius of the fiber to add.
            position (tuple, optional): The x, y coordinates for the fiber. Defaults to (0, 0).

        Returns:
            BaseFused: Returns the instance to allow for method chaining.
        """
        fiber = Circle(
            radius=fiber_radius,
            position=position
        )

        fiber.shifted_core = fiber.center

        self.structure_list.append(fiber)

        self.fiber_list.append(fiber)

        return self

    def add_single_fiber(self, fiber_radius: float, position: tuple = (0, 0)) -> BaseFused:
        """
        Add a single fiber to the structure at the specified position.

        Parameters:
            fiber_radius (float): The radius of the fiber.
            position (tuple): The x, y coordinates for the fiber. Defaults to (0, 0).

        Returns:
            BaseFused: The updated BaseFused instance.
        """
        fiber = Circle(radius=fiber_radius, position=position)
        fiber.shifted_core = fiber.center

        self.structure_list.append(fiber)
        self.fiber_list.append(fiber)

        return self

    def add_center_fiber(self, fiber_radius: float) -> BaseFused:
        """
        Add a single fiber at the center of the structure.

        Parameters:
            fiber_radius (float): The radius of the fiber.

        Returns:
            BaseFused: The updated BaseFused instance.
        """
        return self.add_single_fiber(fiber_radius=fiber_radius, position=(0, 0))


    def add_center_structure(self, fiber_radius: float) -> BaseFused:
        """
        Add a single structure of given radius at the center of the structure.

        :param      fiber_radius:  The fiber radius
        :type       fiber_radius:  float

        :returns:   The self instance
        :rtype:     BaseFused
        """
        return self.add_single_circle_structure(fiber_radius=fiber_radius, position=(0, 0))

    def _add_structure_to_instance_(
        self,
        structure: FiberRing | FiberLine,
        fusion_degree: float = 0.0,
        scale_position: float = 1.0,
        position_shift: list = [0, 0],
        compute_fusing: bool = False
    ) -> BaseFused:
        """
        Internal method to add a fiber structure to the instance.

        Parameters:
            structure (FiberRing | FiberLine): The fiber structure to add.
            fusion_degree (float): The degree of fusion.
            scale_position (float): Factor to scale the position.
            position_shift (list): Shift vector for the position.
            compute_fusing (bool): Whether to compute the fusing operation.

        Returns:
            BaseFused: The updated BaseFused instance.
        """
        if compute_fusing:
            structure.set_fusion_degree(fusion_degree=fusion_degree)

        structure.scale_position(factor=scale_position)
        structure.shift_position(shift=position_shift)
        structure.initialize_cores()

        self.fiber_list += structure.fiber_list

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
            position_shift: list = [0, 0],
            compute_fusing: bool = False,
            angle_shift: float = 0.0) -> BaseFused:
        """
        Adds a predefined structure of fibers, such as a ring or line, with customizable properties and spatial configuration.

        Parameters:
            structure_type (str): The type of structure to add ('ring' or 'line').
            number_of_fibers (int): Number of fibers in the structure.
            fiber_radius (float): Radius of each fiber in the structure.
            fusion_degree (float): The degree of fusion for this structure.
            scale_position (float): Factor to scale the position of each fiber.
            position_shift (list): A 2D vector [x, y] to shift the entire structure.
            compute_fusing (bool): Whether to compute the fusing operation for the structure.
            angle_shift (float): The angle by which to rotate the structure.

        Returns:
            BaseFused: Returns the instance to allow for method chaining.
        """
        match structure_type.lower():
            case 'ring':
                StructureClass = FiberRing
            case 'line':
                StructureClass = FiberRing

        structure = StructureClass(
            number_of_fibers=number_of_fibers,
            fiber_radius=fiber_radius,
            angle_shift=angle_shift
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

        Parameters:
            fibers: Custom fiber objects to be added.
        """
        self.fiber_list.extend(fibers)

    def get_core_positions(self) -> list:
        """
        Return a list of core positions for all fibers in the structure.

        Returns:
            list: A list of core positions.
        """
        return [fiber.core for fiber in self.fiber_list]

    def randomize_core_position(self, random_factor: float = 0) -> BaseFused:
        """
        Randomize the position of fiber cores to simulate real-world imperfections.

        Parameters:
            random_factor (float): Factor determining the randomness in position.

        Returns:
            BaseFused: The updated BaseFused instance.
        """
        if random_factor == 0:
            return self

        logging.info("Randomizing core positions.")

        for fiber in self.fiber_list:
            random_xy = numpy.random.rand(2) * random_factor
            fiber.core.translate(random_xy, in_place=True)

        return self

    def get_rasterized_mesh(self, coordinate_system: CoordinateSystem) -> numpy.ndarray:
        """
        Generate a rasterized mesh of the structure.

        Parameters:
            coordinate_system (CoordinateSystem): The coordinate system to use.

        Returns:
            numpy.ndarray: The rasterized mesh.
        """
        return self.clad_structure.get_rasterized_mesh(coordinate_system=coordinate_system)

    def rotate(self, *args, **kwargs) -> BaseFused:
        """
        Rotate the entire structure, including fiber cores.

        Returns:
            BaseFused: The updated BaseFused instance.
        """
        for fiber in self.fiber_list:
            fiber.core.rotate(*args, **kwargs, in_place=True)

        self._clad_structure = self.clad_structure.rotate(*args, **kwargs)

        return self

    def shift(self, *args, **kwargs) -> BaseFused:
        """
        Shift the entire structure, including fiber cores.

        Returns:
            BaseFused: The updated BaseFused instance.
        """
        for fiber in self.fiber_list:
            fiber.core.shift(*args, **kwargs, in_place=True)

        self._clad_structure = self.clad_structure.shift(*args, **kwargs)

        return self

    def scale_position(self, factor: float) -> BaseFused:
        """
        Scale the positions of fibers in the structure.

        Parameters:
            factor (float): Scaling factor for the positions.

        Returns:
            BaseFused: The updated BaseFused instance.
        """
        for fiber in self.fiber_list:
            fiber.scale_position(factor=factor)

        return self

    def format_ax(self, ax: plt.Axes) -> None:
        """
        Format the plot axes.

        Parameters:
            ax (plt.Axes): The axes to format.
        """
        ax.set(xlabel=r'x-distance [m]', ylabel=r'y-distance [m]')
        ax.ticklabel_format(axis='both', style='sci', scilimits=(-6, -6), useOffset=False)
        ax.set_aspect('equal')

    def plot(self, **kwargs) -> None:
        """
        Plot the structure using matplotlib.

        Parameters:
            kwargs: Additional keyword arguments for rendering.
        """
        figure, ax = plt.subplots(1, 1)
        self.format_ax(ax=ax)
        self.render_patch_on_ax(ax=ax, **kwargs)
        plt.show()

    def render_patch_on_ax(
        self,
        ax: plt.Axes,
        show_structure: bool = True,
        show_fibers: bool = False,
        show_shifted_cores: bool = True,
        show_added: bool = True,
        show_removed: bool = True
    ) -> None:
        """
        Render the structure's geometry on the given axis.

        Parameters:
            ax (plt.Axes): The axis to render on.
            show_structure (bool): Whether to show the fused structure.
            show_fibers (bool): Whether to show the unfused fibers.
            show_shifted_cores (bool): Whether to show the shifted cores.
            show_added (bool): Whether to show added sections.
            show_removed (bool): Whether to show removed sections.
        """
        if show_structure:
            self.clad_structure._render_on_ax_(ax)

        if show_added:
            added_section = utils.Union(*self.added_section_list)
            added_section._render_on_ax_(ax=ax, facecolor='green', label='added section')

        if show_removed:
            removed_section = utils.Union(*self.removed_section_list)
            removed_section._render_on_ax_(ax=ax, facecolor='red', label='removed section')

        if show_fibers:
            for fiber in self.fiber_list:
                fiber._render_on_ax_(ax)
                fiber.center._render_on_ax_(ax, marker='o', s=40, label='core')

        if show_shifted_cores:
            for fiber in self.fiber_list:
                fiber.shifted_core.render_on_axis(ax, marker='x', s=40, label='shifted core')

#  -

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
from MPSPlots.render2D import Axis, SceneList
from FiberFusing import utils
from FiberFusing.utility.overlay_structure_on_mesh import OverlayStructureBaseClass
from FiberFusing.coordinate_system import CoordinateSystem
from FiberFusing.buffer import Circle
from FiberFusing.sub_structures.ring import FiberRing
from FiberFusing.sub_structures.line import FiberLine

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
        return [self.index]

    @property
    def is_multi(self) -> bool:
        return isinstance(self.clad_structure._shapely_object, geo.MultiPolygon)

    @property
    def clad_structure(self):
        if self._clad_structure is None:
            return utils.Union(*self.structure_list)
        else:
            return self._clad_structure

    @property
    def structure_dictionary(self) -> dict:
        return {'name': {'index': self.index, 'polygon': self.clad_structure}}

    def overlay_structures_on_mesh(self, mesh: numpy.ndarray, coordinate_system: CoordinateSystem) -> numpy.ndarray:
        """
        Applies the current fiber structure configuration onto a provided mesh, considering the specified coordinate system.

        Parameters:
            mesh (numpy.ndarray): The mesh on which to overlay the structure.
            coordinate_system (CoordinateSystem): The coordinate system to use for the overlay.

        Returns:
            numpy.ndarray: A mesh with the fiber structures applied.
        """
        structure_list = [
            NameSpace(index=self.index, polygon=self.clad_structure)
        ]

        return self._overlay_structure_on_mesh_(
            structure_list=structure_list,
            mesh=mesh,
            coordinate_system=coordinate_system
        )

    def get_shapely_object(self):
        return self.clad_structure._shapely_object

    @property
    def bounds(self) -> tuple:
        """
        Return the boundaries of the structure.
        """
        return self.clad_structure.bounds

    @property
    def boundaries(self) -> tuple:
        """
        Return the boundaries of the structure.
        """
        return self.clad_structure.bounds

    def get_structure_max_min_boundaries(self) -> tuple:
        return self.clad_structure.bounds

    @property
    def center(self):
        return self.clad_structure.center

    @property
    def fiber(self) -> list:
        """
        Return list of all the fiber in the structure

        :returns:   List of the structure fiber components
        :rtype:     list
        """
        return self.fiber_list

    @property
    def cores(self) -> list:
        """
        Return a list of the cores

        :returns:   List of the cores
        :rtype:     list
        """
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

    def add_single_circle_structure(self, fiber_radius: float, position: tuple = (0, 0)) -> BaseFused:
        """
        Adds a single structure.

        :param      fiber_radius:  The fiber radius
        :type       fiber_radius:  float
        :param      position:      The position
        :type       position:      tuple

        :returns:   The self instance
        :rtype:     BaseFused
        """
        fiber = Circle(
            radius=fiber_radius,
            position=position
        )

        self.structure_list.append(fiber)

        return self

    def add_center_fiber(self, fiber_radius: float) -> BaseFused:
        """
        Add a single fiber of given radius at the center of the structure.

        :param      fiber_radius:  The fiber radius
        :type       fiber_radius:  float

        :returns:   The self instance
        :rtype:     BaseFused
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
            compute_fusing: bool = False) -> BaseFused:

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
        Add any custom defined fiber

        :param      fibers:  The custom fibers
        :type       fibers:  list
        """
        for fiber in fibers:
            self.fiber_list.append(fiber)

    def get_core_positions(self) -> list:
        """
        Return a list of the core positions

        :returns:   The core positions.
        :rtype:     list
        """
        return [fiber.core for fiber in self.fiber_list]

    def randomize_core_position(self, random_factor: float = 0) -> BaseFused:
        """
        Shuffle the position of the fiber cores.
        It can be used to add realism to the fusion process.

        :param      random_factor:  The randomize position
        :type       random_factor:  float

        :returns:   The self instance
        :rtype:     BaseFused
        """
        if random_factor == 0:
            return

        logging.info("Randomizing the core positions")

        if random_factor != 0:
            for fiber in self.fiber_list:
                random_xy = numpy.random.rand(2) * random_factor
                fiber.core.translate(random_xy, in_place=True)

        return self

    def get_rasterized_mesh(self, coordinate_system: CoordinateSystem) -> numpy.ndarray:
        return self.clad_structure.get_rasterized_mesh(coordinate_system=coordinate_system)

    def rotate(self, *args, **kwargs) -> BaseFused:
        """
        Rotates the full structure, including the fiber cores.

        :returns:   The self instance
        :rtype:     BaseFused
        """
        for fiber in self.fiber_list:
            fiber.core.rotate(*args, **kwargs, in_place=True)

        self._clad_structure = self.clad_structure.rotate(*args, **kwargs)

        return self

    def shift(self, *args, **kwargs) -> BaseFused:
        """
        Rotates the full structure, including the fiber cores.

        :returns:   The self instance
        :rtype:     BaseFused
        """
        for fiber in self.fiber_list:
            fiber.core.shift(*args, **kwargs, in_place=True)

        self._clad_structure = self.clad_structure.shift(*args, **kwargs)

        return self

    def scale_position(self, factor: float) -> BaseFused:
        """
        Scale down the distance between each cores.

        :param      factor:  The scaling factor
        :type       factor:  float

        :returns:   The self instance
        :rtype:     BaseFused
        """
        for fiber in self.fiber_list:
            fiber.scale_position(factor=factor)

        return self

    def plot(self, **kwargs) -> SceneList:

        figure = SceneList(unit_size=(6, 6))

        ax = figure.append_ax(
            x_label=r'x',
            y_label=r'y',
            show_grid=True,
            equal_limits=True,
            show_legend=True,
        )

        self.render_patch_on_ax(ax=ax, **kwargs)

        return figure

    def render_patch_on_ax(
            self,
            ax: Axis,
            show_structure: bool = True,
            show_fibers: bool = False,
            show_shifted_cores: bool = True,
            show_added: bool = True,
            show_removed: bool = True) -> None:
        """
        Add the geometry patches to the axis.
        Base patch is the clad representation.
        The boolean paraemters defines which other patch is added
        to the ax.

        :param      ax:                  The axis to which add the patches
        :type       ax:                  Axis
        :param      show_structure:      Added the fused structure to ax
        :type       show_structure:      bool
        :param      show_fibers:         Added the unfused fibers to ax
        :type       show_fibers:         bool
        :param      show_shifted_cores:  Added the shifted cores to ax
        :type       show_shifted_cores:  bool
        :param      show_added:          Added the added section to ax
        :type       show_added:          bool
        :param      show_removed:        Added the removed section to ax
        :type       show_removed:        bool

        :returns:   The scene list.
        :rtype:     SceneList
        """
        if show_structure:
            self.clad_structure._render_on_ax_(ax)

        ax.set_style(
            x_label=r'x-distance [$\mu$m]',
            y_label=r'y-distance [$\mu$m]',
            x_scale_factor=1e6,
            y_scale_factor=1e6,
            equal_limits=True,
        )

        if show_added:
            added_section = utils.Union(*self.added_section_list)
            added_section._render_on_ax_(ax=ax, facecolor='green', label='added section')

        # if show_removed:
        #     removed_section = utils.Union(*self.removed_section_list)
        #     removed_section._render_on_ax_(ax=ax, facecolor='red', label='removed section')

        # if show_fibers:
        #     for n, fiber in enumerate(self.fiber_list):
        #         fiber._render_on_ax_(ax)
        #         fiber.center._render_on_ax_(
        #             ax,
        #             marker='o',
        #             marker_size=40,
        #             label='core',
        #         )

        # if show_shifted_cores:
        #     for n, fiber in enumerate(self.fiber_list):
        #         fiber.shifted_core.render_on_axis(
        #             ax,
        #             marker='x',
        #             marker_size=40,
        #             edge_color=None,
        #             label='shifted core',
        #         )

#  -

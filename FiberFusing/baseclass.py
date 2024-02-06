#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Built-in imports
from typing import Self
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
from FiberFusing.tools import plot_style

logging.basicConfig(level=logging.INFO)


class NameSpace():
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


@dataclass
class BaseFused(OverlayStructureBaseClass):
    fiber_radius: float
    """ Radius of the fiber in the assembly """
    index: float
    """ Refractive index of the cladding structure. """
    tolerance_factor: float = 1e-2
    """ Tolerance on the optimization problem which aim to minimize the difference between added and removed area of the heuristic algorithm. """
    fusion_degree: float | str = 'auto'
    """ Fusion degree of the assembly must be within [0, 1] """
    core_position_scrambling: float = 0
    """ Scrambling value of the core positions """
    scale_down_position: float = 1
    """ Factor to scale down the whole assembly """

    def __post_init__(self):
        self.fiber_list = []
        self.core_list = []
        self._clad_structure = None
        self.structure_list = []
        self.removed_section_list = []
        self.added_section_list = []

        self.compute_parametrized_fusion_degree()

    def compute_parametrized_fusion_degree(self) -> float:
        """
        Calculates the parametrized fusion degree which maps a value from 0 to 1 into
        a value between the fusion range of the specific geometry.

        :returns:   The parametrized fusion degree.
        :rtype:     float
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
        Asserts the possible values of the fusion degree

        :returns:   No return
        :rtype:     None
        """
        if self.fusion_range is None:
            assert self.fusion_degree is None, f"This instance: {self.__class__} do not take fusion_degree as argument."
        else:
            assert numpy.isscalar(self.fusion_degree), f"Fusion degree: [{self.fusion_degree}] has te be a scalar value."

        if numpy.isscalar(self.fusion_degree):
            assert 0 <= self.fusion_degree <= 1, f"User provided fusion degree: {self.fusion_degree} has to be in the range [0, 1]"

    @property
    def refractive_index_list(self) -> list:
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
        return {
            'name': {
                'index': self.index,
                'polygon': self.clad_structure
            }
        }

    def overlay_structures_on_mesh(self, mesh: numpy.ndarray, coordinate_system: CoordinateSystem) -> numpy.ndarray:
        """
        Return a mesh overlaying all the structures in the order they were defined.

        :param      coordinate_system:  The coordinates axis
        :type       coordinate_system:  CoordinateSystem

        :returns:   The raster mesh of the structures.
        :rtype:     numpy.ndarray
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

    def add_single_fiber(self, fiber_radius: float, position: tuple = (0, 0)) -> Self:
        """
        Adds a single fiber.

        :param      fiber_radius:  The fiber radius
        :type       fiber_radius:  float
        :param      position:      The position
        :type       position:      tuple

        :returns:   The self instance
        :rtype:     Self
        """
        fiber = Circle(
            radius=fiber_radius,
            position=position
        )

        fiber.shifted_core = fiber.center

        self.structure_list.append(fiber)

        self.fiber_list.append(fiber)

        return self

    def add_single_circle_structure(self, fiber_radius: float, position: tuple = (0, 0)) -> Self:
        """
        Adds a single structure.

        :param      fiber_radius:  The fiber radius
        :type       fiber_radius:  float
        :param      position:      The position
        :type       position:      tuple

        :returns:   The self instance
        :rtype:     Self
        """
        fiber = Circle(
            radius=fiber_radius,
            position=position
        )

        self.structure_list.append(fiber)

        return self

    def add_center_fiber(self, fiber_radius: float) -> Self:
        """
        Add a single fiber of given radius at the center of the structure.

        :param      fiber_radius:  The fiber radius
        :type       fiber_radius:  float

        :returns:   The self instance
        :rtype:     Self
        """
        return self.add_single_fiber(fiber_radius=fiber_radius, position=(0, 0))

    def add_center_structure(self, fiber_radius: float) -> Self:
        """
        Add a single structure of given radius at the center of the structure.

        :param      fiber_radius:  The fiber radius
        :type       fiber_radius:  float

        :returns:   The self instance
        :rtype:     Self
        """
        return self.add_single_circle_structure(fiber_radius=fiber_radius, position=(0, 0))

    def _add_structure_to_instance_(
            self,
            structure: FiberRing | FiberLine,
            fusion_degree: float = 0.0,
            scale_position: float = 1.0,
            position_shift: list = [0, 0],
            compute_fusing: bool = False) -> Self:

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
            angle_shift: float = 0.0) -> Self:
        """
        Add a ring of equi-distant and same radius fiber with a given
        radius and degree of fusion

        :param      structure_type:    The structure type
        :type       structure_type:    str
        :param      number_of_fibers:  The number of fibers in the structure
        :type       number_of_fibers:  int
        :param      fusion_degree:     The fusion degree for the structure
        :type       fusion_degree:     float
        :param      fiber_radius:      The fiber radius
        :type       fiber_radius:      float
        :param      angle_shift:       The angle shift
        :type       angle_shift:       float
        :param      compute_fusing:    If set to True the computation of the fusion process will be executed
        :type       compute_fusing:    bool

        :returns:   The self instance
        :rtype:     Self
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

    def randomize_core_position(self, random_factor: float = 0) -> Self:
        """
        Shuffle the position of the fiber cores.
        It can be used to add realism to the fusion process.

        :param      random_factor:  The randomize position
        :type       random_factor:  float

        :returns:   The self instance
        :rtype:     Self
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

    def rotate(self, *args, **kwargs) -> Self:
        """
        Rotates the full structure, including the fiber cores.

        :returns:   The self instance
        :rtype:     Self
        """
        for fiber in self.fiber_list:
            fiber.core.rotate(*args, **kwargs, in_place=True)

        self._clad_structure = self.clad_structure.rotate(*args, **kwargs)

        return self

    def shift(self, *args, **kwargs) -> Self:
        """
        Rotates the full structure, including the fiber cores.

        :returns:   The self instance
        :rtype:     Self
        """
        for fiber in self.fiber_list:
            fiber.core.shift(*args, **kwargs, in_place=True)

        self._clad_structure = self.clad_structure.shift(*args, **kwargs)

        return self

    def scale_position(self, factor: float) -> Self:
        """
        Scale down the distance between each cores.

        :param      factor:  The scaling factor
        :type       factor:  float

        :returns:   The self instance
        :rtype:     Self
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

        ax.set_style(**plot_style.geometry)

        if show_added:
            added_section = utils.Union(*self.added_section_list)
            added_section._render_on_ax_(ax=ax, facecolor='green', label='added section')

        if show_removed:
            removed_section = utils.Union(*self.removed_section_list)
            removed_section._render_on_ax_(ax=ax, facecolor='red', label='removed section')

        if show_fibers:
            for n, fiber in enumerate(self.fiber_list):
                fiber._render_on_ax_(ax)
                fiber.center._render_on_ax_(
                    ax,
                    marker='o',
                    marker_size=40,
                    label='core',
                )

        if show_shifted_cores:
            for n, fiber in enumerate(self.fiber_list):
                fiber.shifted_core._render_on_ax_(
                    ax,
                    marker='x',
                    marker_size=40,
                    edge_color=None,
                    label='shifted core',
                )

#  -

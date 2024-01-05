#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Built-in imports
import logging
from dataclasses import dataclass

# Third-party imports
import numpy
import shapely.geometry as geo

# Local imports
from MPSPlots.render2D import Axis, SceneList
from FiberFusing import utils
from FiberFusing.utility.connection_optimization import ConnectionOptimization
from FiberFusing.utility.overlay_structure_on_mesh import OverlayStructureBaseClass
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
class BaseFused(ConnectionOptimization, OverlayStructureBaseClass):
    index: float
    """ Refractive index of the cladding structure. """
    tolerance_factor: float = 1e-2
    """ Tolerance on the optimization problem which aim to minimize the difference between added and removed area of the heuristic algorithm. """
    fusion_degree: float = None

    def __post_init__(self):
        self.fiber_list = []
        self.core_list = []
        self._clad_structure = None
        self.structure_list = []
        self.removed_section_list = []
        self.added_section_list = []

        if self.fusion_range is None:
            if self.fusion_degree is not None:
                logging.warning(f"This instance: {self.__class__} do not take fusion_degree as argument.")
        else:
            assert self.fusion_range[0] <= self.fusion_degree <= self.fusion_range[1], f"User provided fusion degree: {self.fusion_degree} has to be in the range {self.fusion_range}"

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

    def overlay_structures_on_mesh(self, mesh: numpy.ndarray, coordinate_system: Axis) -> numpy.ndarray:
        """
        Return a mesh overlaying all the structures in the order they were defined.

        :param      coordinate_system:  The coordinates axis
        :type       coordinate_system:  Axis

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
        return [fiber.core for fiber in self.fiber_list]

    def add_single_fiber(self, fiber_radius: float, position: tuple = (0, 0)) -> None:
        """
        Adds a single fiber.

        :param      fiber_radius:  The fiber radius
        :type       fiber_radius:  float
        :param      position:      The position
        :type       position:      tuple

        :returns:   No returns
        :rtype:     None
        """
        fiber = Circle(
            radius=fiber_radius,
            position=position
        )

        fiber.shifted_core = fiber.center

        self.structure_list.append(fiber)

        self.fiber_list.append(fiber)

    def add_single_circle_structure(self, fiber_radius: float, position: tuple = (0, 0)) -> None:
        """
        Adds a single structure.

        :param      fiber_radius:  The fiber radius
        :type       fiber_radius:  float
        :param      position:      The position
        :type       position:      tuple

        :returns:   No returns
        :rtype:     None
        """
        fiber = Circle(
            radius=fiber_radius,
            position=position
        )

        self.structure_list.append(fiber)

    def add_center_fiber(self, fiber_radius: float) -> None:
        """
        Add a single fiber of given radius at the center of the structure.

        :param      fiber_radius:  The fiber radius
        :type       fiber_radius:  float

        :returns:   No returns
        :rtype:     None
        """
        return self.add_single_fiber(fiber_radius=fiber_radius, position=(0, 0))

    def add_center_structure(self, fiber_radius: float) -> None:
        """
        Add a single structure of given radius at the center of the structure.

        :param      fiber_radius:  The fiber radius
        :type       fiber_radius:  float

        :returns:   No returns
        :rtype:     None
        """
        return self.add_single_circle_structure(fiber_radius=fiber_radius, position=(0, 0))

    def add_fiber_ring(self,
            number_of_fibers: int,
            fiber_radius: float,
            fusion_degree: float = 0.0,
            scale_position: float = 1.0,
            position_shift: list = [0, 0],
            compute_fusing: bool = False,
            angle_shift: float = 0.0) -> None:
        """
        Add a ring of equi-distant and same radius fiber with a given
        radius and degree of fusion

        :param      number_of_fibers:  The number of fibers in the ring
        :type       number_of_fibers:  int
        :param      fusion_degree:     The fusion degree for that ring
        :type       fusion_degree:     float
        :param      fiber_radius:      The fiber radius
        :type       fiber_radius:      float
        """
        ring = FiberRing(
            number_of_fibers=number_of_fibers,
            fiber_radius=fiber_radius,
            angle_shift=angle_shift
        )

        ring.set_fusion_degree(fusion_degree=fusion_degree)
        ring.scale_position(factor=scale_position)
        ring.shift_position(shift=position_shift)
        ring.initialize_cores()

        self.fiber_list += ring.fiber_list

        if compute_fusing:
            ring.init_connected_fibers()
            ring.compute_optimal_structure()
            self.removed_section_list.append(ring.removed_section)
            self.added_section_list.append(ring.added_section)
            self.structure_list.append(ring.fused_structure)

        else:
            self.structure_list.append(ring.unfused_structure)

    def add_fiber_line(self,
            number_of_fibers: int,
            fiber_radius: float,
            fusion_degree: float = 0.0,
            scale_position: float = 1.0,
            position_shift: list = [0, 0],
            compute_fusing: bool = False,
            rotation_angle: float = 0.0) -> None:
        """
        Add a ring of equi-distant and same radius fiber with a given
        radius and degree of fusion

        :param      number_of_fibers:  The number of fibers in the line
        :type       number_of_fibers:  int
        :param      fusion_degree:     The fusion degree for that line
        :type       fusion_degree:     float
        :param      fiber_radius:      The fiber radius
        :type       fiber_radius:      float
        """
        line = FiberLine(
            number_of_fibers=number_of_fibers,
            fiber_radius=fiber_radius,
            rotation_angle=rotation_angle
        )

        line.set_fusion_degree(fusion_degree=fusion_degree)
        line.scale_position(factor=scale_position)
        line.shift_position(shift=position_shift)
        line.initialize_cores()

        self.fiber_list += line.fiber_list

        if compute_fusing:
            line.init_connected_fibers()
            line.compute_optimal_structure()
            self.removed_section_list.append(line.removed_section)
            self.added_section_list.append(line.added_section)
            self.structure_list.append(line.fused_structure)

        else:
            self.structure_list.append(line.unfused_structure)

    def add_custom_fiber(self, *fibers) -> None:
        """
        Add any custom defined fiber

        :param      fibers:  The custom fibers
        :type       fibers:  list
        """
        for fiber in fibers:
            self.fiber_list.append(fiber)

    def get_core_positions(self) -> list:
        return [fiber.core for fiber in self.fiber_list]

    def randomize_core_position(self, randomize_position: float = 0) -> None:
        """
        Shuffle the position of the fiber cores.
        It can be used to add realism to the fusion process.
        """
        if randomize_position == 0:
            return

        logging.info("Randomizing the core positions")

        if randomize_position != 0:
            for fiber in self.fiber_list:
                random_xy = numpy.random.rand(2) * randomize_position
                fiber.core.translate(random_xy, in_place=True)

    def get_rasterized_mesh(self, coordinate_system: Axis) -> numpy.ndarray:
        return self.clad_structure.get_rasterized_mesh(coordinate_system=coordinate_system)

    def rotate(self, *args, **kwargs):
        """
        Rotates the full structure, including the fiber cores.
        """
        for fiber in self.fiber_list:
            fiber.core.rotate(*args, **kwargs, in_place=True)

        self._clad_structure = self.clad_structure.rotate(*args, **kwargs)

    def shift(self, *args, **kwargs):
        """
        Rotates the full structure, including the fiber cores.
        """
        for fiber in self.fiber_list:
            fiber.core.shift(*args, **kwargs, in_place=True)

        self._clad_structure = self.clad_structure.shift(*args, **kwargs)

    def scale_position(self, factor: float) -> None:
        """
        Scale down the distance between each cores.

        :param      factor:  The scaling factor
        :type       factor:  float
        """
        for fiber in self.fiber_list:
            fiber.scale_position(factor=factor)

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

import numpy
from dataclasses import dataclass
from FiberFusing.buffer import Circle
from FiberFusing import utils
import FiberFusing as ff
from FiberFusing.connection_optimization import ConnectionOptimization


class BaseClass:
    """
    Base class for managing and visualizing fused and unfused fiber structures.

    This class provides methods for initializing fiber cores, setting fusion degrees, scaling,
    shifting, and visualizing the fiber structures.

    Attributes
    ----------
    fiber_radius : float
        Radius of individual fibers in the structure.
    fiber_list : list
        List of fiber objects (instances of Circle).
    added_section : object
        Section added during the fusion process.
    connected_fibers : list
        List of connected fiber objects during fusion.
    """

    @property
    def fused_structure(self):
        """
        Get the fused structure combining all fibers and added sections.

        Returns
        -------
        shapely.geometry.Polygon
            The union of all fibers and the added section.
        """
        return utils.union_geometries(*self.fiber_list, self.added_section)

    @property
    def unfused_structure(self):
        """
        Get the unfused structure combining all fibers.

        Returns
        -------
        shapely.geometry.Polygon
            The union of all fibers without any fusion applied.
        """
        return utils.union_geometries(*self.fiber_list)

    def initialize_cores(self) -> None:
        """
        Initialize the core positions for all fibers by setting their shifted core positions.
        """
        for fiber in self.fiber_list:
            fiber.shifted_core = fiber.center

    def get_scaling_factor_from_fusion_degree(self, fusion_degree: float) -> float:
        """
        Calculate the scaling factor from the fusion degree.

        Parameters
        ----------
        fusion_degree : float
            The fusion degree, ranging from 0 to 1.

        Returns
        -------
        float
            The calculated scaling factor based on the fusion degree.
        """
        factor = 1 - fusion_degree * (2 - numpy.sqrt(2))
        distance_between_cores = 2 * self.fiber_radius * factor
        scaling_factor = distance_between_cores / (2 * self.fiber_radius)
        return scaling_factor

    def set_fusion_degree(self, fusion_degree: float) -> None:
        """
        Adjust the fiber positions according to the specified fusion degree.

        The method scales the fiber positions based on the fusion degree, as described
        in Suzanne Lacroix's article: "Modeling of symmetric 2 x 2 fused-fiber couplers."

        Parameters
        ----------
        fusion_degree : float
            The fusion degree of the structure, where 0 means no fusion and 1 means full fusion.
        """
        scaling_factor = self.get_scaling_factor_from_fusion_degree(fusion_degree)
        self.scale_position(factor=scaling_factor)

    def scale_position(self, factor: float) -> None:
        """
        Scale the distance between fiber cores by the given factor.

        Parameters
        ----------
        factor : float
            The scaling factor to adjust the positions.
        """
        for fiber in self.fiber_list:
            fiber.scale_position(factor=factor)

    def shift_position(self, shift: list) -> None:
        """
        Shift the fiber cores by a specified vector.

        Parameters
        ----------
        shift : list of float
            A 2D shift vector [x, y] to translate the fiber cores.
        """
        for fiber in self.fiber_list:
            fiber.shift_position(shift=shift)

    def compute_fiber_list(self, centers: list) -> None:
        """
        Compute and initialize the list of fibers based on their center positions.

        Parameters
        ----------
        centers : list of Point
            List of center positions for the fibers.
        """
        self.fiber_list = [
            Circle(radius=self.fiber_radius, position=(point.x, point.y))
            for point in centers
        ]


@dataclass
class FiberLine(ConnectionOptimization, BaseClass):
    number_of_fibers: int
    """ Number of fiber in the ring """
    fiber_radius: float
    """ Radius of the radius of the rings, same for every ringe here """
    rotation_angle: float = 0
    """ Shift angle for the ring configuration """
    tolerance_factor: float = 1e-10

    def __post_init__(self):
        core_positions = self.compute_unfused_positions()

        self.compute_fiber_list(centers=core_positions)

    def compute_unfused_positions(self) -> list:
        """
        Computing the core center with a a certain distance from the origin  (0, 0).

        :param      distance_from_center:  The distance from center
        :type       distance_from_center:  float
        """

        core_positions = numpy.arange(self.number_of_fibers).astype(float)

        core_positions -= core_positions.mean()

        core_positions *= 2 * self.fiber_radius

        rotation_angle = numpy.deg2rad(self.rotation_angle)

        core_positions = [
            (numpy.cos(rotation_angle) * pos, numpy.sin(rotation_angle) * pos) for pos in core_positions
        ]

        core_positions = [
            ff.Point(position=position) for position in core_positions
        ]

        return core_positions


@dataclass
class FiberRing(ConnectionOptimization, BaseClass):
    number_of_fibers: int
    """ Number of fiber in the ring """
    fiber_radius: float
    """ Radius of the radius of the rings, same for every ringe here """
    angle_shift: float = 0
    """ Shift angle for the ring configuration """
    tolerance_factor: float = 1e-10

    def __post_init__(self):
        self.angle_list = numpy.linspace(0, 360, self.number_of_fibers, endpoint=False)
        self.angle_list += self.angle_shift
        self.delta_angle = (self.angle_list[1] - self.angle_list[0])

        centers = self.compute_unfused_positions(distance_from_center="not-fused")
        self.compute_fiber_list(centers=centers)

    def compute_unfused_positions(self, distance_from_center="not-fused") -> list:
        """
        Computing the core center with a a certain distance from the origin  (0, 0).

        :param      distance_from_center:  The distance from center
        :type       distance_from_center:  float
        """

        factor = numpy.sqrt(2 / (1 - numpy.cos(numpy.deg2rad(self.delta_angle))))

        distance_from_center = factor * self.fiber_radius

        first_core = ff.Point(position=[0, distance_from_center])

        core_position = [
            first_core.rotate(angle=angle, origin=[0, 0]) for angle in self.angle_list
        ]

        return core_position

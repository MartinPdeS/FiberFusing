from .geometry import Geometry  # noqa: F401
from .components.point import Point  # noqa: F401
from .components.linestring import LineString  # noqa: F401
from .components.polygon import Polygon, EmptyPolygon  # noqa: F401
from .buffer import Circle, Square  # noqa: F401
from .background import BackGround  # noqa: F401
from pydantic.dataclasses import dataclass
from pydantic import ConfigDict

from typing import Optional, Tuple
import numpy

micro = 1e-6


@dataclass(config=ConfigDict(extra='forbid'), kw_only=True)
class CircleOpticalStructure():
    """
    Initialize a CircleOpticalStructure instance.

    Args:
        name (str): Name of the structure.
        index (float): Refractive index of the structure.
        radius (float): Radius of the circle representing the slice of the structure.
        position (Tuple[float, float]): Center position of the circle.
        is_graded (Optional[bool], optional): True if the structure has a graded refractive index. Defaults to False.
        delta_n (Optional[float], optional): Delta refractive index of the grading. Defaults to None.
    """
    name: str
    index: float
    radius: float
    position: Tuple[float, float]
    is_graded: Optional[bool] = False
    delta_n: Optional[float] = None

    def __post_init__(self) -> None:
        self.polygon = Circle(position=self.position, radius=self.radius)

    def compute_index_from_NA(self, NA: float, exterior_index: float) -> float:
        """
        Compute the refractive index from the numerical aperture (NA).

        Args:
            NA (float): Numerical aperture.
            exterior_index (float): Refractive index of the exterior structure.

        Returns:
            float: Computed refractive index.
        """
        return numpy.sqrt(NA**2 + exterior_index**2)

    def get_V_number(self, wavelength: float) -> float:
        """
        Compute the V-number for the optical structure.

        Args:
            wavelength (float): Wavelength of the light.

        Returns:
            float: Computed V-number.
        """
        delta_index = numpy.sqrt(self.index**2 - self.exterior_structure.index**2)

        V = 2 * numpy.pi / wavelength * delta_index * self.radius

        return V

    def scale(self, factor: float) -> None:
        """
        Scale the radius of the optical structure by a given factor.

        Args:
            factor (float): Scaling factor.
        """
        self.radius *= factor
        self.__post_init__()


# -

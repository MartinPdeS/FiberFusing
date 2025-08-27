from .geometry import Geometry  # noqa: F401
from .geometries import Point, LineString, Polygon, EmptyPolygon  # noqa: F401
from .shapes import Circle, Square, Ellipse  # noqa: F401
from .background import BackGround  # noqa: F401
from pydantic.dataclasses import dataclass
from pydantic import ConfigDict
from FiberFusing.graded_index import GradedIndex

from typing import Optional, Tuple
import numpy as np


@dataclass(config=ConfigDict(extra='forbid', kw_only=True))
class CircleOpticalStructure:
    """
    Represents a circular optical structure.

    Attributes
    ----------
    name : str
        Name of the structure.
    refractive_index : float | GradedIndex
        Refractive index of the structure.
    radius : float
        Radius of the circle representing the structure.
    position : Tuple[float, float]
        Center position of the circle.
    """

    name: str
    radius: float
    position: Tuple[float, float]
    refractive_index: float | GradedIndex = None

    def __post_init__(self) -> None:
        """
        Initialize the circular polygon representation of the structure.
        """
        self.polygon = Circle(position=self.position, radius=self.radius)

    def compute_refractive_index_from_NA(self, NA: float, exterior_index: float) -> float:
        """
        Compute the refractive index from the numerical aperture (NA).

        Parameters
        ----------
        NA : float
            Numerical aperture.
        exterior_index : float
            Refractive index of the exterior structure.

        Returns
        -------
        float
            Computed refractive index.
        """
        return np.sqrt(NA**2 + exterior_index**2)

    def get_V_number(self, wavelength: float, exterior_index: float) -> float:
        """
        Compute the V-number for the optical structure.

        Parameters
        ----------
        wavelength : float
            Wavelength of the light.
        exterior_index : float
            Refractive index of the exterior structure.

        Returns
        -------
        float
            Computed V-number.
        """
        delta_index = np.sqrt(self.refractive_index**2 - exterior_index**2)
        V_number = (2 * np.pi / wavelength) * delta_index * self.radius
        return V_number

    def scale(self, factor: float) -> None:
        """
        Scale the radius of the optical structure by a given factor.

        Parameters
        ----------
        factor : float
            Scaling factor.
        """
        self.radius *= factor
        self.polygon = Circle(position=self.position, radius=self.radius)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Tuple, Optional
from pydantic.dataclasses import dataclass
from pydantic import ConfigDict
import shapely.geometry as geo
from shapely import affinity

from FiberFusing.components.utils import interpret_to_point
from FiberFusing.components.polygon import Polygon

config_dict = ConfigDict(extra='forbid', strict=True, kw_only=True)


@dataclass(config=config_dict)
class Circle(Polygon):
    """
    Represents a circular geometry centered at a specified position with a given radius.

    Parameters
    ----------
    position : Tuple[float, float]
        The center position of the circle.
    radius : float
        The radius of the circle.
    resolution : Optional[int], optional
        The resolution of the circle's edge. Higher values yield smoother circles. Default is 128.
    index : Optional[float], optional
        The refractive index of the circle. Default is None.
    """
    position: Tuple[float, float]
    radius: float
    resolution: Optional[int] = 128
    index: Optional[float] = None

    def __post_init__(self):
        """
        Initialize the circular geometry based on the specified position and radius.

        Notes
        -----
        - The geometry is created using a buffer method applied to the position.
        - The position is interpreted and converted to a `shapely` point.
        """
        self.position = interpret_to_point(self.position)

        # Validate radius
        if self.radius <= 0:
            raise ValueError("Radius must be a positive value.")

        # Create a circular geometry using buffer
        circle = self.position._shapely_object.buffer(
            self.radius,
            resolution=self.resolution
        )

        self._shapely_object = circle
        self.core = self.center.copy()


@dataclass(config=config_dict)
class Ellipse(Polygon):
    """
    Represents an elliptical geometry centered at a specified position with a given radius and axis ratio.

    Parameters
    ----------
    position : tuple
        The center position of the ellipse.
    radius : float
        The radius along the major axis.
    resolution : Optional[int], optional
        The resolution of the ellipse's edge. Higher values yield smoother edges. Default is 128.
    index : Optional[float], optional
        The refractive index of the ellipse. Default is None.
    ratio : Optional[float], optional
        The ratio between the minor and major axes. Default is 1 (circular shape).
    """
    position: tuple
    radius: float
    resolution: Optional[int] = 128
    index: Optional[float] = None
    ratio: Optional[float] = 1  # Default ratio of 1 makes this a circle

    def __post_init__(self):
        """
        Initialize the elliptical geometry based on the specified position, radius, and ratio.

        Notes
        -----
        - The ellipse is scaled using the specified ratio after creating a circular base shape.
        - The position is interpreted and converted to a `shapely` point.
        """
        self.position = interpret_to_point(self.position)

        # Validate radius and ratio
        if self.radius <= 0:
            raise ValueError("Radius must be a positive value.")
        if self.ratio <= 0:
            raise ValueError("Ratio must be a positive value.")

        ellipse = self.position._shapely_object.buffer(
            self.radius,
            resolution=self.resolution
        )

        # Scale the ellipse according to the ratio
        ellipse = affinity.scale(
            ellipse,
            xfact=1,
            yfact=self.ratio,
            origin=(0, 0)
        )

        super().__init__(instance=ellipse)
        self.core = self.center.copy()


@dataclass(config=config_dict)
class Square(Polygon):
    """
    Represents a square geometry centered at a specified position with a given side length.

    Parameters
    ----------
    position : tuple
        The center position of the square.
    length : float
        The length of the square's sides.
    index : Optional[float], optional
        The refractive index of the square. Default is None.
    """
    position: tuple
    length: float
    index: Optional[float] = None

    def __post_init__(self):
        """
        Initialize the square geometry based on the specified position and side length.

        Notes
        -----
        - The square is created using `shapely.geometry.box` method.
        - The position is interpreted and converted to a `shapely` point.
        """
        self.position = interpret_to_point(self.position)

        # Validate length
        if self.length <= 0:
            raise ValueError("Length must be a positive value.")

        square = geo.box(
            self.position.x - self.length / 2,
            self.position.y - self.length / 2,
            self.position.x + self.length / 2,
            self.position.y + self.length / 2
        )

        super().__init__(instance=square)
        self.core = self.center.copy()

# -

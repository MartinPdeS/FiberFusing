#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
from typing import Tuple, Optional
from pydantic.dataclasses import dataclass

from FiberFusing.geometries.utils import interpret_to_point
from FiberFusing.geometries.polygon import Polygon
from FiberFusing.shapes.base import config_dict

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
    refractive_index : Optional[float], optional
        The refractive index of the circle. Default is None.
    """
    position: Tuple[float, float]
    radius: float
    resolution: Optional[int] = 128
    refractive_index: Optional[float] = None

    def __post_init__(self):
        """
        Initialize the circular geometry based on the specified position and radius.

        Notes
        -----
        - The geometry is created using a buffer method applied to the position.
        - The position is interpreted and converted to a `shapely` point.
        """
        self.position = interpret_to_point(self.position)
        if not all(math.isfinite(value) for value in (self.position.x, self.position.y)):
            raise ValueError("Position coordinates must be finite.")
        if self.resolution is None or self.resolution < 1:
            raise ValueError("resolution must be a positive integer.")

        # Validate radius
        if not math.isfinite(self.radius) or self.radius <= 0:
            raise ValueError("Radius must be a positive value.")

        # Create a circular geometry using buffer
        circle = self.position._shapely_object.buffer(
            self.radius,
            quad_segs=self.resolution
        )

        self._shapely_object = circle
        self.core = self.center.copy()

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
from typing import Optional
from pydantic.dataclasses import dataclass

from shapely import affinity

from FiberFusing.geometries.utils import interpret_to_point
from FiberFusing.geometries.polygon import Polygon
from FiberFusing.shapes.base import config_dict

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
    refractive_index : Optional[float], optional
        The refractive index of the ellipse. Default is None.
    ratio : Optional[float], optional
        The ratio between the minor and major axes. Default is 1 (circular shape).
    """
    position: tuple
    radius: float
    resolution: Optional[int] = 128
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
        if not all(math.isfinite(value) for value in (self.position.x, self.position.y)):
            raise ValueError("Position coordinates must be finite.")
        if self.resolution is None or self.resolution < 1:
            raise ValueError("resolution must be a positive integer.")

        # Validate radius and ratio
        if not math.isfinite(self.radius) or self.radius <= 0:
            raise ValueError("Radius must be a positive value.")
        if not math.isfinite(self.ratio) or self.ratio <= 0:
            raise ValueError("Ratio must be a positive value.")

        ellipse = self.position._shapely_object.buffer(
            self.radius,
            quad_segs=self.resolution
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

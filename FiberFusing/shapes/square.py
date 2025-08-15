#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Optional
from pydantic.dataclasses import dataclass
import shapely.geometry as geo

from FiberFusing.geometries.utils import interpret_to_point
from FiberFusing.geometries.polygon import Polygon
from FiberFusing.shapes.base import config_dict

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

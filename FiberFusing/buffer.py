#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Tuple, Optional
from pydantic.dataclasses import dataclass
from pydantic import ConfigDict

import shapely.geometry as geo
from shapely import affinity

from FiberFusing.components.utils import interpret_to_point
from FiberFusing.components.polygon import _Polygon, Polygon  # noqa: F401

config_dict = ConfigDict(extra='forbid', strict=True)


@dataclass(config=config_dict, kw_only=True)
class Circle(_Polygon):
    position: Tuple[float, float]
    radius: float
    resolution: Optional[int] = 128
    index: Optional[float] = None

    def __post_init__(self):
        """
        Initializes a circular geometry centered at `position` with a given `radius`.
        """
        self.position = interpret_to_point(self.position)

        # Create a circular geometry using buffer
        circle = self.position._shapely_object.buffer(
            self.radius,
            resolution=self.resolution
        )

        self._shapely_object = circle

        self.core = self.center.copy()


@dataclass(config=config_dict, kw_only=True)
class Ellipse(_Polygon):
    position: tuple
    radius: float
    resolution: Optional[int] = 128
    index: Optional[float] = None
    ratio: Optional[float] = 1  # Default ratio of 1 makes this a circle

    def __post_init__(self):
        """
        Initializes an elliptical geometry centered at `position` with a given `radius` and axis ratio.
        """
        self.position = interpret_to_point(self.position)

        ellipse = self.position._shapely_object.buffer(
            self.radius,
            resolution=self.resolution
        )

        ellipse = affinity.scale(
            ellipse,
            xfact=1,
            yfact=self.ratio,
            origin=(0, 0)
        )

        super().__init__(instance=ellipse)

        self.core = self.center.copy()


@dataclass(config=config_dict, kw_only=True)
class Square(_Polygon):
    position: tuple
    length: float
    index: Optional[float] = None

    def __post_init__(self):
        """
        Initializes a square geometry centered at `position` with side length `length`.
        """
        self.position = interpret_to_point(self.position)

        square = geo.box(
            self.position.x - self.length / 2,
            self.position.y - self.length / 2,
            self.position.x + self.length / 2,
            self.position.y + self.length / 2
        )

        super().__init__(instance=square)

        self.core = self.center.copy()

# -

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import List, Tuple, Optional
import numpy as np
import logging
from scipy.optimize import minimize_scalar
from pydantic.dataclasses import dataclass
from pydantic import ConfigDict

import FiberFusing as ff
from FiberFusing import utils
from FiberFusing.shapes.circle import Circle
from FiberFusing.connection.utils import TopologyType, ConscriptedCircleType



@dataclass(config=ConfigDict(extra='forbid', arbitrary_types_allowed=True, strict=True, frozen=False))
class Connection:
    """
    Represents a connection between two optical fiber circles.

    This class manages the geometric relationship between two fibers, including
    their fusion topology, area calculations, and core positioning optimization.

    Parameters
    ----------
    fiber0 : Circle
        The first fiber in the connection.
    fiber1 : Circle
        The second fiber in the connection.

    Attributes
    ----------
    topology : TopologyType
        The connection topology (convex, concave, or undefined).
    shift : float
        The shift value for the connection geometry.
    added_section : ff.Polygon
        The area added during fiber fusion.
    removed_section : ff.Polygon
        The area removed during fiber fusion.
    virtual_circles : tuple[Circle, Circle] | None
        Pair of virtual circles used for geometry calculations.
    mask : ff.Polygon | None
        Geometric mask for connection calculations.
    core_shift : tuple[ff.Point, ff.Point] | None
        Optimized core position shifts for both fibers.
    """

    fiber0: Circle
    fiber1: Circle

    def __post_init__(self) -> None:
        """Initialize connection properties with default values."""
        self._topology = TopologyType.UNDEFINED
        self._shift: float = 0.0
        self.added_section = ff.EmptyPolygon()
        self.removed_section = ff.EmptyPolygon()
        self.virtual_circles: Optional[Tuple[Circle, Circle]] = None
        self.mask: Optional[ff.Polygon] = None
        self.core_shift: Optional[Tuple[ff.Point, ff.Point]] = None

        logging.info(f"Created connection between fibers at {self.fiber0.center} and {self.fiber1.center}")

    @property
    def topology(self) -> TopologyType:
        """Get the connection topology."""
        return self._topology

    @topology.setter
    def topology(self, value: TopologyType) -> None:
        """Set the connection topology with validation."""
        if not isinstance(value, TopologyType):
            raise TypeError(f"Topology must be a TopologyType enum, got {type(value).__name__}")
        self._topology = value

    @property
    def shift(self) -> float:
        """Get the connection shift value."""
        return self._shift

    @shift.setter
    def shift(self, value: float) -> None:
        """Set the connection shift value."""
        self._shift = float(value)

    @property
    def fibers(self) -> List[Circle]:
        """Get list of connected fibers."""
        return [self.fiber0, self.fiber1]

    def __getitem__(self, idx: int) -> Circle:
        """Get fiber by index."""
        if idx not in (0, 1):
            raise IndexError(f"Fiber index must be 0 or 1, got {idx}")
        return self.fibers[idx]

    def __setitem__(self, idx: int, fiber: Circle) -> None:
        """Set fiber by index."""
        if idx not in (0, 1):
            raise IndexError(f"Fiber index must be 0 or 1, got {idx}")
        if idx == 0:
            self.fiber0 = fiber
        else:
            self.fiber1 = fiber

    # =============================================================================
    # GEOMETRIC PROPERTIES
    # =============================================================================

    @property
    def distance_between_cores(self) -> float:
        """Calculate distance between fiber centers."""
        return self.fiber0.center.distance(self.fiber1.center)

    @property
    def center_line(self) -> ff.LineString:
        """Get line connecting fiber centers."""
        return ff.LineString(coordinates=[self.fiber0.center, self.fiber1.center])

    @property
    def extended_center_line(self) -> ff.LineString:
        """Get extended line connecting fiber centers."""
        line = self.center_line
        extension = self.fiber0.radius + self.fiber1.radius
        return line.make_length(line.length + extension)

    @property
    def limit_added_area(self) -> ff.Polygon:
        """Calculate the theoretical maximum added area."""
        union_hull = self.fiber0.union(self.fiber1).convex_hull
        return union_hull - self.fiber0 - self.fiber1

    @property
    def total_area(self) -> ff.Polygon:
        """Get total area including both fibers and added section."""
        output = utils.union_geometries(self.fiber0, self.fiber1, self.added_section)
        output.remove_non_polygon_elements()
        return output

    # =============================================================================
    # CONNECTION CONFIGURATION
    # =============================================================================

    def configure_connection(self, shift: float, topology: TopologyType) -> None:
        """
        Configure connection with shift and topology parameters.

        Parameters
        ----------
        shift : float
            The shift value for connection geometry.
        topology : TopologyType
            The connection topology type.
        """
        self.shift = shift
        self.topology = topology

        self._compute_all_geometry()

        logging.info(f"Configured connection: shift={shift:.3f}, topology={self.topology.value}")


    def _compute_all_geometry(self) -> None:
        """Compute all geometric components in correct order."""
        if self.topology == TopologyType.UNDEFINED:
            raise ValueError("Cannot compute geometry with undefined topology")

        self._compute_virtual_circles()
        self._compute_mask()
        self._compute_added_section()
        self._compute_removed_section()

    # =============================================================================
    # GEOMETRIC CALCULATIONS
    # =============================================================================

    def _compute_virtual_circles(self) -> None:
        """Compute conscripted virtual circles based on topology."""
        circle_type = (
            ConscriptedCircleType.EXTERIOR if self.topology == TopologyType.CONCAVE
            else ConscriptedCircleType.INTERIOR
        )

        primary_circle = self._get_conscripted_circle(circle_type)
        secondary_circle = primary_circle.rotate(
            angle=180,
            origin=self.center_line.mid_point,
            in_place=False
        )

        self.virtual_circles = (primary_circle, secondary_circle)

    def _get_conscripted_circle(self, circle_type: ConscriptedCircleType) -> Circle:
        """
        Create conscripted circle based on type.

        Parameters
        ----------
        circle_type : ConscriptedCircleType
            Type of conscripted circle to create.

        Returns
        -------
        Circle
            The conscripted circle.
        """
        line = self.center_line
        perpendicular = self.extended_center_line.get_perpendicular().get_vector()
        center_point = line.mid_point.translate(perpendicular * self.shift)

        base_radius = np.sqrt(self.shift**2 + (line.length / 2)**2)

        if circle_type == ConscriptedCircleType.EXTERIOR:
            radius = base_radius - self.fiber0.radius
        else:  # INTERIOR
            radius = base_radius + self.fiber0.radius

        return Circle(position=(center_point.x, center_point.y), radius=radius)

    def _compute_mask(self) -> None:
        """Compute geometric mask for connection."""
        if not self.virtual_circles:
            raise ValueError("Virtual circles must be computed before mask")

        contact_points = self._get_contact_points()

        if self.topology == TopologyType.CONCAVE:
            self.mask = self._compute_concave_mask(contact_points)
        else:  # CONVEX
            self.mask = self._compute_convex_mask(contact_points)

    def _get_contact_points(self) -> List[ff.Point]:
        """Get contact points between fibers and virtual circles."""
        if not self.virtual_circles:
            raise ValueError("Virtual circles not computed")

        v0, v1 = self.virtual_circles

        contacts = [
            utils.nearest_points_exterior(v0, self.fiber0),
            utils.nearest_points_exterior(v1, self.fiber0),
            utils.nearest_points_exterior(v0, self.fiber1),
            utils.nearest_points_exterior(v1, self.fiber1)
        ]

        return [ff.Point(position=(p.x, p.y)) for p in contacts]

    def _compute_concave_mask(self, contact_points: List[ff.Point]) -> ff.Polygon:
        """Compute mask for concave topology."""
        p0, p1, p2, p3 = contact_points
        coordinates = [(p._shapely_object.x, p._shapely_object.y) for p in [p0, p1, p3, p2]]

        mask = ff.Polygon(coordinates=coordinates)
        v0, v1 = self.virtual_circles
        return mask - v0 - v1

    def _compute_convex_mask(self, contact_points: List[ff.Point]) -> ff.Polygon:
        """Compute mask for convex topology."""
        p0, p1, p2, p3 = contact_points
        mid_point = self.center_line.mid_point

        # Create two mask triangles
        coords0 = [(p._shapely_object.x, p._shapely_object.y) for p in [mid_point, p0, p2]]
        coords1 = [(p._shapely_object.x, p._shapely_object.y) for p in [mid_point, p1, p3]]

        mask0 = ff.Polygon(coordinates=coords0)
        mask1 = ff.Polygon(coordinates=coords1)

        # Scale masks
        scale_factor = 1000
        mask0.scale(factor=scale_factor, origin=mid_point._shapely_object, in_place=True)
        mask1.scale(factor=scale_factor, origin=mid_point._shapely_object, in_place=True)

        # Combine masks with virtual circles
        v0, v1 = self.virtual_circles
        combined_mask = utils.union_geometries(mask0, mask1)
        combined_virtual = utils.union_geometries(v0, v1)

        return combined_mask & combined_virtual

    def _compute_added_section(self) -> None:
        """Compute the area added during fiber fusion."""
        if not self.virtual_circles or not self.mask:
            raise ValueError("Virtual circles and mask must be computed first")

        v0, v1 = self.virtual_circles
        base_section = self.mask - self.fiber0 - self.fiber1

        if self.topology == TopologyType.CONVEX:
            intersection = v0.intersection(v1, in_place=False)
            self.added_section = base_section & intersection
        else:  # CONCAVE
            union = v0.union(v1, in_place=False)
            self.added_section = base_section - union

        self.added_section.remove_non_polygon_elements()

    def _compute_removed_section(self) -> None:
        """Compute the area removed during fiber fusion."""
        self.removed_section = utils.intersection_geometries(self.fiber0, self.fiber1)

        # Calculate actual removed area
        total_individual_area = self.fiber0.area + self.fiber1.area
        union_area = utils.union_geometries(self.fiber0, self.fiber1).area
        self.removed_section.Area = total_individual_area - union_area

    def determine_topology(self) -> TopologyType:
        """
        Automatically determine connection topology based on geometry.

        Returns
        -------
        TopologyType
            The determined topology type.
        """
        if self.removed_section.Area > self.limit_added_area.area:
            return TopologyType.CONVEX
        else:
            return TopologyType.CONCAVE

    # =============================================================================
    # GEOMETRY OPERATIONS
    # =============================================================================

    def split_geometry(self,
        geometry: ff.Polygon,
        position: ff.Point,
        return_largest: bool = True) -> ff.Polygon:
        """
        Split geometry at specified position.

        Parameters
        ----------
        geometry : ff.Polygon
            Geometry to split.
        position : ff.Point
            Position for splitting.
        return_largest : bool, default True
            Whether to return the largest split section.

        Returns
        -------
        ff.Polygon
            The split geometry section.
        """
        # Create perpendicular split line
        split_line = self.center_line.centering(center=position)
        split_line = split_line.rotate(angle=90, origin=split_line.mid_point)
        split_line = split_line.extend(factor=2)

        # Prepare geometry and split
        clean_geometry = (utils.union_geometries(geometry.copy())
                         .remove_non_polygon_elements()
                         .keep_largest_polygon())

        return clean_geometry.split_with_line(line=split_line, return_largest=return_largest)

    # =============================================================================
    # CORE POSITION OPTIMIZATION
    # =============================================================================

    def optimize_core_positions(self, tolerance: float = 1e-10) -> None:
        """
        Optimize core positions to minimize area mismatch.

        Parameters
        ----------
        tolerance : float, default 1e-10
            Optimization tolerance.
        """
        logging.info("Starting core position optimization...")

        result = minimize_scalar(
            self._compute_area_mismatch_cost,
            bounds=(0.50001, 0.99),
            method='bounded',
            options={'xatol': tolerance}
        )

        if result.success:
            logging.info(f"Optimization successful: cost={result.fun:.2e}")
            # Apply optimized shifts
            if self.core_shift:
                self.fiber0.shifted_core += self.core_shift[0]
                self.fiber1.shifted_core += self.core_shift[1]
        else:
            logging.warning(f"Optimization failed: {result.message}")

    def _compute_area_mismatch_cost(self, x: float) -> float:
        """
        Compute area mismatch cost for optimization.

        Parameters
        ----------
        x : float
            Optimization parameter (0 to 1).

        Returns
        -------
        float
            Cost value to minimize.
        """
        # Get split positions
        line = self.extended_center_line
        position0 = line.get_position_parametrization(1 - x)
        position1 = line.get_position_parametrization(x)

        # Calculate small section area
        small_section = self.split_geometry(
            geometry=self.total_area,
            position=position0,
            return_largest=False
        )

        # Compute cost and store shifts
        target_area = self.fiber0.area / 2.0
        cost = abs(small_section.area - target_area)

        self.core_shift = (
            position0 - self.fiber0.center,
            position1 - self.fiber1.center
        )

        logging.debug(f"Optimization step: x={x:.3f}, cost={cost:.2e}")

        return cost

    # =============================================================================
    # UTILITY METHODS
    # =============================================================================

    def get_connection_summary(self) -> dict:
        """
        Get summary of connection properties.

        Returns
        -------
        dict
            Dictionary containing connection summary.
        """
        return {
            'distance_between_cores': self.distance_between_cores,
            'topology': self.topology.value,
            'shift': self.shift,
            'added_area': self.added_section.area if hasattr(self.added_section, 'area') else 0,
            'removed_area': getattr(self.removed_section, 'Area', 0),
            'total_area': self.total_area.area,
            'fiber0_center': (self.fiber0.center.x, self.fiber0.center.y),
            'fiber1_center': (self.fiber1.center.x, self.fiber1.center.y),
        }

    def __repr__(self) -> str:
        """String representation of the connection."""
        return (f"Connection(fiber0=Circle({self.fiber0.center.x:.2f}, {self.fiber0.center.y:.2f}), "
                f"fiber1=Circle({self.fiber1.center.x:.2f}, {self.fiber1.center.y:.2f}), "
                f"topology={self.topology.value})")
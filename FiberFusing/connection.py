#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy
import logging
from scipy.optimize import minimize_scalar
from pydantic.dataclasses import dataclass
from pydantic import ConfigDict
import FiberFusing as ff
from FiberFusing import utils
from FiberFusing.buffer import Circle


@dataclass(config=ConfigDict(extra='forbid', arbitrary_types_allowed=True, strict=True))
class Connection:
    """
    Represents a connection between two fiber circles.

    Parameters
    ----------
    fiber0 : Circle
        The first fiber in the connection.
    fiber1 : Circle
        The second fiber in the connection.
    """
    fiber0: Circle
    fiber1: Circle

    def __post_init__(self):
        """
        Initialize the Connection instance between two fibers.

        Notes
        -----
        - Initializes additional attributes such as `added_section`, `removed_section`, `topology`,
          and `shift`.
        """
        self.fiber_list = [self.fiber0, self.fiber1]
        self.added_section = ff.EmptyPolygon()
        self.removed_section = ff.EmptyPolygon()
        self.topology = "not defined"
        self.shift = "not defined"

    def set_shift_and_topology(self, shift: float, topology: str) -> None:
        """
        Set the shift and topology for the connection and compute related properties.

        Parameters
        ----------
        shift : float
            The shift value for the connection.
        topology : str
            The topology type for the connection.
        """
        self.shift = shift
        self.topology = topology
        self.compute_virtual_circles()
        self.compute_mask()
        self.compute_added_section()
        self.compute_removed_section()

    def __getitem__(self, idx: int) -> Circle:
        """
        Retrieve a fiber by index.

        Parameters
        ----------
        idx : int
            The index of the fiber to retrieve.

        Returns
        -------
        Circle
            The fiber object at the specified index.
        """
        return self.fiber_list[idx]

    def __setitem__(self, idx: int, item: Circle) -> None:
        """
        Set a fiber at a specified index.

        Parameters
        ----------
        idx : int
            The index at which to set the fiber.
        item : Circle
            The fiber object to set.
        """
        self.fiber_list[idx] = item

    @property
    def distance_between_cores(self) -> float:
        """
        Calculate the distance between the centers of the two fibers.

        Returns
        -------
        float
            The distance between the fiber centers.
        """
        return self[0].center.distance(self[1].center)

    @property
    def limit_added_area(self) -> ff.Polygon:
        """
        Calculate the limit added area formed by the union of the two fibers.

        Returns
        -------
        ff.Polygon
            The polygon representing the limit added area.
        """
        return self[0].union(self[1]).convex_hull - self[0] - self[1]

    def compute_removed_section(self) -> None:
        """
        Compute the removed section of the connection.

        Notes
        -----
        - Calculates the area of the removed section based on intersections.
        """
        self.removed_section = utils.intersection_geometries(*self)
        self.removed_section.Area = self[1].area + self[0].area - utils.union_geometries(*self).area

    def compute_topology(self) -> None:
        """
        Determine the topology of the connection based on the area of the removed section.

        Notes
        -----
        - Sets topology as 'convex' or 'concave' based on comparison with the limit added area.
        """
        if self.removed_section.Area > self.limit_added_area.area:
            self.topology = 'convex'
        else:
            self.topology = 'concave'

    def get_conscripted_circles(self, type: str = 'exterior') -> Circle:
        """
        Return the conscripted circles of the connection, which can be either 'exterior' or 'interior'.

        Parameters
        ----------
        type : str, optional
            The type of conscripted circle to compute ('exterior' or 'interior'). Default is 'exterior'.

        Returns
        -------
        Circle
            The conscripted circle based on the specified type.

        Raises
        ------
        ValueError
            If the type is invalid.
        """
        extended_line = self.get_center_line(extended=True)
        line = self.get_center_line(extended=False)
        perpendicular_vector = extended_line.get_perpendicular().get_vector()
        point = line.mid_point.translate(perpendicular_vector * self.shift)

        if type.lower() in ['exterior', 'concave']:
            radius = numpy.sqrt(self.shift**2 + (line.length / 2)**2) - self[0].radius
        elif type.lower() in ['interior', 'convex']:
            radius = numpy.sqrt(self.shift**2 + (line.length / 2)**2) + self[0].radius
        else:
            raise ValueError(f"Invalid type '{type}'. Expected 'exterior' or 'interior'.")

        return Circle(position=(point.x, point.y), radius=radius)

    def compute_virtual_circles(self) -> None:
        """
        Compute the conscripted virtual circles based on the current topology.

        Raises
        ------
        Exception
            If the topology is not defined.
        """
        if self.topology == "not defined":
            raise Exception("Trying to compute conscripted virtual circles without a defined topology!")

        line = self.get_center_line(extended=False)
        conscripted_0 = self.get_conscripted_circles(type=self.topology)
        conscripted_1 = conscripted_0.rotate(
            angle=180,
            origin=line.mid_point,
            in_place=False
        )
        self.virtual_circles = conscripted_0, conscripted_1

    def get_connected_point(self) -> list:
        """
        Return a list of contact points from the connected fibers and virtual circles.

        Returns
        -------
        list
            A list of contact points as ff.Point instances.
        """
        P0 = utils.nearest_points_exterior(self.virtual_circles[0], self[0])
        P1 = utils.nearest_points_exterior(self.virtual_circles[1], self[0])
        P2 = utils.nearest_points_exterior(self.virtual_circles[0], self[1])
        P3 = utils.nearest_points_exterior(self.virtual_circles[1], self[1])

        return [ff.Point(position=(p.x, p.y)) for p in [P0, P1, P2, P3]]

    def compute_mask(self) -> None:
        """
        Compute the mask that connects the center to the contact points with the virtual circles.

        Notes
        -----
        - The mask computation varies depending on whether the topology is 'concave' or 'convex'.
        """
        P0, P1, P2, P3 = self.get_connected_point()

        if self.topology.lower() == 'concave':
            coordinates = [(p._shapely_object.x, p._shapely_object.y) for p in [P0, P1, P3, P2]]
            mask = ff.Polygon(coordinates=coordinates)
            self.mask = (mask - self.virtual_circles[0] - self.virtual_circles[1])

        elif self.topology.lower() == 'convex':
            mid_point = ff.LineString(coordinates=[self[0].center, self[1].center]).mid_point

            coordinates0 = [(p._shapely_object.x, p._shapely_object.y) for p in [mid_point, P0, P2]]
            mask0 = ff.Polygon(coordinates=coordinates0)
            mask0.scale(factor=1000, origin=mid_point._shapely_object, in_place=True)

            coordinates1 = [(p._shapely_object.x, p._shapely_object.y) for p in [mid_point, P1, P3]]
            mask1 = ff.Polygon(coordinates=coordinates1)
            mask1.scale(factor=1000, origin=mid_point._shapely_object, in_place=True)

            self.mask = (utils.union_geometries(mask0, mask1) & utils.union_geometries(*self.virtual_circles))

    def compute_added_section(self) -> None:
        """
        Compute the added section of the connection based on the topology.

        Notes
        -----
        - The added section computation varies depending on whether the topology is 'convex' or 'concave'.
        """
        if self.topology == 'convex':
            intersection = self.virtual_circles[0].intersection(self.virtual_circles[1], in_place=False)
            self.added_section = (self.mask - self[0] - self[1]) & intersection

        elif self.topology == 'concave':
            union = self.virtual_circles[0].union(self.virtual_circles[1], in_place=False)
            self.added_section = self.mask - self[0] - self[1] - union

        self.added_section.remove_non_polygon_elements()

    def get_center_line(self, extended: bool = False) -> ff.LineString:
        """
        Get the line connecting the centers of the two connected fibers.

        Parameters
        ----------
        extended : bool, optional
            Indicates if the line should be extended. Default is False.

        Returns
        -------
        ff.LineString
            The line connecting the centers of the two fibers.
        """
        line = ff.LineString(coordinates=[self[0].center, self[1].center])

        if extended:
            line = line.make_length(line.length + self[0].radius + self[1].radius)

        return line

    @property
    def total_area(self) -> ff.Polygon:
        """
        Returns a polygon representing the total area of the two connected fibers.

        Returns:
            ff.Polygon: The polygon representing the total area.
        """
        output = utils.union_geometries(*self, self.added_section)
        output.remove_non_polygon_elements()

        return output

    def split_geometry(self, geometry: ff.Polygon, position: ff.Point, return_largest: bool = True) -> ff.Polygon:
        """
        Splits the connection geometry at a specified position.

        Parameters:
            geometry (ff.Polygon): The geometry to be split.
            position (ff.Point): The position at which to split the geometry.
            return_largest (bool): Whether to return the largest part of the split geometry.

        Returns:
            ff.Polygon: The split geometry.
        """
        split_line = self.get_center_line(extended=False)
        split_line = split_line.centering(center=position)
        split_line = split_line.rotate(angle=90, origin=split_line.mid_point)
        split_line = split_line.extend(factor=2)

        external_part = utils.union_geometries(geometry.copy()).remove_non_polygon_elements().keep_largest_polygon()

        return external_part.split_with_line(line=split_line, return_largest=return_largest)

    def compute_area_mismatch_cost(self, x: float = 0.5) -> float:
        """
        Compute the cost of area mismatch for the connection based on a given parameter x.

        This function splits the total area of the connected fibers at a specified position
        and computes the cost as the absolute difference between the area of the smaller section
        and half the area of the first fiber. It also calculates the shift in the core positions.

        Parameters:
            x (float): The parameter used to determine the split position, ranging from 0 to 1.

        Returns:
            float: The computed cost of area mismatch.
        """
        line = self.get_center_line(extended=True)
        position0 = line.get_position_parametrization(1 - x)
        position1 = line.get_position_parametrization(x)

        small_section = self.split_geometry(
            geometry=self.total_area,
            position=position0,
            return_largest=False
        )

        cost = abs(small_section.area - self[0].area / 2.0)

        self.core_shift = (position0 - self[0].center), (position1 - self[1].center)

        logging.info(
            f'Core positioning optimization: x = {x:.2f} -> cost = {cost:.2e} -> core shift: ({self.core_shift[0].x}, {self.core_shift[0].y})'
        )

        return cost

    def optimize_core_position(self) -> None:
        """
        Optimize the core positions of the connected fibers to minimize the area mismatch.

        This method uses a scalar minimization algorithm to find the optimal parameter x that
        minimizes the area mismatch cost. It then adjusts the core positions of both fibers
        based on the computed core shifts.

        Returns:
            None
        """
        result = minimize_scalar(
            self.compute_area_mismatch_cost,
            bounds=(0.50001, 0.99),
            method='bounded',
            options={'xatol': 1e-10}
        )

        logging.info(result)

        self[0].shifted_core += self.core_shift[0]
        self[1].shifted_core += self.core_shift[1]
# -

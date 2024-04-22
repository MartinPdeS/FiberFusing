#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Built-in imports
import numpy
import logging
from scipy.optimize import minimize_scalar

# Local imports
import FiberFusing as ff
from FiberFusing import utils


class Connection():
    def __init__(self, fiber0, fiber1):
        self.fiber_list = [fiber0, fiber1]
        self.added_section = ff.EmptyPolygon()
        self.removed_section = ff.EmptyPolygon()
        self.topology = "not defined"
        self.shift = "not-defined"

    def set_shift_and_topology(self, shift: float, topology: str):
        self.shift = shift
        self.topology = topology
        self.compute_virtual_circles()
        self.compute_mask()
        self.compute_added_section()
        self.compute_removed_section()

    def __getitem__(self, idx):
        return self.fiber_list[idx]

    def __setitem__(self, idx, item):
        self.fiber_list[idx] = item

    @property
    def distance_between_cores(self):
        return self[0].center.distance(self[1].center)

    @property
    def limit_added_area(self):
        return self[0].union(self[1]).convex_hull - self[0] - self[1]

    def compute_removed_section(self) -> None:
        self.removed_section = utils.Intersection(*self)  # here
        self.removed_section.Area = self[1].area + self[0].area - utils.Union(*self).area  # here

    def compute_topology(self) -> None:
        if self.removed_section.Area > self.limit_added_area.area:
            self.topology = 'convex'
        else:
            self.topology = 'concave'

    def get_conscripted_circles(self, type='exterior') -> ff.Circle:
        """
        Return the connection two circonscript circles, which can be either of type exterior
        or interior.

        :param      type:  The type of circonscript circle to compute
        :type       type:  str

        :returns:   The conscripted circles.
        :rtype:     ff.Circle
        """
        extended_line = self.get_center_line(extended=True)
        line = self.get_center_line(extended=False)

        perpendicular_vector = extended_line.get_perpendicular().get_vector()

        point = line.mid_point.translate(perpendicular_vector * self.shift)

        if type.lower() in ['exterior', 'concave']:
            radius = numpy.sqrt(self.shift**2 + (line.length / 2)**2) - self[0].radius

        if type.lower() in ['interior', 'convex']:
            radius = numpy.sqrt(self.shift**2 + (line.length / 2)**2) + self[0].radius

        return ff.Circle(position=point, radius=radius)

    def compute_virtual_circles(self) -> None:
        if self.topology == "not defined":
            raise Exception("Trying to compute circonsript virtual circles with a defined topology!")

        line = self.get_center_line(extended=False)

        circonscript_0 = self.get_conscripted_circles(type=self.topology)

        circonscript_1 = circonscript_0.rotate(
            angle=180,
            origin=line.mid_point,
            in_place=False
        )

        self.virtual_circles = circonscript_0, circonscript_1

    def get_connected_point(self) -> list:
        """
        Return list of contact point from the connected fibers and
        virtual circles.
        """
        P0 = utils.NearestPoints(self.virtual_circles[0], self[0])
        P1 = utils.NearestPoints(self.virtual_circles[1], self[0])
        P2 = utils.NearestPoints(self.virtual_circles[0], self[1])
        P3 = utils.NearestPoints(self.virtual_circles[1], self[1])

        return [ff.Point(position=(p.x, p.y)) for p in [P0, P1, P2, P3]]

    def compute_mask(self) -> None:
        """
        Compute the mask that is connecting the center to the contact point
        with the virtual circles.

        :returns:   No return.
        :rtype:     None
        """
        P0, P1, P2, P3 = self.get_connected_point()

        if self.topology.lower() == 'concave':

            mask = ff.Polygon(coordinates=[P0._shapely_object, P1._shapely_object, P3._shapely_object, P2._shapely_object])

            self.mask = (mask - self.virtual_circles[0] - self.virtual_circles[1])

            # utils.multi_plot(*self.fiber_list, self.mask, *self.virtual_circles)

        elif self.topology.lower() == 'convex':
            mid_point = ff.LineString(coordinates=[self[0].center, self[1].center]).mid_point

            mask0 = ff.Polygon(coordinates=[mid_point._shapely_object, P0._shapely_object, P2._shapely_object])
            mask0.scale(
                factor=1000,
                origin=mid_point._shapely_object,
                in_place=True
            )

            mask1 = ff.Polygon(coordinates=[mid_point._shapely_object, P1._shapely_object, P3._shapely_object])
            mask1.scale(
                factor=1000,
                origin=mid_point._shapely_object,
                in_place=True
            )

            self.mask = (utils.Union(mask0, mask1) & utils.Union(*self.virtual_circles))

    def compute_added_section(self) -> None:
        if self.topology == 'convex':
            intersection = self.virtual_circles[0].intersection(self.virtual_circles[1], in_place=False)
            self.added_section = (self.mask - self[0] - self[1]) & intersection

        elif self.topology == 'concave':
            union = self.virtual_circles[0].union(self.virtual_circles[1], in_place=False)
            self.added_section = self.mask - self[0] - self[1] - union

        self.added_section.remove_non_polygon_elements()

    def get_center_line(self, extended: bool = False) -> ff.LineString:
        """
        Returns the line connecting the two centers of the connected fibers.
        If extended is true that line is extended up to the boundary of the two fibers.

        :param      extended:  Indicates if extended
        :type       extended:  bool

        :returns:   The center line.
        :rtype:     ff.LineString
        """
        line = ff.LineString(coordinates=[self[0].center, self[1].center])

        if extended is True:
            line = line.make_length(line.length + self[0].radius + self[1].radius)

        return line

    @property
    def total_area(self) -> ff.Polygon:
        """
        Returns polygone representating the total area of the connected two fibers.

        :returns:   Total area
        :rtype:     ff.Polygon
        """
        output = utils.Union(*self, self.added_section)
        output.remove_non_polygon_elements()

        return output

    def split_geometry(self, geometry: ff.Polygon, position: ff.Point, return_largest: bool = True) -> ff.Polygon:
        """
        Split the connection at a certain position x which is the parametrised
        point covering the full connection.

        :param      geometry:  The geometry
        :type       geometry:  ff.Polygon
        :param      position:  The parametrized position
        :type       position:  float

        :returns:   The splitted geometry
        :rtype:     ff.Polygon
        """
        split_line = self.get_center_line(extended=False)

        split_line = split_line.centering(center=position)

        split_line = split_line.rotate(angle=90, origin=split_line.mid_point)

        split_line = split_line.extend(factor=2)

        external_part = utils.Union(geometry.copy()).remove_non_polygon_elements().keep_largest_polygon()

        return external_part.split_with_line(line=split_line, return_largest=return_largest)

    def compute_area_mismatch_cost(self, x: float = 0.5) -> float:
        line = self.get_center_line(extended=True)
        position0 = line.get_position_parametrization(1 - x)
        position1 = line.get_position_parametrization(x)

        small_section = self.split_geometry(
            geometry=self.total_area,
            position=position0,
            return_largest=False
        )

        cost = abs(small_section.area - self[0].area / 2.)

        self.core_shift = (position0 - self[0].center), (position1 - self[1].center)

        logging.info(f'Core positioning optimization: {x = :+.2f} \t -> \t{cost = :<10.2e} -> \t\t core shift: {self.core_shift[0].x, self.core_shift[0].y}')

        return cost

    def optimize_core_position(self) -> None:
        minimize_scalar(
            self.compute_area_mismatch_cost,
            bounds=(0.50001, 0.99),
            method='bounded',
            options={'xatol': 1e-10}
        )

        self[0].shifted_core = self[0].shifted_core + self.core_shift[0]

        self[1].shifted_core = self[1].shifted_core + self.core_shift[1]

# -

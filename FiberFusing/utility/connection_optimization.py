#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Built-in imports
import logging
from scipy.optimize import minimize_scalar
from itertools import combinations

# Local imports
from FiberFusing.connection import Connection
from FiberFusing.buffer import Polygon
from FiberFusing import utils


class ConnectionOptimization():
    _added_section = None
    _removed_section = None

    @property
    def added_section(self):
        if self._added_section is None:
            self._added_section = self.get_added_section()

        return self._added_section

    @property
    def removed_section(self):
        if self._removed_section is None:
            self._removed_section = self.get_removed_section()

        return self._removed_section

    def iterate_over_connected_fibers(self) -> tuple:
        """ TODO: check if the fiber in connections are linked to fiber_list
        Just like the name implies, generator that iterate
        over all the connected fibers.

        :returns:   pair of two connected fibers
        :rtype:     tuple
        """
        for fiber0, fiber1 in combinations(self.fiber_list, 2):
            if fiber0.intersection(fiber1).is_empty:
                continue
            else:
                yield fiber0, fiber1

    def shift_connections(self, virtual_shift: float) -> None:
        """
        Set the virtual shift of the virtual circles for each of the
        connections.

        :param      virtual_shift:  The shift of virtual circles
        :type       virtual_shift:  float
        """
        self.virtual_shift = virtual_shift

        topology = self.get_overall_topology()
        for connection in self.connected_fibers:
            connection.set_shift_and_topology(shift=virtual_shift, topology=topology)

    def get_added_section(self) -> Polygon:
        """
        Returns the added section of the connection

        :returns:   The added section.
        :rtype:     Polygon
        """
        added_section_list = []
        for n, connection in enumerate(self.connected_fibers):
            new_added_section = connection.added_section

            added_section_list.append(new_added_section)

        added_section = utils.Union(*added_section_list) - utils.Union(*self.fiber_list)
        added_section.remove_non_polygon_elements()

        return added_section

    def get_removed_section(self) -> Polygon:
        """
        Retunrs the removed section corresponding to the overlap of the individual circles
        representing the fibers.

        :returns:   The removed section.
        :rtype:     Polygon
        """
        removed_section_list = []
        for connection in self.connected_fibers:
            removed_section_list.append(connection.removed_section)

        removed_section = utils.Union(*removed_section_list)
        return removed_section

    def get_removed_area(self) -> float:
        """
        Retunrs the float value of the removed area.

        :returns:   The removed area.
        :rtype:     float
        """
        disconnected_fibers_area = len(self.fiber_list) * self.fiber_list[0].area

        connected_fibers_area = utils.Union(*self.fiber_list).area

        return disconnected_fibers_area - connected_fibers_area

    def init_connected_fibers(self) -> None:
        """
        Generate the connections (every pair of connnected fibers).
        """
        self.connected_fibers = []

        for fiber_0, fiber_1 in self.iterate_over_connected_fibers():
            connection = Connection(fiber_0, fiber_1)
            self.connected_fibers.append(connection)

    def get_overall_topology(self) -> str:
        """
        Compute the overall topology of the structure

        :returns:   The topology either 'concave' or 'convex'.
        :rtype:     str
        """
        limit = []
        for connection in self.connected_fibers:
            limit.append(connection.limit_added_area)

        overall_limit = utils.Union(*limit) - utils.Union(*self.fiber_list)

        total_removed_area = self.get_removed_area()

        topology = 'convex' if total_removed_area > overall_limit.area else 'concave'

        return topology

    def compute_optimal_core_positions(self) -> None:
        """
        Optimize one round for the core positions of each connections.
        """
        logging.info("Computing the optimal core positions")

        for connection in self.connected_fibers:
            connection.optimize_core_position()

    def get_cost_value(self, virtual_shift: float) -> float:
        """
        Gets the cost value which is the difference between removed section
        and added section for a given virtual circle shift.

        :param      virtual_shift:  The shift of the virtual circles
        :type       virtual_shift:  float

        :returns:   The cost value.
        :rtype:     float
        """

        self.shift_connections(virtual_shift=virtual_shift)

        added_section_area = self.get_added_section().area

        removed_section_area = self.get_removed_area()

        cost = abs(added_section_area - removed_section_area)

        logging.debug(f'Fusing optimization: {virtual_shift = :.2e} \t -> \t{added_section_area = :.2e} \t -> {removed_section_area = :.2e} \t -> {cost = :.2e}')

        return cost

    def optimize_virtual_shift(self, bounds: tuple) -> float:
        """
        Compute the optimized geometry such that mass is conserved.
        Does not compute the core movment.

        :param      bounds:  The virtual shift boundaries
        :type       bounds:  tuple

        :returns:   The optimal virtual shift.
        :rtype:     float
        """
        if len(self.connected_fibers) == 0:
            logging.warning('No connected fibers are found. Continuing.')
            return 0

        core_distance = self.connected_fibers[0].distance_between_cores
        bounds = (0, core_distance * 1e3) if bounds is None else bounds

        res = minimize_scalar(
            self.get_cost_value,
            bounds=bounds,
            method='bounded',
            options={'xatol': core_distance * self.tolerance_factor}
        )

        return res.x

    def compute_optimal_structure(self, bounds: tuple = None) -> None:
        """
        Compute the optimized geometry such that mass is conserved and return the optimal geometry.
        Does not compute the core movment.

        :param      bounds:  The virtual shift boundaries
        :type       bounds:  tuple

        :returns:   The optimize geometry.
        :rtype:     buffer.Polygon
        """
        logging.info("Computing the optimal structure geometry")

        optimal_virtual_shift = self.optimize_virtual_shift(bounds=bounds)

        self._clad_structure = self.get_shifted_geometry(virtual_shift=optimal_virtual_shift)

        self.compute_optimal_core_positions()

    def get_shifted_geometry(self, virtual_shift: float) -> Polygon:
        """
        Returns the clad geometry for a certain shift value.

        :param      virtual_shift:  The shift value
        :type       virtual_shift:  float

        :returns:   The optimized geometry.
        :rtype:     Polygon
        """

        added_section = self.get_added_section()

        opt_geometry = utils.Union(*self.fiber_list, added_section)

        return opt_geometry

# -

from typing import Tuple
import logging
from scipy.optimize import minimize_scalar
from itertools import combinations
from FiberFusing.connection import Connection
from FiberFusing.buffer import Polygon
from FiberFusing import utils


class ConnectionOptimization:
    """
    Class for optimizing the geometry and core positions of connected fibers in a fused structure.

    This class provides methods for computing the optimal configuration of fiber connections,
    such that mass conservation and structural constraints are maintained.

    Attributes
    ----------
    _added_section : Polygon or None
        Cached value of the added section, computed when first accessed.
    _removed_section : Polygon or None
        Cached value of the removed section, computed when first accessed.
    fiber_list : list
        List of fibers in the structure.
    connected_fibers : list
        List of `Connection` objects representing connected fibers in the structure.

    Methods
    -------
    iterate_over_connected_fibers()
        Generator that iterates over all connected fiber pairs.
    shift_connections(virtual_shift)
        Sets the shift of virtual circles for each connection based on the topology.
    get_added_section()
        Computes the added section of the connection.
    get_removed_section()
        Computes the removed section corresponding to the overlap of the fibers.
    get_removed_area()
        Returns the total area of the removed sections.
    init_connected_fibers()
        Initializes the list of connected fibers.
    get_overall_topology()
        Determines the overall topology of the structure ('concave' or 'convex').
    optimize_core_positions()
        Optimizes the core positions for each connection.
    get_cost_value(virtual_shift)
        Computes the cost value based on the area difference between removed and added sections.
    find_optimal_virtual_shift(bounds)
        Optimizes the virtual shift to minimize the cost value.
    compute_optimal_structure(bounds=None)
        Computes the optimized geometry and returns the optimal configuration.
    compute_shifted_geometry(virtual_shift)
        Returns the clad geometry for a given shift value.
    """

    _added_section = None
    _removed_section = None

    @property
    def added_section(self):
        """Polygon: The added section of the connection, computed lazily."""
        if self._added_section is None:
            self._added_section = self.get_added_section()
        return self._added_section

    @property
    def removed_section(self):
        """Polygon: The removed section of the connection, computed lazily."""
        if self._removed_section is None:
            self._removed_section = self.get_removed_section()
        return self._removed_section

    def iterate_over_connected_fibers(self) -> Tuple:
        """
        Generator that iterates over all connected fibers in the structure.

        Yields
        ------
        tuple
            A pair of connected fibers.
        """
        for fiber0, fiber1 in combinations(self.fiber_list, 2):
            if not fiber0.intersection(fiber1).is_empty:
                yield fiber0, fiber1

    def shift_connections(self, virtual_shift: float) -> None:
        """
        Sets the shift of virtual circles for each connection based on the topology.

        Parameters
        ----------
        virtual_shift : float
            The shift value for the virtual circles.
        """
        self.virtual_shift = virtual_shift
        topology = self.get_overall_topology()
        for connection in self.connected_fibers:
            connection.set_shift_and_topology(shift=virtual_shift, topology=topology)

    def get_added_section(self) -> Polygon:
        """
        Computes and returns the added section of the connection.

        Returns
        -------
        Polygon
            The added section as a polygon.
        """
        added_section_list = [conn.added_section for conn in self.connected_fibers]
        added_section = utils.union_geometries(*added_section_list) - utils.union_geometries(*self.fiber_list)
        added_section.remove_non_polygon_elements()
        return added_section

    def get_removed_section(self) -> Polygon:
        """
        Computes and returns the removed section corresponding to the overlap of fibers.

        Returns
        -------
        Polygon
            The removed section as a polygon.
        """
        removed_section_list = [conn.removed_section for conn in self.connected_fibers]
        return utils.union_geometries(*removed_section_list)

    def get_removed_area(self) -> float:
        """
        Computes and returns the total area of the removed sections.

        Returns
        -------
        float
            The total removed area.
        """
        disconnected_area = len(self.fiber_list) * self.fiber_list[0].area
        connected_area = utils.union_geometries(*self.fiber_list).area
        return disconnected_area - connected_area

    def init_connected_fibers(self) -> None:
        """
        Initializes the connections between pairs of fibers in the structure.
        """
        self.connected_fibers = [Connection(f0, f1) for f0, f1 in self.iterate_over_connected_fibers()]

    def get_overall_topology(self) -> str:
        """
        Determines the overall topology of the structure based on the added and removed areas.

        Returns
        -------
        str
            The overall topology ('concave' or 'convex').
        """
        limit = [conn.limit_added_area for conn in self.connected_fibers]
        overall_limit = utils.union_geometries(*limit) - utils.union_geometries(*self.fiber_list)
        total_removed_area = self.get_removed_area()
        return 'convex' if total_removed_area > overall_limit.area else 'concave'

    def optimize_core_positions(self) -> None:
        """
        Optimizes the core positions for each connection in the structure.
        """
        logging.info("Computing the optimal core positions")
        for connection in self.connected_fibers:
            connection.optimize_core_position()

    def get_cost_value(self, virtual_shift: float) -> float:
        """
        Computes the cost value based on the difference between added and removed areas.

        Parameters
        ----------
        virtual_shift : float
            The shift value for the virtual circles.

        Returns
        -------
        float
            The computed cost value.
        """
        self.shift_connections(virtual_shift)
        added_area = self.get_added_section().area
        removed_area = self.get_removed_area()
        cost = abs(added_area - removed_area)
        logging.debug(f'Fusing optimization: virtual_shift={virtual_shift:.2e} -> added_area={added_area:.2e} -> removed_area={removed_area:.2e} -> cost={cost:.2e}')
        return cost

    def find_optimal_virtual_shift(self, bounds: tuple) -> float:
        """
        Optimizes the virtual shift to minimize the cost value.

        Parameters
        ----------
        bounds : tuple
            The boundaries for the virtual shift.

        Returns
        -------
        float
            The optimal virtual shift value.
        """
        if not self.connected_fibers:
            logging.warning('No connected fibers found. Skipping optimization.')
            return 0

        core_distance = self.connected_fibers[0].distance_between_cores
        bounds = (0, core_distance * 1e3) if bounds is None else bounds

        result = minimize_scalar(
            self.get_cost_value,
            bounds=bounds,
            method='bounded',
            options={'xatol': core_distance * self.tolerance_factor}
        )
        return result.x

    def compute_optimal_structure(self, bounds: tuple = None) -> None:
        """
        Computes the optimized geometry and updates the structure configuration.

        Parameters
        ----------
        bounds : tuple, optional
            The boundaries for the virtual shift.
        """
        logging.info("Computing the optimal structure geometry")
        self.find_optimal_virtual_shift(bounds)
        self._clad_structure = self.compute_shifted_geometry()
        self.optimize_core_positions()

    def compute_shifted_geometry(self) -> Polygon:
        """
        Computes the clad geometry for a given virtual shift.

        Parameters
        ----------
        virtual_shift : float
            The shift value for the virtual circles.

        Returns
        -------
        Polygon
            The optimized clad geometry.
        """
        added_section = self.get_added_section()
        return utils.union_geometries(*self.fiber_list, added_section)

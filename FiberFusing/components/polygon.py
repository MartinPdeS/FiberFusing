#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from typing import Iterable, List, Optional, Union, Tuple
from matplotlib.path import Path
import shapely.geometry as geo
import matplotlib.pyplot as plt
from FiberFusing.coordinate_system import CoordinateSystem
from FiberFusing.components.base_class import BaseArea
from FiberFusing.plottings import plot_polygon
from pydantic import ConfigDict
from FiberFusing.helper import _plot_helper

config = ConfigDict(extra='forbid', arbitrary_types_allowed=True, kw_only=True)


class Polygon(BaseArea):
    """
    Represents a polygon using either a set of coordinates or a Shapely Polygon instance.

    Parameters
    ----------
    coordinates : list of tuple of float, optional
        A list of (x, y) tuples representing the coordinates of the polygon.
    instance : geo.Polygon or geo.MultiPolygon, optional
        An existing Shapely Polygon or MultiPolygon instance.
    index : float, optional
        An optional numerical index associated with the polygon.

    Raises
    ------
    ValueError
        If neither coordinates nor instance is provided or if both are provided.
    """
    def __init__(
            self,
            coordinates: Optional[List[Tuple[float, float]]] = None,
            instance: Optional[Union[geo.Polygon, geo.MultiPolygon]] = None,
            index: Optional[float] = None):

        if not ((coordinates is None) ^ (instance is None)):
            raise ValueError('Polygon must be initialized with either coordinates or an instance')

        if coordinates is not None:
            self._shapely_object = geo.Polygon(coordinates)
        else:
            self._shapely_object = instance

        self.index = index

    @property
    def interiors(self):
        """
        Retrieves the interior coordinates of the polygon.

        Returns
        -------
        Iterable
            An iterable of coordinates that define the interior boundaries of the polygon.
        """
        return self._shapely_object.interiors

    def get_hole(self) -> geo.Polygon:
        """
        Retrieves the holes within the polygon as a new Polygon object.

        Returns
        -------
        geo.Polygon
            A polygon representing the holes, or an empty polygon if no holes exist.
        """
        if isinstance(self._shapely_object, geo.MultiPolygon):
            return EmptyPolygon()

        output = self.copy()

        if isinstance(output.interiors, Iterable):
            from FiberFusing.components.utils import get_polygon_union
            polygons = [geo.Polygon(c) for c in output.interiors]
            output = get_polygon_union(*polygons)
        else:
            output._shapely_object = geo.Polygon(*output.interiors)

        return output

    def contains_points(self, coordinates: np.ndarray) -> np.ndarray:
        """
        Checks which of the provided coordinates lie within the polygon or multipolygon,
        excluding any holes.

        Parameters
        ----------
        coordinates : np.ndarray
            An array of coordinates to check against the polygon or multipolygon.

        Returns
        -------
        np.ndarray
            A boolean array where True indicates that the coordinate is inside the polygon
            or multipolygon (excluding any holes) and False indicates that it is outside or within a hole.
        """
        inclusion_mask = np.zeros(coordinates.shape[0], dtype=bool)

        if isinstance(self._shapely_object, geo.MultiPolygon):
            for polygon in self._shapely_object.geoms:
                inclusion_mask |= self._contain_points_with_holes(coordinates=coordinates, polygon=polygon)
        elif isinstance(self._shapely_object, geo.Polygon):
            inclusion_mask = self._contain_points_with_holes(coordinates=coordinates, polygon=self._shapely_object)
        else:
            raise TypeError("Input geometry must be a Polygon or MultiPolygon.")

        return inclusion_mask

    def _contain_points_with_holes(self, coordinates: np.ndarray, polygon: geo.Polygon) -> np.ndarray:
        """
        Determines if the given coordinates are contained within the exterior of the specified polygon,
        excluding any points that fall inside the holes (interiors).

        Parameters
        ----------
        coordinates : np.ndarray
            An array of 2D coordinates, where each row represents a point (x, y).
        polygon : geo.Polygon
            A Shapely Polygon object whose exterior and interiors will be used to test point containment.

        Returns
        -------
        np.ndarray
            A boolean array where each element is True if the corresponding coordinate is inside
            the polygon's exterior but not inside any of its holes, and False otherwise.
        """
        # Create a Matplotlib Path object from the polygon's exterior coordinates
        path_exterior = Path(np.array(polygon.exterior.coords))
        exterior_mask = path_exterior.contains_points(coordinates)

        # If the polygon has interiors (holes), check if any points fall inside them
        hole_mask = np.zeros(coordinates.shape[0], dtype=bool)
        for interior in polygon.interiors:
            path_hole = Path(np.array(interior.coords))
            hole_mask |= path_hole.contains_points(coordinates)

        # Points are inside if they are in the exterior but not in any hole
        return exterior_mask & ~hole_mask

    @_plot_helper
    def plot(self, ax: plt.Axes, **kwargs) -> None:
        """
        Plots the polygon on the given Matplotlib axis.

        Parameters
        ----------
        ax : plt.Axes
            The Matplotlib axis where the polygon should be plotted.
        **kwargs
            Additional keyword arguments passed to the plotting function.
        """
        plot_polygon(ax=ax, polygon=self._shapely_object, **kwargs)

    def rasterize(self, coordinate_system: CoordinateSystem) -> np.ndarray:
        """
        Rasterizes the polygon to a grid based on a coordinate system.

        Parameters
        ----------
        coordinate_system : CoordinateSystem
            The coordinate system used for rasterization.

        Returns
        -------
        np.ndarray
            A 2D array where 1 indicates the presence of the polygon and 0 indicates its absence.
        """
        unstructured_coordinates = coordinate_system.to_unstructured_coordinate()
        exterior_mask = self.contains_points(unstructured_coordinates)
        hole = self.get_hole()
        hole_mask = np.zeros(exterior_mask.shape, dtype=bool)

        if isinstance(hole, Iterable):
            for sub_hole in hole.geoms:
                hole_mask |= sub_hole.contains_points(unstructured_coordinates)
        elif not hole.is_empty:
            hole_mask = hole.contains_points(unstructured_coordinates)

        return np.where(exterior_mask & ~hole_mask, 1, 0).reshape(coordinate_system.shape)

    def remove_non_polygon_elements(self) -> 'Polygon':
        """
        Removes non-polygon elements from the geometry.

        Filters out elements that are not Polygon or MultiPolygon from the current geometry.

        Returns
        -------
        Polygon
            The instance of this class with only polygon elements retained.
        """
        if isinstance(self._shapely_object, geo.GeometryCollection):
            filtered_geometries = [
                geom for geom in self._shapely_object.geoms if isinstance(geom, (geo.Polygon, geo.MultiPolygon))
            ]
            self._shapely_object = geo.MultiPolygon(filtered_geometries)
        return self

    def keep_largest_polygon(self) -> 'Polygon':
        """
        Retains only the largest polygon in the geometry.

        If the geometry is a MultiPolygon, it keeps the one with the largest area.

        Returns
        -------
        Polygon
            The instance of this class with the largest polygon retained.
        """
        if isinstance(self._shapely_object, geo.MultiPolygon):
            largest_polygon = max(self._shapely_object.geoms, key=lambda poly: poly.area)
            self._shapely_object = largest_polygon
        return self


class EmptyPolygon(Polygon):
    """
    A representation of an empty polygon.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(instance=geo.Polygon(), *args, **kwargs)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy
from typing import Iterable, List, Optional, Union, Tuple
from matplotlib.path import Path
import shapely.geometry as geo
import matplotlib.pyplot as plt
from FiberFusing.coordinate_system import CoordinateSystem
from FiberFusing.components.base_class import BaseArea
from FiberFusing.plottings import plot_polygon
from pydantic.dataclasses import dataclass
from dataclasses import field
from pydantic import ConfigDict
from FiberFusing.helper import _plot_helper

config = ConfigDict(extra='forbid', arbitrary_types_allowed=True, kw_only=True)


@dataclass(config=config)
class Polygon(BaseArea):
    """
    Initialize a Polygon instance with a set of coordinates or an existing Shapely Polygon.

    Parameters
    ----------
    coordinates : list, optional
        A list of tuples representing the x, y coordinate pairs.
    instance : geo.Polygon, optional
        An existing Shapely Polygon object.
    index : float, optional
        A numerical index associated with the polygon.

    Raises:
        ValueError: If neither coordinates nor instance is provided.
    """
    coordinates: Optional[List[Tuple[float, float]]] = field(default=None, repr=False)
    instance: Optional[Union[geo.Polygon, geo.MultiPolygon]] = field(default=None, repr=False)
    index: Optional[float] = field(default=None)

    def __post_init__(self):
        if not ((self.coordinates is None) ^ (self.instance is None)):
            raise ValueError('Polygon must be initialized with either coordinate or instance')

        self._shapely_object = geo.Polygon(self.coordinates) if self.coordinates is not None else self.instance

    def get_hole(self) -> geo.Polygon:
        """
        Retrieve any holes within the polygon as a new Polygon object.

        Returns:
            geo.Polygon: A polygon representing the holes, or an empty polygon if no holes exist.
        """
        if isinstance(self._shapely_object, geo.MultiPolygon):
            return EmptyPolygon()

        output = self.copy()

        if isinstance(output.interiors, Iterable):
            from FiberFusing.components.utils import get_polygon_union
            polygon = [geo.Polygon(c) for c in output.interiors]
            output = get_polygon_union(*polygon)
        else:
            output._shapely_object = geo.Polygon(*output.interiors)

        return output

    @property
    def interiors(self):
        """
        Retrieve the interior coordinates of the polygon.

        Returns:
            Iterable: An iterable of coordinates that define the interior boundaries of the polygon.
        """
        return self._shapely_object.interiors

    def remove_non_polygon_elements(self) -> 'Polygon':
        """
        Filters out non-polygon elements from a GeometryCollection or MultiPolygon.

        This method modifies the current geometry to include only Polygon or MultiPolygon
        elements, effectively removing any other shapes (like lines or points) that may
        be present in a GeometryCollection.

        Returns:
            Polygon: The instance of this class with the updated geometry.
        """
        if isinstance(self._shapely_object, geo.GeometryCollection):
            # Filter to keep only Polygon and MultiPolygon objects
            filtered_geometries = [
                geom for geom in self._shapely_object.geoms if isinstance(geom, (geo.Polygon, geo.MultiPolygon))
            ]
            self._shapely_object = geo.MultiPolygon(filtered_geometries)

        return self

    def keep_largest_polygon(self) -> 'Polygon':
        """
        Updates the instance's geometry to retain only the largest polygon.

        This is applicable when the current geometry is a MultiPolygon. This method
        finds the polygon with the largest area and updates the instance's geometry
        to this largest polygon, discarding all others.

        Returns:
            Polygon: The instance of this class with the updated geometry.
        """
        if isinstance(self._shapely_object, geo.MultiPolygon):
            # Find the index of the polygon with the largest area
            largest_polygon = max(self._shapely_object.geoms, key=lambda poly: poly.area)
            self._shapely_object = largest_polygon

        return self

    @_plot_helper
    def plot(self, ax: plt.Axes, **kwargs) -> None:
        """
        Render the Polygon on a specific axis.

        :param      ax:   The axis to which add the plot
        :type       ax:   plt.Axes

        :returns:   No return
        :rtype:     None
        """
        # TODO: rings -> https://sgillies.net/2010/04/06/painting-punctured-polygons-with-matplotlib.html

        if isinstance(self._shapely_object, geo.MultiPolygon):
            for polygon in self._shapely_object.geoms:
                plot_polygon(ax, polygon, **kwargs)

        else:
            plot_polygon(ax, self._shapely_object, **kwargs)

    def rasterize(self, coordinate_system: CoordinateSystem) -> numpy.ndarray:
        """
        Rasterizes the polygon using a specified coordinate system to generate a mesh grid.

        Parameters:
            coordinate_system (CoordinateSystem): The coordinate system to use for rasterization.

        Returns:
            numpy.ndarray: A 2D array representing the rasterized form of the polygon,
                           where 1 indicates the presence of the polygon and 0 indicates absence.
        """
        unstructured_coordinates = coordinate_system.to_unstructured_coordinate()

        # Get a boolean mask where points are inside the polygon's exterior
        exterior_mask = self.contains_points(unstructured_coordinates)

        # Retrieve the hole of the polygon if any and create a mask for it
        hole = self.get_hole()
        hole_mask = numpy.zeros(exterior_mask.shape, dtype=bool)

        if isinstance(hole, Iterable):
            for sub_hole in hole.geoms:
                hole_mask |= sub_hole.contains_points(unstructured_coordinates)
        elif not hole.is_empty:
            hole_mask = hole.contains_points(unstructured_coordinates)

        return numpy.where(exterior_mask & ~hole_mask, 1, 0)

    def contains_points(self, coordinates: numpy.ndarray) -> numpy.ndarray:
        """
        Determines which of the provided coordinates lie within the polygon.

        Parameters:
            coordinates (numpy.ndarray): An array of coordinates to check against the polygon.

        Returns:
            numpy.ndarray: A boolean array where True indicates that the coordinate is inside the polygon.
        """
        # Initialize a boolean array for storing point inclusion results
        inclusion_mask = numpy.zeros(coordinates.shape[0], dtype=bool)

        if isinstance(self._shapely_object, geo.MultiPolygon):
            for polygon in self._shapely_object.geoms:
                inclusion_mask += self._contain_points(coordinates=coordinates, polygon=polygon)

        else:
            inclusion_mask = self._contain_points(coordinates=coordinates, polygon=self._shapely_object)

        return inclusion_mask

    def _contain_points(self, coordinates: numpy.ndarray, polygon: geo.Polygon) -> numpy.ndarray:
        """
        Determines if the given coordinates are contained within the exterior of the specified polygon.

        This method utilizes Matplotlib's Path object, which is efficient for point-in-polygon tests.

        Parameters:
            coordinates (numpy.ndarray): An array of 2D coordinates, where each row represents a point (x, y).
            polygon (Polygon): A Shapely Polygon object whose exterior will be used to test point containment.

        Returns:
            numpy.ndarray: A boolean array where each element is True if the corresponding coordinate is inside
                           the polygon's exterior, and False otherwise.
        """
        # Create a Matplotlib Path object from the polygon's exterior coordinates
        path_exterior = Path(numpy.array(polygon.exterior.coords))

        # Use the Path object to check if points are inside the polygon's exterior
        return path_exterior.contains_points(coordinates).astype(bool)


class _Polygon(BaseArea):
    def __post_init__(self):
        if (self.coordinates is None) ^ (self.instance is None):
            raise ValueError('Polygon must be initialized with either coordinate or instance')

        self._shapely_object = geo.Polygon(self.coordinates) if self.coordinates is not None else self.instance

    def get_hole(self) -> geo.Polygon:
        """
        Retrieve any holes within the polygon as a new Polygon object.

        Returns:
            geo.Polygon: A polygon representing the holes, or an empty polygon if no holes exist.
        """
        if isinstance(self._shapely_object, geo.MultiPolygon):
            return EmptyPolygon()

        output = self.copy()

        if isinstance(output.interiors, Iterable):
            from FiberFusing.components.utils import get_polygon_union
            polygon = [geo.Polygon(c) for c in output.interiors]
            output = get_polygon_union(*polygon)
        else:
            output._shapely_object = geo.Polygon(*output.interiors)

        return output

    @property
    def interiors(self):
        """
        Retrieve the interior coordinates of the polygon.

        Returns:
            Iterable: An iterable of coordinates that define the interior boundaries of the polygon.
        """
        return self._shapely_object.interiors

    def remove_non_polygon_elements(self) -> 'Polygon':
        """
        Filters out non-polygon elements from a GeometryCollection or MultiPolygon.

        This method modifies the current geometry to include only Polygon or MultiPolygon
        elements, effectively removing any other shapes (like lines or points) that may
        be present in a GeometryCollection.

        Returns:
            Polygon: The instance of this class with the updated geometry.
        """
        if isinstance(self._shapely_object, geo.GeometryCollection):
            # Filter to keep only Polygon and MultiPolygon objects
            filtered_geometries = [
                geom for geom in self._shapely_object.geoms if isinstance(geom, (geo.Polygon, geo.MultiPolygon))
            ]
            self._shapely_object = geo.MultiPolygon(filtered_geometries)

        return self

    def keep_largest_polygon(self) -> 'Polygon':
        """
        Updates the instance's geometry to retain only the largest polygon.

        This is applicable when the current geometry is a MultiPolygon. This method
        finds the polygon with the largest area and updates the instance's geometry
        to this largest polygon, discarding all others.

        Returns:
            Polygon: The instance of this class with the updated geometry.
        """
        if isinstance(self._shapely_object, geo.MultiPolygon):
            # Find the index of the polygon with the largest area
            largest_polygon = max(self._shapely_object.geoms, key=lambda poly: poly.area)
            self._shapely_object = largest_polygon

        return self

    @_plot_helper
    def plot(self, ax: plt.Axes = None, **kwargs) -> None:
        """
        Render the Polygon on a specific axis.

        :param      ax:   The axis to which add the plot
        :type       ax:   plt.Axes

        :returns:   No return
        :rtype:     None
        """
        if isinstance(self._shapely_object, geo.MultiPolygon):
            for polygon in self._shapely_object.geoms:
                plot_polygon(ax=ax, poly=polygon, **kwargs)

        else:
            plot_polygon(ax=ax, poly=self._shapely_object, **kwargs)

    def rasterize(self, coordinate_system: CoordinateSystem) -> numpy.ndarray:
        """
        Rasterizes the polygon using a specified coordinate system to generate a mesh grid.

        Parameters:
            coordinate_system (CoordinateSystem): The coordinate system to use for rasterization.

        Returns:
            numpy.ndarray: A 2D array representing the rasterized form of the polygon,
                           where 1 indicates the presence of the polygon and 0 indicates absence.
        """
        unstructured_coordinates = coordinate_system.to_unstructured_coordinate()

        # Get a boolean mask where points are inside the polygon's exterior
        exterior_mask = self.contains_points(unstructured_coordinates)

        # Retrieve the hole of the polygon if any and create a mask for it
        hole = self.get_hole()
        hole_mask = numpy.zeros(exterior_mask.shape, dtype=bool)

        if isinstance(hole, Iterable):
            for sub_hole in hole.geoms:
                hole_mask |= sub_hole.contains_points(unstructured_coordinates)
        elif not hole.is_empty:
            hole_mask = hole.contains_points(unstructured_coordinates)

        return numpy.where(exterior_mask & ~hole_mask, 1, 0)

    def contains_points(self, coordinates: numpy.ndarray) -> numpy.ndarray:
        """
        Determines which of the provided coordinates lie within the polygon.

        Parameters:
            coordinates (numpy.ndarray): An array of coordinates to check against the polygon.

        Returns:
            numpy.ndarray: A boolean array where True indicates that the coordinate is inside the polygon.
        """
        # Initialize a boolean array for storing point inclusion results
        inclusion_mask = numpy.zeros(coordinates.shape[0], dtype=bool)

        if isinstance(self._shapely_object, geo.MultiPolygon):
            for polygon in self._shapely_object.geoms:
                inclusion_mask += self._contain_points(coordinates=coordinates, polygon=polygon)

        else:
            inclusion_mask = self._contain_points(coordinates=coordinates, polygon=self._shapely_object)

        return inclusion_mask

    def _contain_points(self, coordinates: numpy.ndarray, polygon: geo.Polygon) -> numpy.ndarray:
        """
        Determines if the given coordinates are contained within the exterior of the specified polygon.

        This method utilizes Matplotlib's Path object, which is efficient for point-in-polygon tests.

        Parameters:
            coordinates (numpy.ndarray): An array of 2D coordinates, where each row represents a point (x, y).
            polygon (Polygon): A Shapely Polygon object whose exterior will be used to test point containment.

        Returns:
            numpy.ndarray: A boolean array where each element is True if the corresponding coordinate is inside
                           the polygon's exterior, and False otherwise.
        """
        # Create a Matplotlib Path object from the polygon's exterior coordinates
        path_exterior = Path(numpy.array(polygon.exterior.coords))

        # Use the Path object to check if points are inside the polygon's exterior
        return path_exterior.contains_points(coordinates).astype(bool)


class EmptyPolygon(Polygon):
    def __init__(self, *args, **kwargs):
        super().__init__(instance=geo.Polygon(), *args, **kwargs)

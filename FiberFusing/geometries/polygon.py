#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Iterable, List, Optional, Union, Tuple, Self
import numpy as np
from matplotlib.path import Path
import shapely.geometry as geo
import matplotlib.pyplot as plt
from shapely.ops import split
from shapely import affinity
from MPSPlots import helper

from FiberFusing.coordinate_system import CoordinateSystem
from FiberFusing.plottings import plot_polygon
from FiberFusing import geometries

class Polygon(geometries.base_class.Alteration):
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
            from FiberFusing.geometries.utils import get_polygon_union
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

    @helper.pre_plot(nrows=1, ncols=1)
    def plot(self, axes: plt.Axes, **kwargs) -> None:
        """
        Plots the polygon on the given Matplotlib axis.

        Parameters
        ----------
        ax : plt.Axes
            The Matplotlib axis where the polygon should be plotted.
        **kwargs
            Additional keyword arguments passed to the plotting function.
        """
        plot_polygon(ax=axes, polygon=self._shapely_object, **kwargs)

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
        unstructured_coordinates = coordinate_system.get_coordinates_flattened()
        exterior_mask = self.contains_points(unstructured_coordinates)
        hole = self.get_hole()
        hole_mask = np.zeros(exterior_mask.shape, dtype=bool)

        if isinstance(hole, Iterable):
            for sub_hole in hole.geoms:
                hole_mask |= sub_hole.contains_points(unstructured_coordinates)
        elif not hole.is_empty:
            hole_mask = hole.contains_points(unstructured_coordinates)

        return np.where(exterior_mask & ~hole_mask, 1, 0).reshape(coordinate_system.shape)

    def remove_non_polygon_elements(self) -> Self:
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

    def keep_largest_polygon(self) -> Self:
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

    @property
    def is_iterable(self) -> bool:
        """
        Check if the shapely object is iterable.

        Returns
        -------
        bool
            True if the object is iterable, False otherwise.
        """
        return isinstance(self._shapely_object, Iterable)

    @property
    def is_multi(self) -> bool:
        """
        Check if the shapely object is a MultiPolygon.

        Returns
        -------
        bool
            True if the object is a MultiPolygon, False otherwise.
        """
        return isinstance(self._shapely_object, geo.MultiPolygon)

    @property
    def is_empty(self) -> bool:
        """
        Check if the shapely object is empty.

        Returns
        -------
        bool
            True if the object is empty, False otherwise.
        """
        return self._shapely_object.is_empty

    @property
    def is_pure_polygon(self) -> bool:
        """
        Check if the shapely object is a pure Polygon.

        Returns
        -------
        bool
            True if the object is a pure Polygon, False otherwise.
        """
        return isinstance(self._shapely_object, geo.Polygon)

    @property
    def exterior(self):
        """
        Get the exterior boundary of the polygon.

        Returns
        -------
        LinearRing
            The exterior boundary of the polygon.
        """
        return self._shapely_object.exterior

    def get_rasterized_mesh(self, coordinate_system: CoordinateSystem) -> np.ndarray:
        """
        Rasterize the shape based on the given coordinate system.

        Parameters
        ----------
        coordinate_system : CoordinateSystem
            The coordinate system used for rasterization.

        Returns
        -------
        numpy.ndarray
            The rasterized shape as a mesh.
        """
        raster = self.rasterize(coordinate_system=coordinate_system)
        raster = raster.reshape(coordinate_system.shape)
        return raster.astype(np.float64)

    @property
    def convex_hull(self) -> geo.Polygon:
        """
        Get the convex hull of the shape.

        Returns
        -------
        Polygon
            The convex hull as a Polygon.
        """
        return geometries.Polygon(instance=self._shapely_object.convex_hull)

    @property
    def area(self) -> float:
        """
        Calculate the area of the shape.

        Returns
        -------
        float
            The area of the shape.
        """
        return self._shapely_object.area

    @property
    def bounds(self) -> Tuple[float, float, float, float]:
        """
        Get the bounds of the shape.

        Returns
        -------
        tuple of float
            The (minx, miny, maxx, maxy) bounds of the shape.
        """
        return self._shapely_object.bounds

    @property
    def center(self) -> geo.Point:
        """
        Get the center (centroid) of the shape.

        Returns
        -------
        Point
            The centroid of the shape as a Point.
        """
        return geometries.Point(position=(self._shapely_object.centroid.x, self._shapely_object.centroid.y))

    def __add__(self, other: Self) -> Self:
        """
        Add two geometries together using union.

        Parameters
        ----------
        other : Polygon
            The other geometry to union with.

        Returns
        -------
        Polygon
            The union of the two geometries.
        """
        output = self.copy()
        output._shapely_object = self._shapely_object.union(other._shapely_object)
        return output

    def __sub__(self, other: Self, tolerance: float = 1e-9) -> Self:
        """
        Subtract one geometry from another.

        Parameters
        ----------
        other : Polygon
            The geometry to subtract.

        Returns
        -------
        Polygon
            The difference of the two geometries.
        """
        output = self.copy()

        buffered_self = self._shapely_object.buffer(tolerance)

        if not buffered_self.intersects(other._shapely_object):
            return self

        output._shapely_object = buffered_self.difference(other._shapely_object)

        return output

    def __and__(self, other: Self) -> Self:
        """
        Perform the intersection operation.

        Parameters
        ----------
        other : Polygon
            The geometry to intersect with.

        Returns
        -------
        Polygon
            The intersection of the two geometries.
        """
        output = self.copy()
        output._shapely_object = self._shapely_object.intersection(other._shapely_object)
        return output

    def scale_position(self, factor: float) -> Self:
        """
        Scale the position of the shape.

        Parameters
        ----------
        factor : float
            The scaling factor for the shape's position.

        Returns
        -------
        Polygon
            The scaled shape.
        """
        new_position = affinity.scale(
            self.center._shapely_object,
            xfact=factor,
            yfact=factor,
            origin=(0, 0)
        )

        shift = (new_position.x - self.center.x, new_position.y - self.center.y)

        self.core.translate(shift=shift, in_place=True)
        self.translate(shift=shift, in_place=True)

        return self

    def shift_position(self, shift: Tuple[float, float], inplace: bool = True) -> Self:
        """
        Shift the position of the shape.

        Parameters
        ----------
        shift : tuple of float
            The (x, y) shift values.

        Returns
        -------
        Polygon
            The shifted shape.
        """
        if hasattr(self, 'core'):
            self.core.translate(shift=shift, in_place=inplace)
        self.translate(shift=shift, in_place=inplace)
        return self

    def split_with_line(self, line, return_largest: bool = True) -> Self:
        """
        Split the shape using a line.

        Parameters
        ----------
        line : LineString
            The line used for splitting the shape.
        return_largest : bool, optional
            If True, returns the largest resulting polygon. Otherwise, returns the smallest. Default is True.

        Returns
        -------
        geometries.Polygon
            The resulting polygon based on the split.

        Raises
        ------
        ValueError
            If the shape is not a pure polygon.
        """
        if not self.is_pure_polygon:
            raise ValueError(f"Error: expected a pure polygon, but got {self._shapely_object.__class__}.")

        split_geometry = split(self._shapely_object, line.copy().extend(factor=100)._shapely_object).geoms
        areas = [poly.area for poly in split_geometry]
        idx = np.argmax(areas) if return_largest else np.argmin(areas)

        return geometries.Polygon(instance=split_geometry[idx])



class EmptyPolygon(Polygon):
    """
    A representation of an empty polygon.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(instance=geo.Polygon(), *args, **kwargs)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy
from FiberFusing import Circle
from FiberFusing import CircleOpticalStructure
import pprint
from copy import deepcopy


pp = pprint.PrettyPrinter(indent=4, sort_dicts=False, compact=True, width=1)


class BaseClass:
    """
    A collection of optical structures representing the full structure of an optical fiber.

    Attributes:
        full_structure (list): Returns the list of all structures.
        fiber_structure (list): Returns the list of structures excluding 'air'.
        refractive_index_list (list): Returns a list of refractive indices of the fiber structures.
        inner_structure (list): Returns the list of structures excluding 'air' and 'outer_clad'.
    """

    @property
    def full_structure(self) -> list:
        """Returns the list of all structures."""
        return self.structure_list

    @property
    def fiber_structure(self) -> list:
        """Returns the list of structures excluding 'air'."""
        return [s for s in self.structure_list if s.name not in ['air']]

    @property
    def refractive_index_list(self) -> list:
        """Returns a list of refractive indices of the fiber structures."""
        return [struct.index for struct in self.fiber_structure]

    @property
    def inner_structure(self) -> list:
        """Returns the list of structures excluding 'air' and 'outer_clad'."""
        return [s for s in self.structure_list if s.name not in ['air', 'outer_clad']]

    def __getitem__(self, idx: int):
        """
        Allows indexing to access specific structures.

        Args:
            idx (int): Index of the structure.

        Returns:
            CircleOpticalStructure: The structure at the specified index.
        """
        return self.structure_list[idx]

    def scale(self, factor: float):
        """
        Scales the radius of each structure by a given factor.

        Args:
            factor (float): The scaling factor.

        Returns:
            BaseStructureCollection: A new scaled version of the collection.
        """
        fiber_copy = deepcopy(self)
        for structure in fiber_copy.structure_list:
            if structure.radius is not None:
                structure.radius *= factor
                new_polygon = Circle(
                    position=structure.position,
                    radius=structure.radius,
                    index=structure.index
                )
                structure.polygon = new_polygon

        return fiber_copy

    def create_and_add_new_structure(self, index: float = None, NA: float = None, **kwargs) -> None:
        """
        Adds a new circular structure to the collection.

        Args:
            index (float, optional): The refractive index of the structure. Defaults to None.
            NA (float, optional): The numerical aperture of the structure. Defaults to None.
            **kwargs: Additional keyword arguments for the structure.

        Returns:
            None
        """
        index = self._interpret_index_or_NA_to_index(index=index, NA=NA)
        new_structure = CircleOpticalStructure(
            **kwargs,
            index=index,
            position=self.position
        )
        setattr(self, new_structure.name, new_structure)
        self.structure_list.append(new_structure)

    def _interpret_index_or_NA_to_index(self, index: float, NA: float) -> float:
        """
        Interprets and converts NA or index to a refractive index.

        Args:
            index (float, optional): The refractive index. Defaults to None.
            NA (float, optional): The numerical aperture. Defaults to None.

        Returns:
            float: The interpreted refractive index.

        Raises:
            ValueError: If NA is provided but no previous layer is defined.
        """
        if (index is not None) == (NA is not None):
            raise ValueError('Only one of NA or index can be defined')

        if index is not None:
            return index

        if len(self.structure_list) == 0:
            raise ValueError('Cannot initialize layer from NA if no previous layer is defined')

        return self.compute_index_from_NA(
            exterior_index=self.structure_list[-1].index,
            NA=NA
        )

    def compute_index_from_NA(self, exterior_index: float, NA: float) -> float:
        """
        Computes refractive index from NA and exterior index.

        Args:
            exterior_index (float): The refractive index of the exterior layer.
            NA (float): The numerical aperture.

        Returns:
            float: The computed refractive index.
        """
        return numpy.sqrt(NA**2 + exterior_index**2)

    def _overlay_structure_on_mesh_(self, structure_list: list, mesh: numpy.ndarray, coordinate_system) -> numpy.ndarray:
        """
        Overlays the structures on a mesh grid based on the coordinate system.

        Args:
            structure_list (list): The list of structures to overlay.
            mesh (numpy.ndarray): The mesh grid.
            coordinate_system (CoordinateSystem): The coordinate system to use.

        Returns:
            numpy.ndarray: The raster mesh of the structures.
        """
        for structure in structure_list:
            raster = structure.polygon.get_rasterized_mesh(coordinate_system=coordinate_system)
            mesh[numpy.where(raster != 0)] = 0

            if structure.is_graded:
                index = self.get_graded_index_mesh(
                    coordinate_system=coordinate_system,
                    polygon=structure.polygon,
                    min_index=structure.index,
                    max_index=structure.index + structure.delta_n
                )
            else:
                index = structure.index

            mesh += raster * index

        return mesh


# -

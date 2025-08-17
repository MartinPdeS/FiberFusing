#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy
from FiberFusing import Circle
from FiberFusing import CircleOpticalStructure
import pprint
from copy import deepcopy


pp = pprint.PrettyPrinter(indent=4, sort_dicts=False, compact=True, width=1)


class BaseFiber:
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

    def create_and_add_new_structure(self, refractive_index: float = None, NA: float = None, **kwargs) -> None:
        """
        Adds a new circular structure to the collection.

        Parameters
        ----------
        refractive_index : float, optional
            The refractive index of the new structure. If provided, NA should be None.
        NA : float, optional
            The numerical aperture of the new structure. If provided, refractive_index should be None.

        Raises
        ------
        ValueError
            If both refractive_index and NA are provided or if neither is provided.
        """
        refractive_index = self._interpret_index_or_NA_to_index(refractive_index=refractive_index, NA=NA)

        new_structure = CircleOpticalStructure(
            **kwargs,
            refractive_index=refractive_index,
            position=self.position
        )
        setattr(self, new_structure.name, new_structure)
        self.structure_list.append(new_structure)

    def create_and_add_new_graded_index_structure(self, refractive_index_in: float, refractive_index_out: float, **kwargs) -> None:
        """
        Adds a new graded index structure to the collection.

        Parameters
        ----------
        refractive_index : float, optional
            The refractive index of the new structure. If provided, NA should be None.
        NA : float, optional
            The numerical aperture of the new structure. If provided, refractive_index should be None.

        Raises
        ------
        ValueError
            If both refractive_index and NA are provided or if neither is provided.
        """
        new_structure = CircleOpticalStructure(
            **kwargs,
            refractive_index_in=refractive_index_in,
            refractive_index_out=refractive_index_out,
            position=self.position
        )
        setattr(self, new_structure.name, new_structure)
        self.structure_list.append(new_structure)


    def _interpret_index_or_NA_to_index(self, refractive_index: float, NA: float) -> float:
        """
        Interprets and converts NA or index to a refractive index.

        Parameters
        ----------
        refractive_index : float, optional
            The refractive index of the structure. If provided, NA should be None.
        NA : float, optional
            The numerical aperture of the structure. If provided, refractive_index should be None.

        Returns
        -------
        float
            The refractive index of the structure.
        """
        if (refractive_index is not None) == (NA is not None):
            raise ValueError('Only one of NA or refractive_index can be defined')

        if refractive_index is not None:
            return refractive_index

        if len(self.structure_list) == 0:
            raise ValueError('Cannot initialize layer from NA if no previous layer is defined')

        return self.compute_index_from_NA(
            exterior_index=self.structure_list[-1].refractive_index,
            NA=NA
        )

    def compute_index_from_NA(self, exterior_index: float, NA: float) -> float:
        """
        Computes refractive index from NA and exterior index.

        Parameters
        ----------
        exterior_index : float
            The refractive index of the exterior medium.
        NA : float
            The numerical aperture of the structure.

        Returns
        -------
        float
            The computed refractive index.
        """
        return numpy.sqrt(NA**2 + exterior_index**2)

    def _overlay_structure_on_mesh_(self, structure_list: list, mesh: numpy.ndarray, coordinate_system) -> numpy.ndarray:
        """
        Overlays the structures on a mesh grid based on the coordinate system.

        Parameters
        ----------
        structure_list : list
            A list of structures to overlay on the mesh.
        mesh : numpy.ndarray
            The mesh grid on which the structures will be overlayed.
        coordinate_system : CoordinateSystem
            The coordinate system used for overlaying the structures.

        Returns
        -------
        numpy.ndarray
            A numpy ndarray with the structures overlayed onto the original mesh.
        """
        for structure in structure_list:
            raster = structure.polygon.get_rasterized_mesh(coordinate_system=coordinate_system)
            mesh[numpy.where(raster != 0)] = 0

            if structure.is_graded:
                refractive_index = self.get_graded_index_mesh(
                    coordinate_system=coordinate_system,
                    polygon=structure.polygon,
                    min_index=structure.refractive_index_in,
                    max_index=structure.refractive_index_out
                )
            else:
                refractive_index = structure.refractive_index

            mesh += raster * refractive_index

        return mesh


# -

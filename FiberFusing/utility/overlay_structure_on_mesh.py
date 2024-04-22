#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Built-in imports
import numpy


class OverlayStructureBaseClass:
    def _overlay_structure_on_mesh_(self, structure_list: dict, mesh: numpy.ndarray, coordinate_system: object) -> numpy.ndarray:
        """
        Return a mesh overlaying all the structures in the order they were defined.

        :param      coordinate_system:  The coordinates axis
        :type       coordinate_system:  Axis

        :returns:   The raster mesh of the structures.
        :rtype:     numpy.ndarray
        """
        for structure in structure_list:
            polygon = structure.polygon
            raster = polygon.get_rasterized_mesh(coordinate_system=coordinate_system)
            mesh[numpy.where(raster != 0)] = 0
            index = structure.index

            if hasattr(structure, 'graded_index_factor'):
                index += self.get_graded_index_mesh(
                    coordinate_system=coordinate_system,
                    polygon=polygon,
                    delta_n=structure.graded_index_factor
                )

            raster *= index

            mesh += raster

        return mesh

# -

#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Third-party imports
import numpy
from dataclasses import dataclass, field
from scipy.ndimage import gaussian_filter

# MPSPlots imports
from MPSPlots import colormaps
from MPSPlots.render2D import SceneList, Axis

from MPSTools.tools.mathematics import get_rho_gradient

# FiberFusing imports
from FiberFusing.coordinate_system import CoordinateSystem
from FiberFusing.tools import plot_style
import FiberFusing

from matplotlib import colors


@dataclass
class Geometry(object):
    """
    Class represent the refractive index (RI) geometric profile.
    """
    background: object
    """ Geometrique object representing the background (usually air). """
    additional_structure_list: list = field(default_factory=list)
    """ List of geometrique object representing the fiber structure. """
    fiber_list: list = field(default_factory=list)
    """ List of fiber structure to add. """
    x_bounds: list | str = 'centering'
    """ X boundary to render the structure, argument can be either list or a string from ['auto', 'left', 'right', 'centering']. """
    y_bounds: list | str = 'centering'
    """ Y boundary to render the structure, argument can be either list or a string from ['auto', 'top', 'bottom', 'centering']. """
    resolution: int = 100
    """ Number of point (x and y-direction) to evaluate the rendering. """
    index_scrambling: float = 0
    """ Index scrambling for degeneracy lifting. """
    gaussian_filter: int = None
    """ Standard deviation of the gaussian blurring for the mesh and gradient. """
    boundary_pad_factor: float = 1.3
    """ The factor that multiply the boundary value in order to keep padding between mesh and boundary. """

    def generate_coordinate_system(self) -> None:
        """
        Generates the coordinate system (CoordinateSystem) for the mesh construction

        :returns:   No returns
        :rtype:     None
        """
        min_x, min_y, max_x, max_y = self.get_boundaries()

        self.coordinate_system = CoordinateSystem(
            min_x=min_x,
            max_x=max_x,
            min_y=min_y,
            max_y=max_y,
            nx=self.resolution,
            ny=self.resolution
        )

        self.coordinate_system.centering(factor=self.boundary_pad_factor)

        self.interpret_y_boundary()

        self.interpret_x_boundary()

    def add_fiber(self, *fibers) -> None:
        """
        Adds a fiber structure to the geometry. The fibers than can be added
        have to be defined with the generic_fiber class in fiber_catalogue.py

        :param      fibers:  The fibers to be added
        :type       fibers:  tuple
        """
        for fiber in fibers:
            self.fiber_list.append(fiber)

    def add_structure(self, *structures) -> None:
        """
        Adds a custom structure to the geometry.

        :param      structures:  The fibers to be added
        :type       structures:  tuple
        """
        for structure in structures:
            self.additional_structure_list.append(structure)

    @property
    def structure_list(self) -> list:
        """
        Returns list of all the optical structure to be considered for the mesh construct.

        :returns:   List of the optical structures
        :rtype:     list
        """

        return [self.background, *self.additional_structure_list, *self.fiber_list]

    def interpret_x_boundary(self) -> None:
        """
        Interpret the x_bound parameter.
        If the parameter is in ["left", "right", ""], it returns
        an auto-evaluated boundary

        :param      x_bound:  The y boundary to be interpreted
        :type       x_bound:  list

        :returns:   The interpreted y boundary
        :rtype:     list
        """
        if not isinstance(self.x_bounds, str):
            return self.coordinate_system.set_x_boundary(self.x_bounds)

        match self.x_bounds:
            case 'right':
                return self.coordinate_system.set_right()
            case 'left':
                return self.coordinate_system.set_left()
            case 'centering':
                return self.coordinate_system.x_centering()

        raise ValueError(f"Invalid x_bounds input:{self.x_bounds}, value has to be in [list, 'right', 'left', 'centering']")

    def interpret_y_boundary(self) -> None:
        """
        Interpret the y_bound parameter.
        If the parameter is in ["top", "bottom", "centering"], it returns
        an auto-evaluated boundary

        :param      y_bound:  The y boundary to be interpreted
        :type       y_bound:  list

        :returns:   The interpreted y boundary
        :rtype:     list
        """
        if not isinstance(self.y_bounds, str):
            return self.coordinate_system.set_y_boundary(self.y_bounds)

        match self.y_bounds:
            case 'top':
                return self.coordinate_system.set_top()
            case 'bottom':
                return self.coordinate_system.set_bottom()
            case 'centering':
                return self.coordinate_system.y_centering()

        raise ValueError(f"Invalid y_bounds input:{self.y_bounds}, value has to be in [list, 'top', 'bottom', 'centering']")

    def get_boundaries(self) -> tuple:
        """
        Gets the boundaries containing the collection of defined structures.
        The list returns min_x, min_y, max_x, max_y.

        :returns:   The boundaries.
        :rtype:     tuple
        """
        if self.structure_list == []:
            raise ValueError('No internal structure provided for computation of the mesh.')

        min_x, min_y, max_x, max_y = [], [], [], []

        for obj in [*self.additional_structure_list, *self.fiber_list]:
            boundaries = obj.get_structure_max_min_boundaries()

            min_x.append(boundaries[0])
            min_y.append(boundaries[1])
            max_x.append(boundaries[2])
            max_y.append(boundaries[3])

        return (
            numpy.min(min_x),
            numpy.min(min_y),
            numpy.max(max_x),
            numpy.max(max_y)
        )

    @property
    def refractive_index_maximum(self) -> float:
        index_list = []
        for obj in self.structure_list:
            index_list += obj.refractive_index_list
        return max(index_list)

    @property
    def refractive_index_minimum(self) -> float:
        index_list = []
        for obj in self.structure_list:
            if isinstance(obj, FiberFusing.background.BackGround):
                continue
            index_list += obj.refractive_index_list
        return min(index_list)

    def get_index_range(self) -> list:
        """
        Returns the list of all index associated to the element of the geometry.
        """
        return [float(obj.index) for obj in self.structure_list]

    def rotate(self, angle: float) -> None:
        """
        Rotate the full geometry

        :param      angle:  Angle to rotate the geometry, in degrees.
        :type       angle:  float
        """
        for obj in self.structure_list:
            obj = obj.rotate(angle=angle)

    def generate_coordinate_mesh_gradient(self) -> None:
        self.generate_coordinate_system()

        self.generate_mesh()

        self.n2_gradient = self.get_n2_rho_gradient()

    def randomize_fiber_structures_index(self, random_factor: float) -> None:
        """
        Randomize the refractive index of the fiber structures

        :param      random_factor:  The random factor
        :type       random_factor:  float

        :returns:   No returns
        :rtype:     None
        """
        for fiber in self.fiber_list:
            for structure in fiber.inner_structure:
                structure.index += structure.index * self.index_scrambling * numpy.random.rand()

    def rasterize_polygons(self, coordinates: numpy.ndarray) -> numpy.ndarray:
        """
        Returns the rasterize mesh of the object.

        :param      coordinates:  The coordinates to which evaluate the mesh.
        :type       coordinates:  { type_description }
        :param      n_x:          The number of point in the x direction
        :type       n_x:          int
        :param      n_y:          The number of point in the y direction
        :type       n_y:          int

        :returns:   The rasterized mesh
        :rtype:     numpy.ndarray
        """
        mesh = numpy.zeros(self.coordinate_system.shape)

        self.background.overlay_structures_on_mesh(
            mesh=mesh,
            coordinate_system=self.coordinate_system
        )

        for structure in self.additional_structure_list:
            structure.overlay_structures_on_mesh(
                mesh=mesh,
                coordinate_system=self.coordinate_system
            )

        if self.index_scrambling != 0:
            self.randomize_fiber_structures_index(random_factor=self.index_scrambling)

        for fiber in self.fiber_list:
            fiber.overlay_structures_on_mesh(
                mesh=mesh,
                coordinate_system=self.coordinate_system,
                structures_type='inner_structure'
            )

        return mesh

    def add_background_to_mesh(self, mesh: numpy.ndarray) -> numpy.ndarray:
        raster = self.background.get_rasterized_mesh(coordinate_system=self.coordinate_system)
        mesh[numpy.where(raster != 0)] = 0
        raster *= self.background.index
        mesh += raster

    def generate_mesh(self) -> numpy.ndarray:
        self.coords = numpy.vstack(
            (self.coordinate_system.x_mesh.flatten(), self.coordinate_system.y_mesh.flatten())
        ).T

        self.mesh = self.rasterize_polygons(coordinates=self.coords)

        if self.gaussian_filter is not None:
            self.mesh = gaussian_filter(input=self.mesh, sigma=self.gaussian_filter)

        return self.mesh

    def get_n2_rho_gradient(self) -> numpy.ndarray:
        """
        Returns the n squared radial gradient.

        :returns:   The n 2 rho gradient.
        :rtype:     numpy.ndarray
        """
        gradient = get_rho_gradient(
            mesh=self.mesh**2,
            coordinate_system=self.coordinate_system
        )

        return gradient

    def render_patch_on_ax(self, ax: Axis) -> None:
        """
        Add the patch representation of the geometry into the give ax.

        :param      ax:   The ax to which append the representation.
        :type       ax:   Axis
        """
        ax.set_style(**plot_style.geometry, title='Coupler index structure')

        for structure in self.additional_structure_list:
            structure.render_patch_on_ax(ax=ax)

        for fiber in self.fiber_list:
            fiber.render_patch_on_ax(ax=ax)

    def render_gradient_on_ax(self, ax: Axis) -> None:
        """
        Add the rasterized representation of the gradient of the geometrys into the give ax.

        :param      ax:   The ax to which append the representation.
        :type       ax:   Axis
        """
        artist = ax.add_mesh(
            x=self.coordinate_system.x_vector,
            y=self.coordinate_system.y_vector,
            scalar=self.n2_gradient,
        )

        ax.set_style(
            **plot_style.geometry,
            title='Refractive index gradient',
            show_colorbar=True,
        )

        ax.add_colorbar(
            artist=artist,
            log_norm=True,
            position='right',
            numeric_format='%.1e',
            symmetric=True,
            colormap=colormaps.blue_white_red,
            norm=colors.SymLogNorm(linthresh=1e-10)
        )

    def render_mesh_on_ax(self, ax: Axis) -> None:
        """
        Add the rasterized representation of the geometry into the give ax.

        :param      ax:   The ax to which append the representation.
        :type       ax:   Axis
        """
        artist = ax.add_mesh(
            x=self.coordinate_system.x_vector,
            y=self.coordinate_system.y_vector,
            scalar=self.mesh,
        )

        ax.set_style(
            **plot_style.geometry,
            title='Rasterized mesh',
            show_colorbar=True,
        )

        ax.add_colorbar(
            artist=artist,
            discreet=False,
            position='right',
            numeric_format='%.4f',
            colormap='Blues',
            norm=colors.LogNorm(vmin=self.refractive_index_minimum / 1.01)
        )

    def plot(self, show_patch: bool = True, show_mesh: bool = True, show_gradient: bool = True) -> SceneList:
        """
        Plot the different representations [patch, mesh, gradient] of the geometry.

        :param      show_patch:     The show patch
        :type       show_patch:     bool
        :param      show_mesh:      The show mesh
        :type       show_mesh:      bool
        :param      show_gradient:  The show gradient
        :type       show_gradient:  bool

        :returns:   The figure encompassing all the axis
        :rtype:     SceneList
        """
        self.generate_coordinate_mesh_gradient()

        figure = SceneList(
            unit_size=(4, 4),
            tight_layout=True,
            ax_orientation='horizontal'
        )

        if show_patch:
            ax = figure.append_ax()
            self.render_patch_on_ax(ax)

        if show_mesh:
            ax = figure.append_ax()
            self.render_mesh_on_ax(ax)

        if show_gradient:
            ax = figure.append_ax()
            self.render_gradient_on_ax(ax)

        ax.set_style(**plot_style.geometry)

        return figure

# -

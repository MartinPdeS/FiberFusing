#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Tuple, List, Dict, Union
from FiberFusing.fiber.generic_fiber import GenericFiber
from FiberFusing import micro
from FiberFusing.fiber.loader import load_fiber_as_dict
from FiberFusing.components.point import Point
from PyOptik import MaterialBank


__all__ = [
    'load_fiber',
    'make_fiber',
    'CapillaryTube',
    'GradientCore',
    'CustomFiber',
]


def load_fiber(fiber_name: str, wavelength: float, position: Tuple[float, float] = (0, 0), remove_cladding: bool = True) -> GenericFiber:
    """
    Load a fiber configuration and construct a GenericFiber object based on specified parameters.

    Parameters
    ----------
    fiber_name : str
        The name of the fiber to load.
    wavelength : float
        The wavelength at which the fiber's material refractive index is evaluated.
    position : Tuple[float, float], optional
        The spatial position of the fiber, defaulting to (0, 0).
    remove_cladding : bool, optional
        Whether to exclude the cladding layer from the fiber configuration. Defaults to True.

    Returns
    -------
    GenericFiber
        A configured GenericFiber object with the specified properties.
    """
    if isinstance(position, Point):
        position = (position.x, position.y)

    fiber = GenericFiber(wavelength=wavelength, position=position)
    fiber_dict = load_fiber_as_dict(fiber_name=fiber_name, wavelength=wavelength)

    for structure in fiber_dict['layers'].values():
        if remove_cladding and 'cladding' in structure['name'].lower():
            continue
        fiber.create_and_add_new_structure(**structure)

    return fiber


def make_fiber(wavelength: float, structure_list: List[Dict], position: Tuple[float, float] = (0, 0)) -> GenericFiber:
    """
    Construct a GenericFiber object based on a list of structural configurations.

    Parameters
    ----------
    wavelength : float
        The wavelength at which the fiber's material properties are considered.
    structure_list : List[Dict]
        A list of dictionaries, each containing the parameters for a fiber structure.
    position : Tuple[float, float], optional
        The spatial position of the fiber. Defaults to (0, 0).

    Returns
    -------
    GenericFiber
        The newly created GenericFiber object populated with specified structures.
    """
    fiber = GenericFiber(wavelength=wavelength, position=position)
    for structure in structure_list:
        fiber.create_and_add_new_structure(**structure)

    return fiber


class CustomFiber(GenericFiber):
    """
    A class for creating a custom fiber configuration with an air layer.

    Parameters
    ----------
    wavelength : float
        The operational wavelength of the fiber in micrometers.
    position : Tuple[float, float], optional
        The spatial position of the fiber. Defaults to (0, 0).
    """

    def __init__(self, wavelength: float, position: Tuple[float, float] = (0, 0)):
        super().__init__(wavelength=wavelength, position=position)
        self.add_air()


class CapillaryTube(GenericFiber):
    """
    A class for creating a capillary tube type of fiber with a specified radius and refractive index.

    Parameters
    ----------
    wavelength : float
        The wavelength at which the fiber operates.
    radius : float
        The radius of the capillary tube.
    delta_n : float, optional
        The change in refractive index from the base silica index. Defaults to 0.015.
    """

    def __init__(self, wavelength: float, radius: float, delta_n: float = 0.015):
        super().__init__(wavelength=wavelength)
        self.radius = radius
        index = MaterialBank.fused_silica.compute_refractive_index(self.wavelength)
        self.create_and_add_new_structure(index=index + delta_n, radius=self.radius, name='capillary tube')


class GradientCore(GenericFiber):
    """
    A class for creating a fiber with a gradient index core, commonly used in certain optical applications.

    Parameters
    ----------
    wavelength : float
        The wavelength at which the fiber operates.
    core_radius : float
        The radius of the gradient index core.
    delta_n : Union[float, str]
        The change in refractive index, either as a direct float or as a percentage string.
    position : Tuple[float, float], optional
        The spatial position of the fiber. Defaults to (0, 0).

    Notes
    -----
    The fiber is based on designs described in [1]_.

    References
    ----------
    .. [1] Nature, "Fiber with gradient core index", https://www.nature.com/articles/s41598-018-27072-2
    """

    def __init__(self, wavelength: float, core_radius: float, delta_n: Union[float, str], position: Tuple[float, float] = (0, 0)):
        super().__init__(wavelength=wavelength, position=position)

        # Add the cladding layer
        self.create_and_add_new_structure(
            name='cladding',
            index=self.pure_silica_index,
            radius=62.5 * micro
        )

        # Convert delta_n if provided as a percentage string
        if isinstance(delta_n, str):
            factor = float(delta_n.strip('%')) / 100
            delta_n = self.pure_silica_index * factor

        # Add the gradient index core
        self.create_and_add_new_structure(
            name='core',
            is_graded=True,
            delta_n=delta_n,
            radius=core_radius,
            index=self.pure_silica_index
        )

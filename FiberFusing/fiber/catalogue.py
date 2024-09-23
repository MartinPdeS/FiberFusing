#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Tuple, List, Dict, Union
from FiberFusing.fiber.generic_fiber import GenericFiber
from FiberFusing import micro
from MPSTools.fiber_catalogue.loader import load_fiber_as_dict
from MPSTools.material_catalogue.loader import get_silica_index
from FiberFusing.components.point import Point


__all__ = [
    'load_fiber',
    'make_fiber',
    'CapillaryTube',
    'GradientCore',
    'CustomFiber',

]


def load_fiber(fiber_name: str, wavelength: float, position: Tuple[float, float] = (0, 0), remove_cladding: bool = True) -> GenericFiber:
    """
    Loads a fiber configuration from a specified source using the MPSTools library and constructs
    a GenericFiber object based on the specifications provided.

    Args:
        fiber_name (str): The name of the fiber to load.
        wavelength (float): The wavelength at which the fiber's material refractive index is evaluated.
        position (Tuple[float, float], optional): The position at which the fiber is placed. Defaults to (0, 0).
        remove_cladding (bool, optional): Whether to exclude the cladding layer from the fiber configuration. Defaults to False.

    Returns:
        GenericFiber: A configured GenericFiber object.
    """
    if isinstance(position, Point):
        position = (position.x, position.y)

    fiber = GenericFiber(wavelength=wavelength, position=position)
    fiber_dict = load_fiber_as_dict(fiber_name=fiber_name, wavelength=wavelength)

    for name, structure in fiber_dict['layers'].items():
        if remove_cladding and 'cladding' in structure['name'].lower():
            continue
        fiber.create_and_add_new_structure(**structure)

    return fiber


def make_fiber(wavelength: float, structure_list: List[Dict], position: Tuple[float, float] = (0, 0)) -> GenericFiber:
    """
    Constructs a GenericFiber object based on a specified wavelength and a list of structural configurations.

    Args:
        wavelength (float): The wavelength at which the fiber's material properties are considered.
        structure_list (List[Dict]): A list of dictionaries, each containing the parameters needed to add a structure to the fiber.
        position (Tuple[float, float], optional): The spatial position of the fiber. Defaults to (0, 0).

    Returns:
        GenericFiber: The newly created GenericFiber object populated with specified structures.
    """
    fiber = GenericFiber(wavelength=wavelength, position=position)
    for structure in structure_list:
        fiber.create_and_add_new_structure(**structure)

    return fiber


class CustomFiber(GenericFiber):
    def __init__(self, wavelength: float, position: Tuple[float, float] = (0, 0)):
        """
        Initializes a custom fiber, specifically adding an air layer after creation.

        Args:
            wavelength (float): The operational wavelength of the fiber in micrometers.
            position (Tuple[float, float]): The spatial position of the fiber, defaulting to (0, 0).
        """
        super().__init__(wavelength=wavelength, position=position)
        self.add_air()


class CapillaryTube(GenericFiber):
    def __init__(self, wavelength: float, radius: float, delta_n: float = 0.015):
        """
        Initializes a capillary tube type of fiber with a given radius and index modification.

        Args:
            wavelength (float): The wavelength at which the fiber operates.
            radius (float): The radius of the capillary tube.
            delta_n (float): Change in refractive index from the base silica index.
        """
        super().__init__(wavelength=wavelength)
        self.radius = radius
        index = get_silica_index(wavelength=self.wavelength)
        self.create_and_add_new_structure(index=index + delta_n, radius=self.radius, name='capillary tube')


class GradientCore(GenericFiber):
    # Fiber from https://www.nature.com/articles/s41598-018-27072-2

    def __init__(self, wavelength: float, core_radius: float, delta_n: Union[float, str], position: Tuple[float, float] = (0, 0)):
        """
        Initializes a fiber with a gradient index core, commonly used in certain optical applications.

        Args:
            wavelength (float): The wavelength at which the fiber operates.
            core_radius (float): The radius of the gradient index core.
            delta_n (Union[float, str]): The change in refractive index, either as a direct float or a percentage string.
            position (Tuple[float, float]): The spatial position of the fiber, defaulting to (0, 0).
        """
        super().__init__(wavelength=wavelength, position=position)

        self.create_and_add_new_structure(
            name='cladding',
            index=self.pure_silica_index,
            radius=62.5 * micro
        )

        if isinstance(delta_n, str):
            factor = float(delta_n.strip('%')) / 100
            delta_n = self.pure_silica_index * factor

        self.create_and_add_new_structure(
            name='core',
            is_graded=True,
            delta_n=delta_n,
            radius=core_radius,
            index=self.pure_silica_index
        )

# -

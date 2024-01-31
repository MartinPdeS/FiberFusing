#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Building a custom fiber type in the following way:

fiber = CustomFiber(wavelength=1550e-9)

fiber.add_silica_pure_cladding()

fiber.create_and_add_new_structure(name='core', radius=40e-6 / 2, NA=0.115)

fiber.create_and_add_new_structure(name='core', radius=4.1e-6, NA=0.13)

fiber.plot().show()

"""

from FiberFusing.fiber.base_class import GenericFiber
from FiberFusing import micro
from MPSTools.fiber_catalogue.loader import load_fiber_as_dict
from MPSTools.material_catalogue.loader import get_silica_index

__all__ = [
    'CapillaryTube',
    'GradientCore',
    'CustomFiber',

]


def load_fiber(fiber_name: str, wavelength: float, position: tuple = (0, 0), remove_cladding: bool = False) -> GenericFiber:
    """
    Loads a fiber from the MPSTools library.

    :param      fiber_name:  The fiber name
    :type       fiber_name:  str
    :param      wavelength:  The wavelength at which the fiber material refractive index is evaluated
    :type       wavelength:  float
    :param      position:    The position of the fiber
    :type       position:    tuple

    :returns:   The generic fiber.
    :rtype:     GenericFiber
    """
    fiber = GenericFiber(wavelength=wavelength, position=position)

    fiber_dict = load_fiber_as_dict(
        fiber_name=fiber_name,
        wavelength=wavelength
    )

    for name, structure in fiber_dict['layers'].items():
        if remove_cladding and structure['name'].lower() in ['cladding', 'clad']:
            continue

        fiber.create_and_add_new_structure(**structure)

    return fiber


class CustomFiber(GenericFiber):
    def __init__(self, wavelength: float, position: tuple = (0, 0)):
        super().__init__(wavelength=wavelength, position=position)

        self.add_air()


class CapillaryTube(GenericFiber):
    model = "CapillaryTube"

    def __init__(self, wavelength: float, radius: float, delta_n: float = 15e-3):
        super().__init__(wavelength=wavelength)
        self.radius = radius

        index = get_silica_index(wavelength=self.wavelength)

        self.create_and_add_new_structure(
            index=index + delta_n,
            radius=self.radius,
            name='capillary tube')


class GradientCore(GenericFiber):
    # Fiber from https://www.nature.com/articles/s41598-018-27072-2

    def __init__(self, wavelength: float, core_radius: float, delta_n: float | str, position: tuple = (0, 0)):
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

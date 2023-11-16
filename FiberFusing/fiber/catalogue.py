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
    'SMF28',
    'HP630',
    'HI1060',
    'CapillaryTube',
    'FluorineCapillaryTube',
    'FluorineCapillaryTube_2',
    'GradientCore',
    'DCF13',
    'CustomFiber',
    'DCF1300S_20',
    'DCF1300S_33',
    'DCF1300S_26',
    'DCF1300S_42',
    'F2058L1',
    'F2058G1',
    'F2028M24',
    'F2028M21',
    'F2028M12',

]


class CustomFiber(GenericFiber):
    def __init__(self, wavelength: float, position: tuple = (0, 0)):
        super().__init__(wavelength=wavelength, position=position)

        self.add_air()


class SMF28(GenericFiber):
    model = "SMF28"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        fiber_dict = load_fiber_as_dict(
            fiber_name=self.model,
            wavelength=self.wavelength
        )

        for _, structure in fiber_dict['layers'].items():
            self.create_and_add_new_structure(**structure)


class HP630(GenericFiber):
    model = "HP630"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        fiber_dict = load_fiber_as_dict(
            fiber_name=self.model,
            wavelength=self.wavelength
        )

        for _, structure in fiber_dict['layers'].items():
            self.create_and_add_new_structure(**structure)


class HI1060(GenericFiber):
    model = "HI630"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        fiber_dict = load_fiber_as_dict(
            fiber_name=self.model,
            wavelength=self.wavelength
        )

        for _, structure in fiber_dict['layers'].items():
            self.create_and_add_new_structure(**structure)


class CapillaryTube(GenericFiber):
    model = "CapillaryTube"

    def __init__(self, wavelength: float, radius: float, delta_n: float = 15e-3):
        super().__init__(wavelength=wavelength)
        self.radius = radius

        index = get_silica_index(wavelength=self.wavelength)

        self.create_and_add_new_structure(
            index=index,
            radius=self.radius,
            name='capillary tube')


class GradientCore(GenericFiber):
    # Fiber from https://www.nature.com/articles/s41598-018-27072-2

    def __init__(self, *args, core_radius, delta_n, **kwargs):
        super().__init__(*args, **kwargs)

        self.create_and_add_new_structure(
            name='outer_clad',
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


class DCF13(GenericFiber):
    model = "DCF13"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        fiber_dict = load_fiber_as_dict(
            fiber_name=self.model,
            wavelength=self.wavelength
        )

        for _, structure in fiber_dict['layers'].items():
            self.create_and_add_new_structure(**structure)


class DCF1300S_20(GenericFiber):
    model = "DCF1300S_20"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        fiber_dict = load_fiber_as_dict(
            fiber_name=self.model,
            wavelength=self.wavelength
        )

        for _, structure in fiber_dict['layers'].items():
            self.create_and_add_new_structure(**structure)


class DCF1300S_33(GenericFiber):
    model = "DCF1300S_33"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        fiber_dict = load_fiber_as_dict(
            fiber_name=self.model,
            wavelength=self.wavelength
        )

        for _, structure in fiber_dict['layers'].items():
            self.create_and_add_new_structure(**structure)


class DCF1300S_26(GenericFiber):
    model = "DCF1300S_26"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        fiber_dict = load_fiber_as_dict(
            fiber_name=self.model,
            wavelength=self.wavelength
        )

        for _, structure in fiber_dict['layers'].items():
            self.create_and_add_new_structure(**structure)


class DCF1300S_42(GenericFiber):
    model = "DCF1300S_42"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        fiber_dict = load_fiber_as_dict(
            fiber_name=self.model,
            wavelength=self.wavelength
        )

        for _, structure in fiber_dict['layers'].items():
            self.create_and_add_new_structure(**structure)


class F2058L1(GenericFiber):
    model = "F2058L1"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        fiber_dict = load_fiber_as_dict(
            fiber_name=self.model,
            wavelength=self.wavelength
        )

        for _, structure in fiber_dict['layers'].items():
            self.create_and_add_new_structure(**structure)


class F2058G1(GenericFiber):
    model = "F2058G1"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        fiber_dict = load_fiber_as_dict(
            fiber_name=self.model,
            wavelength=self.wavelength
        )

        for _, structure in fiber_dict['layers'].items():
            self.create_and_add_new_structure(**structure)


class F2028M24(GenericFiber):
    model = "F2028M24"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        fiber_dict = load_fiber_as_dict(
            fiber_name=self.model,
            wavelength=self.wavelength
        )

        for _, structure in fiber_dict['layers'].items():
            self.create_and_add_new_structure(**structure)


class F2028M21(GenericFiber):
    model = "F2028M21"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        fiber_dict = load_fiber_as_dict(
            fiber_name=self.model,
            wavelength=self.wavelength
        )

        for _, structure in fiber_dict['layers'].items():
            print(structure)
            self.create_and_add_new_structure(**structure)


class F2028M12(GenericFiber):
    model = "F2028M12"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        fiber_dict = load_fiber_as_dict(
            fiber_name=self.model,
            wavelength=self.wavelength
        )

        for _, structure in fiber_dict['layers'].items():
            self.create_and_add_new_structure(**structure)

# -

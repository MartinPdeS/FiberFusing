#!/usr/bin/env python
# -*- coding: utf-8 -*-

from FiberFusing.fiber.base_class import GenericFiber
from FiberFusing import micro
from FiberFusing.utils import get_silica_index

__all__ = [
    'SMF28',
    'HP630',
    'HI1060',
    'FiberCoreA',
    'FiberCoreB',
    'CapillaryTube',
    'FluorineCapillaryTube',
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


class SMF28(GenericFiber):
    brand = 'Corning'
    model = "SMF28"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.create_and_add_new_structure(
            name='clad',
            index=self.pure_silica_index,
            radius=62.5 * micro
        )

        self.create_and_add_new_structure(
            name='core',
            NA=0.12,
            radius=8.2 / 2 * micro,
        )


class HP630(GenericFiber):
    brand = 'Thorlab'
    model = "HP630"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.create_and_add_new_structure(
            name='clad',
            index=self.pure_silica_index,
            radius=62.5 * micro
        )

        self.create_and_add_new_structure(
            name='core',
            NA=0.13,
            radius=3.5 / 2 * micro,
        )


class HI1060(GenericFiber):
    brand = 'Corning'
    model = "HI630"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.create_and_add_new_structure(
            name='clad',
            index=self.pure_silica_index,
            radius=62.5 * micro
        )

        self.create_and_add_new_structure(
            name='core',
            NA=0.14,
            radius=5.3 / 2 * micro,
        )


class FiberCoreA(GenericFiber):
    brand = 'FiberCore'
    model = 'PS1250/1500'
    note = "Boron Doped Photosensitive Fiber"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.create_and_add_new_structure(
            name='clad',
            index=self.pure_silica_index,
            radius=62.5 * micro
        )

        self.create_and_add_new_structure(
            name='core',
            NA=0.12,
            radius=8.8 / 2 * micro,
        )


class FiberCoreB(GenericFiber):
    brand = 'FiberCore'
    model = 'SM1250'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.create_and_add_new_structure(
            name='clad',
            index=self.pure_silica_index,
            radius=62.5 * micro
        )

        self.create_and_add_new_structure(
            name='core',
            NA=0.12,
            radius=9.0 / 2 * micro,
        )


class CapillaryTube(GenericFiber):
    def __init__(self, wavelength: float,
                       radius: float,
                       index: float = None,
                       position: tuple = (0, 0)) -> None:

        super().__init__(wavelength=wavelength, position=position)
        self.radius = radius
        self._index = index

        self.initialize()

    def initialize(self) -> None:
        self.create_and_add_new_structure(
            name='clad',
            index=self.index,
            radius=self.radius
        )

    @property
    def index(self) -> float:
        if self._index is None:
            raise ValueError("Index hasn't been defined for object")
        return self._index

    @index.setter
    def index(self, value: float) -> None:
        self._index = value
        self.initialize()

    def set_delta_n(self, value: float) -> None:
        self.index = self.pure_silica_index + value


class FluorineCapillaryTube(GenericFiber):
    def __new__(cls, wavelength: float, delta_n: float = -15e-3, **kwargs):
        silica_index = get_silica_index(wavelength=wavelength)

        return CapillaryTube(
            wavelength=wavelength,
            **kwargs,
            index=silica_index + delta_n
        )


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
    brand = "Thorlabs"
    model = "DCF13"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.create_and_add_new_structure(
            name='outer_clad',
            index=self.pure_silica_index,
            radius=62.5 * micro
        )

        self.create_and_add_new_structure(
            name='inner_clad',
            NA=0.2,
            radius=19.9 / 2 * micro
        )

        self.create_and_add_new_structure(
            name='core',
            NA=0.12,
            radius=105.0 / 2 * micro,
        )


class CustomFiber(GenericFiber):
    def __init__(self, wavelength: float, position: tuple = (0, 0)):
        super().__init__(wavelength=wavelength, position=position)

        self.add_air()


class DCF1300S_20(GenericFiber):
    brand = "COPL"
    model = "DCF1300S_20"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.create_and_add_new_structure(
            name='outer_clad',
            index=self.pure_silica_index,
            radius=62.5 * micro
        )

        self.create_and_add_new_structure(
            name='inner_clad',
            NA=0.11,
            radius=19.9 / 2 * micro
        )

        self.create_and_add_new_structure(
            name='core',
            NA=0.12,
            radius=9.2 / 2 * micro,
        )


class DCF1300S_33(GenericFiber):
    brand = "COPL"
    model = "DCF1300S_33"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.create_and_add_new_structure(
            name='outer_clad',
            index=self.pure_silica_index,
            radius=62.5 * micro
        )

        self.create_and_add_new_structure(
            name='inner_clad',
            NA=0.11,
            radius=33.0 / 2 * micro
        )

        self.create_and_add_new_structure(
            name='core',
            NA=0.125,
            radius=9.0 / 2 * micro,
        )


class DCF1300S_26(GenericFiber):
    brand = "COPL"
    model = "DCF1300S_26"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.create_and_add_new_structure(
            name='outer_clad',
            index=self.pure_silica_index,
            radius=62.5 * micro
        )

        self.create_and_add_new_structure(
            name='inner_clad',
            NA=0.117,
            radius=26.8 / 2 * micro
        )

        self.create_and_add_new_structure(
            name='core',
            NA=0.13,
            radius=9.0 / 2 * micro,
        )


class DCF1300S_42(GenericFiber):
    brand = "COPL"
    model = "DCF1300S_42"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.create_and_add_new_structure(
            name='outer_clad',
            index=self.pure_silica_index,
            radius=62.5 * micro
        )

        self.create_and_add_new_structure(
            name='inner_clad',
            NA=0.116,
            radius=42.0 / 2 * micro
        )

        self.create_and_add_new_structure(
            name='core',
            NA=0.13,
            radius=9.0 / 2 * micro,
        )


class F2058L1(GenericFiber):
    brand = "COPL"
    model = "F2058L1"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.create_and_add_new_structure(
            name='outer_clad',
            index=self.pure_silica_index,
            radius=62.5 * micro
        )

        self.create_and_add_new_structure(
            name='inner_clad',
            NA=0.117,
            radius=19.6 / 2 * micro
        )

        self.create_and_add_new_structure(
            name='core',
            NA=0.13,
            radius=9.0 / 2 * micro,
        )


class F2058G1(GenericFiber):
    brand = "COPL"
    model = "F2058G1"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.create_and_add_new_structure(
            name='outer_clad',
            index=self.pure_silica_index,
            radius=62.5 * micro
        )

        self.create_and_add_new_structure(
            name='inner_clad',
            NA=0.115,
            radius=32.3 / 2 * micro
        )

        self.create_and_add_new_structure(
            name='core',
            NA=0.124,
            radius=9.0 / 2 * micro,
        )


class F2028M24(GenericFiber):
    model = "F2028M24"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.create_and_add_new_structure(
            name='outer_clad',
            index=self.pure_silica_index,
            radius=62.5 * micro
        )

        self.create_and_add_new_structure(
            name='inner_clad',
            NA=0.19,
            radius=14.1 / 2 * micro
        )

        self.create_and_add_new_structure(
            name='core',
            NA=0.11,
            radius=2.3 / 2 * micro,
        )


class F2028M21(GenericFiber):
    model = "F2028M21"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.create_and_add_new_structure(
            name='outer_clad',
            index=self.pure_silica_index,
            radius=62.5 * micro
        )

        self.create_and_add_new_structure(
            name='inner_clad',
            NA=0.19,
            radius=17.6 / 2 * micro
        )

        self.create_and_add_new_structure(
            name='core',
            NA=0.11,
            radius=2.8 / 2 * micro,
        )


class F2028M12(GenericFiber):
    model = "F2028M12"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.create_and_add_new_structure(
            name='outer_clad',
            index=self.pure_silica_index,
            radius=62.5 * micro
        )

        self.create_and_add_new_structure(
            name='inner_clad',
            NA=0.19,
            radius=25.8 / 2 * micro
        )

        self.create_and_add_new_structure(
            name='core',
            NA=0.11,
            radius=4.1 / 2 * micro,
        )


if __name__ == '__main__':
    fiber = CustomFiber(wavelength=1550e-9)

    fiber.add_silica_pure_cladding()

    fiber.create_and_add_new_structure(name='core', radius=40e-6 / 2, NA=0.115)

    fiber.create_and_add_new_structure(name='core', radius=4.1e-6, NA=0.13)

    fiber.plot().show()

# -

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest.mock import patch

from FiberFusing import configuration
from FiberFusing.fiber import catalogue


fused_structures = [
    configuration.ring.FusedProfile_02x02,
    configuration.ring.FusedProfile_03x03,
    configuration.ring.FusedProfile_04x04,
    configuration.ring.FusedProfile_05x05,
    configuration.line.FusedProfile_02x02,
    configuration.line.FusedProfile_03x03,
    configuration.line.FusedProfile_04x04,
    configuration.line.FusedProfile_05x05,
]


@patch("matplotlib.pyplot.show")
def test_load_fiber(patch):
    fiber = catalogue.load_fiber(fiber_name='SMF28', wavelength=1550e-9)

    fiber.plot().show().close()


@patch("matplotlib.pyplot.show")
def test_custom_fiber(patch):
    fiber = catalogue.GenericFiber(wavelength=1550e-9)

    fiber.add_silica_pure_cladding()

    fiber.create_and_add_new_structure(name='core', radius=4.2 / 2, NA=0.115)

    fiber.plot().show().close()


@patch("matplotlib.pyplot.show")
def test_cappilary_tube(patch):
    capillary = catalogue.CapillaryTube(wavelength=1550e-9, radius=100e-6)

    capillary.plot().show().close()


@patch("matplotlib.pyplot.show")
def test_graded_index_fiber(patch):
    fiber = catalogue.GradientCore(wavelength=1550e-9, core_radius=8e-6, delta_n=15e-3)

    fiber.plot().show().close()
# -

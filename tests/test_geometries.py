#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest.mock import patch

import pytest

from FiberFusing import Geometry, configuration, BackGround
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


@pytest.mark.parametrize('fused_structure', fused_structures, ids=fused_structures)
@patch("matplotlib.pyplot.show")
def test_building_geometry(patch, fused_structure):

    clad = fused_structure(
        fusion_degree='auto',
        fiber_radius=62.5e-6,
        index=1.4444
    )

    background = BackGround(index=1)

    geometry = Geometry(
        additional_structure_list=[clad],
        background=background,
        x_bounds='centering',
        y_bounds='centering',
        resolution=50
    )

    geometry.add_structure(clad)

    geometry.generate_coordinate_mesh_gradient()

    geometry.plot().show().close()


@pytest.mark.parametrize('fused_structure', fused_structures, ids=fused_structures)
@patch("matplotlib.pyplot.show")
def test_building_geometry_with_cappilary(patch, fused_structure):

    clad = fused_structure(
        fusion_degree='auto',
        fiber_radius=62.5e-6,
        index=1.4444
    )

    background = BackGround(index=1)

    cappilary_tube = catalogue.CapillaryTube(wavelength=1550e-9, radius=125e-6)

    geometry = Geometry(
        additional_structure_list=[cappilary_tube, clad],
        background=background,
        x_bounds='centering',
        y_bounds='centering',
        resolution=50
    )

    geometry.add_structure(clad)

    geometry.generate_coordinate_mesh_gradient()

    geometry.plot().show().close()


@pytest.mark.parametrize('fused_structure', fused_structures, ids=fused_structures)
@patch("matplotlib.pyplot.show")
def test_building_geometry_with_cappilary_and_fibers(patch, fused_structure):
    clad = fused_structure(
        fusion_degree='auto',
        fiber_radius=62.5e-6,
        index=1.4444
    )

    background = BackGround(index=1)

    cappilary_tube = catalogue.CapillaryTube(wavelength=1550e-9, radius=125e-6)

    fiber_list = [
        catalogue.load_fiber(fiber_name='DCF1300S_20', wavelength=1550e-9),
        catalogue.load_fiber(fiber_name='SMF28', wavelength=1550e-9),
    ]

    geometry = Geometry(
        additional_structure_list=[cappilary_tube, clad],
        background=background,
        fiber_list=fiber_list,
        x_bounds='left',
        y_bounds='centering',
        resolution=50
    )

    geometry.add_structure(clad)

    geometry.generate_coordinate_mesh_gradient()

    geometry.plot().show().close()

# -

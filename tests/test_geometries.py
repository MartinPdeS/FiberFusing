#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from unittest.mock import patch
from FiberFusing import Geometry, configuration, BackGround
from FiberFusing.fiber import catalogue

# Define the different fused structures from configurations
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


# Parameterize the test cases to run with each structure
@pytest.mark.parametrize('fused_structure', fused_structures, ids=str)
@patch("matplotlib.pyplot.show")
def test_building_geometry(mock_show, fused_structure):
    """
    Test that the Geometry class can build and plot a structure without additional components.
    """
    clad = fused_structure(fusion_degree='auto', fiber_radius=62.5e-6, index=1.4444)
    background = BackGround(index=1)
    geometry = Geometry(additional_structure_list=[clad], background=background,
                        x_bounds='centering', y_bounds='centering', resolution=50)

    geometry.add_structure(clad)
    geometry.generate_coordinate_mesh()
    geometry.plot().show()
    mock_show.assert_called()


@pytest.mark.parametrize('fused_structure', fused_structures, ids=str)
@patch("matplotlib.pyplot.show")
def test_building_geometry_with_capillary(mock_show, fused_structure):
    """
    Test that the Geometry class can build and plot a structure with a capillary tube.
    """
    clad = fused_structure(fusion_degree='auto', fiber_radius=62.5e-6, index=1.4444)
    background = BackGround(index=1)
    capillary_tube = catalogue.CapillaryTube(wavelength=1550e-9, radius=125e-6)
    geometry = Geometry(additional_structure_list=[capillary_tube, clad], background=background,
                        x_bounds='centering', y_bounds='centering', resolution=50)

    geometry.add_structure(clad)
    geometry.generate_coordinate_mesh()
    geometry.plot().show()
    mock_show.assert_called()


@pytest.mark.parametrize('fused_structure', fused_structures, ids=str)
@patch("matplotlib.pyplot.show")
def test_building_geometry_with_capillary_and_fibers(mock_show, fused_structure):
    """
    Test that the Geometry class can build and plot a structure with a capillary tube and additional fibers.
    """
    clad = fused_structure(fusion_degree='auto', fiber_radius=62.5e-6, index=1.4444)
    background = BackGround(index=1)
    capillary_tube = catalogue.CapillaryTube(wavelength=1550e-9, radius=125e-6)
    fiber_list = [
        catalogue.load_fiber(fiber_name='DCF1300S_20', wavelength=1550e-9),
        catalogue.load_fiber(fiber_name='SMF28', wavelength=1550e-9),
    ]
    geometry = Geometry(additional_structure_list=[capillary_tube, clad], background=background,
                        fiber_list=fiber_list, x_bounds='left', y_bounds='centering', resolution=50)

    geometry.add_structure(clad)
    geometry.generate_coordinate_mesh()
    geometry.plot().show()
    mock_show.assert_called()

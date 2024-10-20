#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from unittest.mock import patch
import matplotlib.pyplot as plt

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
def test_load_fiber(mock_show):
    """Test loading a standard fiber from the catalogue."""
    fiber = catalogue.load_fiber(fiber_name='SMF28', wavelength=1550e-9)
    assert fiber is not None, "Fiber should be loaded successfully."

    fiber.plot()
    plt.close()
    mock_show.assert_called()


@patch("matplotlib.pyplot.show")
def test_custom_fiber(mock_show):
    """Test creating and plotting a custom fiber."""
    fiber = catalogue.GenericFiber(wavelength=1550e-9)

    fiber.add_silica_pure_cladding()

    fiber.create_and_add_new_structure(name='core', radius=4.2 / 2, NA=0.115)

    fiber.plot()
    plt.close()
    mock_show.assert_called()


@patch("matplotlib.pyplot.show")
def test_cappilary_tube(mock_show):
    """Test creating and plotting a capillary tube."""
    capillary = catalogue.CapillaryTube(wavelength=1550e-9, radius=100e-6)
    assert capillary is not None, "Capillary tube should be created successfully."

    capillary.plot()
    plt.close()
    mock_show.assert_called()


@patch("matplotlib.pyplot.show")
def test_graded_index_fiber(mock_show):
    """Test creating and plotting a graded index fiber."""
    fiber = catalogue.GradientCore(wavelength=1550e-9, core_radius=8e-6, delta_n=15e-3)
    assert fiber is not None, "Graded index fiber should be created successfully."

    fiber.plot()
    plt.close()
    mock_show.assert_called()


if __name__ == "__main__":
    pytest.main(["-W error", __file__])

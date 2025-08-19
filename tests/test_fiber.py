#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from unittest.mock import patch
import matplotlib.pyplot as plt
from FiberFusing.fiber import FiberLoader, GenericFiber
from FiberFusing import GradedIndex


@patch("matplotlib.pyplot.show")
def test_load_fiber(mock_show):
    """Test loading a standard fiber from the catalogue."""

    fiber_loader = FiberLoader()
    fiber = fiber_loader.load_fiber(fiber_name='SMF28', clad_refractive_index=1.4444)
    assert fiber is not None, "Fiber should be loaded successfully."

    fiber.plot()
    plt.close()
    mock_show.assert_called()


@patch("matplotlib.pyplot.show")
def test_custom_fiber(mock_show):
    """Test creating and plotting a custom fiber."""
    fiber = GenericFiber()

    fiber.create_and_add_new_structure(name='clad', refractive_index=1.0, radius=62.5e-6)

    fiber.create_and_add_new_structure(name='core', radius=4.2 / 2, NA=0.115)

    fiber.plot()
    plt.close()
    mock_show.assert_called()


@patch("matplotlib.pyplot.show")
def test_cappilary_tube(mock_show):
    """Test creating and plotting a capillary tube."""

    capillary_tube = GenericFiber()

    capillary_tube.create_and_add_new_structure(
        name='cladding',
        refractive_index=1.44,
        radius=100 * 1e-6
    )

    assert capillary_tube is not None, "Capillary tube should be created successfully."

    capillary_tube.plot()
    plt.close()
    mock_show.assert_called()


@patch("matplotlib.pyplot.show")
def test_graded_index_fiber(mock_show):
    """Test creating and plotting a graded index fiber."""

    fiber = GenericFiber()

    graded_index = GradedIndex(
        inside=1.4480,
        outside=1.4450,
    )

    fiber.create_and_add_new_structure(
        name='core',
        refractive_index=graded_index,
        radius=8e-6
    )

    assert fiber is not None, "Graded index fiber should be created successfully."

    fiber.plot()
    plt.close()
    mock_show.assert_called()


if __name__ == "__main__":
    pytest.main(["-W error", __file__])

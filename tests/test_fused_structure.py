#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest.mock import patch
import pytest
import matplotlib.pyplot as plt
from FiberFusing.profile import Profile, StructureType


@pytest.mark.parametrize("fusion_degree", [0.1, 0.5], ids=lambda x: f"FusionDegree_{x}")
@pytest.mark.parametrize('number_of_fibers', [2, 3, 5], ids=lambda x: f"FusedProfile_{x}x{x}")
@pytest.mark.parametrize('structure_type', [StructureType.CIRCULAR, StructureType.LINEAR], ids=lambda x: f"StructureType_{x}")
@patch("matplotlib.pyplot.show")
def test_building_structure(mock_show, number_of_fibers, fusion_degree, structure_type):
    profile = Profile()

    profile.add_structure(
        structure_type=structure_type,
        number_of_fibers=number_of_fibers,
        fusion_degree=fusion_degree,
        fiber_radius=62.5e-6,
        compute_fusing=True
    )

    profile.plot()
    mock_show.assert_called_once()  # Verify that show was called exactly once
    plt.close()


def test_randomize_core_position():
    """Test the randomization of core positions in a profile structure.
    """
    profile = Profile()

    profile.add_structure(
        structure_type=StructureType.CIRCULAR,
        number_of_fibers=5,
        fusion_degree=0.4,
        fiber_radius=62.5e-6,
        compute_fusing=True
    )

    profile.randomize_core_positions(random_factor=4e-6)

    assert len(profile.fiber_list) == 5
    for fiber in profile.fiber_list:
        assert fiber.shifted_core is not None
        assert fiber.center != fiber.core

def test_rotate_profile():
    """Test the rotation of a profile structure.
    """
    profile = Profile()

    profile.add_structure(
        structure_type=StructureType.CIRCULAR,
        number_of_fibers=5,
        fusion_degree=0.4,
        fiber_radius=62.5e-6,
        compute_fusing=True
    )

    initial_fiber_list = profile.fiber_list.copy()
    profile = profile.rotate(90)

    assert len(profile.fiber_list) == len(initial_fiber_list)

def test_translate_profile():
    """Test the translation of a profile structure.
    """
    profile = Profile()

    profile.add_structure(
        structure_type=StructureType.CIRCULAR,
        number_of_fibers=5,
        fusion_degree=0.4,
        fiber_radius=62.5e-6,
        compute_fusing=True
    )

    initial_fiber_list = profile.fiber_list.copy()
    profile = profile.translate(shift=(1e-6, 2e-6))

    assert len(profile.fiber_list) == len(initial_fiber_list)

def test_scale_profile():
    """Test the scaling of a profile structure.
    """
    profile = Profile()

    profile.add_structure(
        structure_type=StructureType.CIRCULAR,
        number_of_fibers=5,
        fusion_degree=0.4,
        fiber_radius=62.5e-6,
        compute_fusing=True
    )

    initial_fiber_list = profile.fiber_list.copy()
    profile = profile.scale_position(2.0)

    assert len(profile.fiber_list) == len(initial_fiber_list)

if __name__ == "__main__":
    pytest.main(["-W error", __file__])

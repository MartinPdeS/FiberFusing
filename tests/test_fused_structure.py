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

    profile.randomize_core_position(random_factor=4e-6)


if __name__ == "__main__":
    pytest.main(["-W error", __file__])

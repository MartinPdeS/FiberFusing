#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest.mock import patch
import pytest
from FiberFusing import configuration
import matplotlib.pyplot as plt


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


@pytest.mark.parametrize('fused_structure', fused_structures, ids=lambda x: x.__name__)
@patch("matplotlib.pyplot.show")
def test_building_clad_structure(mock_show, fused_structure):
    clad = fused_structure(
        fusion_degree='auto',
        fiber_radius=62.5e-6,
        index=1.4444
    )

    clad.plot()
    mock_show.assert_called_once()  # Verify that show was called exactly once
    plt.close()


if __name__ == "__main__":
    pytest.main(["-W error", __file__])

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest.mock import patch
import pytest
from itertools import product
import matplotlib.pyplot as plt
from FiberFusing import Geometry, configuration, BackGround


x_boundaries = ['left', 'right', 'centering', [-1, 1]]
y_boundaries = ['top', 'bottom', 'centering', [-1, 1]]

x_y_boundaries = product(x_boundaries, y_boundaries)

@patch("matplotlib.pyplot.show")
@pytest.mark.parametrize('boundaries', x_y_boundaries)
def test_building_geometry(mock_show, boundaries):

    clad = configuration.ring.FusedProfile_01x01(
        fiber_radius=62.5e-6,
        index=1.4444
    )

    background = BackGround(index=1)

    geometry = Geometry(
        additional_structure_list=[clad],
        background=background,
        x_bounds=boundaries[0],
        y_bounds=boundaries[1],
        resolution=50
    )

    geometry.add_structure(clad)

    geometry.generate_coordinate_mesh()

    geometry.plot()
    plt.close()

if __name__ == '__main__':
    pytest.main([__file__])

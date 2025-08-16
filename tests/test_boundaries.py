#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from unittest.mock import patch
from itertools import product
import matplotlib.pyplot as plt
from FiberFusing import Geometry, BoundaryMode, BackGround
from FiberFusing.profile import Profile, StructureType


# Parameter sets for testing
x_boundaries = [BoundaryMode.LEFT, BoundaryMode.RIGHT, BoundaryMode.CENTERING, [-1, 1]]
y_boundaries = [BoundaryMode.TOP, BoundaryMode.BOTTOM, BoundaryMode.CENTERING, [-1, 1]]
boundary_combinations = list(product(x_boundaries, y_boundaries))


@pytest.mark.parametrize('boundaries', boundary_combinations)
@patch("matplotlib.pyplot.show")
def test_building_geometry(mock_show, boundaries):
    """
    Test the creation and plotting of a Geometry instance with different boundary arrangmentss.

    Parameters
    ----------
    mock_show : MagicMock
        Mock object for `plt.show()` to prevent actual rendering during tests.
    boundaries : Tuple
        Tuple containing x and y boundaries to be tested.
    """
    x_boundary, y_boundary = boundaries

    # Create a arrangments instance and background
    profile = Profile()

    profile.add_structure(
        structure_type=StructureType.CIRCULAR,
        number_of_fibers=5,
        fusion_degree=0.4,
        fiber_radius=62.5e-6,
        compute_fusing=True
    )

    profile.index = 1.4444

    background = BackGround(index=1)

    # Create a geometry instance with the given parameters
    geometry = Geometry(
        additional_structure_list=[profile],
        background=background,
        x_bounds=x_boundary,
        y_bounds=y_boundary,
        resolution=50
    )

    # Add the structure and generate the mesh
    geometry.add_structure(profile)

    # Plot the geometry (mocked)
    geometry.plot()
    plt.close()


# Run the tests if the file is executed directly
if __name__ == "__main__":
    pytest.main(["-W error", __file__])

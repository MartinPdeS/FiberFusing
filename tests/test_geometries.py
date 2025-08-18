#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from unittest.mock import patch
import matplotlib.pyplot as plt
from FiberFusing import Geometry, DomainAlignment, BackGround
from FiberFusing.fiber import FiberLoader, GenericFiber
from FiberFusing.profile import Profile, StructureType


@pytest.mark.parametrize("fusion_degree", [0.1, 0.5], ids=lambda x: f"FusionDegree_{x}")
@pytest.mark.parametrize('number_of_fibers', [2, 3, 5], ids=lambda x: f"FusedProfile_{x}x{x}")
@pytest.mark.parametrize('structure_type', [StructureType.CIRCULAR, StructureType.LINEAR], ids=lambda x: f"StructureType_{x}")
@patch("matplotlib.pyplot.show")
def test_building_geometry(mock_show, fusion_degree, number_of_fibers, structure_type):
    """
    Test the creation and plotting of a Geometry instance with a single fused structure.

    Parameters
    ----------
    mock_show : MagicMock
        Mock object for `plt.show()` to prevent actual rendering during tests.
    fused_structure : callable
        The structure arrangments callable to test.
    """
    profile = Profile()

    profile.add_structure(
        structure_type=structure_type,
        number_of_fibers=number_of_fibers,
        fusion_degree=fusion_degree,
        fiber_radius=62.5e-6
    )

    profile.refractive_index = 1.4444


    background = BackGround(refractive_index=1)
    geometry = Geometry(
        x_bounds=DomainAlignment.CENTERING,
        y_bounds=DomainAlignment.CENTERING,
        resolution=150
    )

    geometry.add_structure(background, profile)
    geometry.initialize()

    plt.close('all')


@pytest.mark.parametrize("fusion_degree", [0.1, 0.5], ids=lambda x: f"FusionDegree_{x}")
@pytest.mark.parametrize('number_of_fibers', [2, 3, 5], ids=lambda x: f"FusedProfile_{x}x{x}")
@pytest.mark.parametrize('structure_type', [StructureType.CIRCULAR, StructureType.LINEAR], ids=lambda x: f"StructureType_{x}")
@patch("matplotlib.pyplot.show")
def test_building_geometry_with_capillary(mock_show, fusion_degree, number_of_fibers, structure_type):
    """
    Test the creation and plotting of a Geometry instance with a capillary tube and a fused structure.

    Parameters
    ----------
    mock_show : MagicMock
        Mock object for `plt.show()` to prevent actual rendecircular ducircular tests.
    fused_structure : callable
        The structure arrangments callable to test.
    """
    profile = Profile()

    profile.add_structure(
        structure_type=structure_type,
        number_of_fibers=number_of_fibers,
        fusion_degree=fusion_degree,
        fiber_radius=62.5e-6
    )

    profile.refractive_index=1.4444

    background = BackGround(refractive_index=1)

    capillary_tube = GenericFiber()

    capillary_tube.create_and_add_new_structure(
        name='cladding',
        refractive_index=1.4440,
        radius=125 * 1e-6
    )

    geometry = Geometry(
        x_bounds=DomainAlignment.CENTERING,
        y_bounds=DomainAlignment.CENTERING,
        resolution=50
    )

    geometry.add_structure(background, capillary_tube, profile)
    geometry.initialize()
    geometry.plot()
    plt.close('all')


@pytest.mark.parametrize("fusion_degree", [0.1, 0.5], ids=lambda x: f"FusionDegree_{x}")
@pytest.mark.parametrize('number_of_fibers', [2, 3, 5], ids=lambda x: f"FusedProfile_{x}x{x}")
@pytest.mark.parametrize('structure_type', [StructureType.CIRCULAR, StructureType.LINEAR], ids=lambda x: f"StructureType_{x}")
@patch("matplotlib.pyplot.show")
def test_building_geometry_with_capillary_and_fibers(mock_show, fusion_degree, number_of_fibers, structure_type):
    """
    Test the creation and plotting of a Geometry instance with a capillary tube and additional fibers.

    Parameters
    ----------
    mock_show : MagicMock
        Mock object for `plt.show()` to prevent actual rendecircular ducircular tests.
    fused_structure : callable
        The structure arrangments callable to test.
    """
    profile = Profile()

    profile.add_structure(
        structure_type=structure_type,
        number_of_fibers=number_of_fibers,
        fusion_degree=fusion_degree,
        fiber_radius=62.5e-6
    )

    profile.refractive_index = 1.4444

    background = BackGround(refractive_index=1)

    capillary_tube = GenericFiber()

    capillary_tube.create_and_add_new_structure(
        name='cladding',
        refractive_index=1.4440,
        radius=125 * 1e-6
    )

    fiber_loader = FiberLoader()

    fiber_list = [
        fiber_loader.load_fiber(fiber_name='DCF1300S_20', clad_refractive_index=1.4480),
        fiber_loader.load_fiber(fiber_name='SMF28', clad_refractive_index=1.4480),
    ]
    geometry = Geometry(
        x_bounds=DomainAlignment.LEFT,
        y_bounds=DomainAlignment.CENTERING,
        resolution=50
    )

    geometry.add_structure(background, profile, capillary_tube, *fiber_list)

    geometry.initialize()
    geometry.plot()
    plt.close('all')


def test_geometry_api():
    profile = Profile()

    profile.add_structure(
        structure_type=StructureType.CIRCULAR,
        number_of_fibers=2,
        fusion_degree=0.3,
        fiber_radius=62.5e-6
    )

    profile.refractive_index = 1.4444

    geometry = Geometry(
        x_bounds=DomainAlignment.CENTERING,
        y_bounds=DomainAlignment.CENTERING,
        resolution=100
    )

    geometry.add_structure(profile)
    geometry.initialize()

    geometry.x_bounds = DomainAlignment.LEFT
    geometry.x_bounds = DomainAlignment.CENTERING
    geometry.x_bounds = DomainAlignment.RIGHT
    geometry.rotate(90)

    geometry.y_bounds = DomainAlignment.TOP
    geometry.y_bounds = DomainAlignment.CENTERING
    geometry.y_bounds = DomainAlignment.BOTTOM


if __name__ == "__main__":
    pytest.main(["-W", "error", __file__])

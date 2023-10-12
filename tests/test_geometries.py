#!/usr/bin/env python
# -*- coding: utf-8 -*-


import pytest

from FiberFusing import Geometry, configuration, BackGround


fused_structures = [
    configuration.ring.FusedProfile_02x02,
    configuration.ring.FusedProfile_03x03,
    configuration.ring.FusedProfile_04x04,
    configuration.ring.FusedProfile_05x05,
    # configuration.line.FusedProfile_02x02,
    # configuration.line.FusedProfile_03x03,
    # configuration.line.FusedProfile_04x04,
    # configuration.line.FusedProfile_05x05,
]


@pytest.mark.parametrize('fused_structure', fused_structures, ids=fused_structures)
def test_fused(fused_structure):

    clad = fused_structure(
        fiber_radius=62.5e-6,
        index=1.4444
    )

    geometry = Geometry(
        additional_structure_list=[clad],
        background=BackGround(index=1),
        x_bounds='centering',
        y_bounds='centering',
        resolution=50
    )

    geometry.add_structure(clad)

    geometry.generate_coordinate_mesh_gradient()

# -

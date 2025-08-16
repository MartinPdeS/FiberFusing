"""
19x19 Ring - Clad
=================
"""

from FiberFusing.profile import Profile, StructureType

profile = Profile()

profile.add_structure(
    structure_type=StructureType.CIRCULAR,
    number_of_fibers=6,
    fusion_degree=0.2,
    fiber_radius=62.5e-6,
    scale_position=1.0,
    angle_shift=0,
    compute_fusing=False
)

profile.add_structure(
    structure_type=StructureType.CIRCULAR,
    number_of_fibers=12,
    fusion_degree=0.2,
    fiber_radius=62.5e-6,
    scale_position=1.00,
    compute_fusing=False,
    angle_shift=15,
)

profile.add_center_fiber(fiber_radius=62.5e-6)


profile.plot(show_cores=True, show_centers=False)


# -

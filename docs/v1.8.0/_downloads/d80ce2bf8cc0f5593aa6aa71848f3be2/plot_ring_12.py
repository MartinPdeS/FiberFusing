"""
12x12 Ring - Clad
=================
"""

# %%
from FiberFusing.profile import Profile, StructureType

profile = Profile()

profile.add_structure(
    structure_type=StructureType.CIRCULAR,
    number_of_fibers=3,
    fusion_degree=0.3,
    fiber_radius=62.5e-6,
    scale_position=1.0,
    angle_shift=0,
    compute_fusing=True
)

profile.add_structure(
    structure_type=StructureType.CIRCULAR,
    number_of_fibers=9,
    fusion_degree=0.1,
    fiber_radius=62.5e-6,
    scale_position=1.0,
    compute_fusing=True,
    angle_shift=20,
)

profile.plot(show_cores=True, show_centers=False)

# -

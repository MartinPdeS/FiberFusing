"""
4x4 Line - Clad
===============
"""

from FiberFusing.profile import Profile, StructureType

profile = Profile()

profile.add_structure(
    structure_type=StructureType.LINEAR,
    number_of_fibers=4,
    fusion_degree=0.3,
    fiber_radius=62.5e-6,
    compute_fusing=True
)

profile.plot(show_cores=True, show_centers=True)

# -

"""
Effect of fusion degree
=======================
"""

# %%
from FiberFusing.profile import Profile, StructureType

for fusion_degree in [0.1, 0.2, 0.3, 0.4, 0.5]:

    profile = Profile()

    profile.add_structure(
        structure_type=StructureType.CIRCULAR,
        number_of_fibers=3,
        fusion_degree=fusion_degree,
        fiber_radius=62.5e-6,
        compute_fusing=True
    )

    profile.plot()


# -

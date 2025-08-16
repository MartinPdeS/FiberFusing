"""
Effect of core randomization
============================
"""

from FiberFusing.profile import Profile, StructureType

profile = Profile()

profile.add_structure(
    structure_type=StructureType.LINEAR,
    number_of_fibers=2,
    fusion_degree=0.3,
    fiber_radius=62.5e-6,
    compute_fusing=True
)


# %%
factor = 0
profile.randomize_core_position(random_factor=factor)
profile.plot(show_centers=True, show_cores=True)

# %%
factor = 10e-6
profile.randomize_core_position(random_factor=factor)
profile.plot(show_centers=True, show_cores=True)

# %%
factor = 10e-6
profile.randomize_core_position(random_factor=factor)
profile.plot(show_centers=True, show_cores=True)

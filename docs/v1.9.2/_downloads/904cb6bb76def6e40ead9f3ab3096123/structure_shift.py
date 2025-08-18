"""
Effect of translation
=====================
"""

from FiberFusing.profile import Profile, StructureType

profile = Profile()

profile.add_structure(
    structure_type=StructureType.LINEAR,
    number_of_fibers=3,
    fusion_degree=0.3,
    fiber_radius=62.5e-6,
    compute_fusing=True
)

profile.plot(show_cores=True, show_centers=True)


# %%
shift = (0, 0)
profile = profile.translate(shift)
profile.plot()

# %%
shift = (20e-6, 0)
profile = profile.translate(shift)
profile.plot()

"""
Effect of core randomization
============================
"""

# %%
from FiberFusing.configuration.line import FusedProfile_02x02 as FusedProfile
from PyOptik import MaterialBank

material = MaterialBank.fused_silica

wavelength = 15.5e-6

structure = FusedProfile(
    fiber_radius=62.5e-6,
    fusion_degree=0.1,
    index=material.compute_refractive_index(wavelength),
)


for factor in [0, 10e-6]:
    structure.randomize_core_position(random_factor=factor)

    structure.plot(show_centers=True, show_cores=True)


# -

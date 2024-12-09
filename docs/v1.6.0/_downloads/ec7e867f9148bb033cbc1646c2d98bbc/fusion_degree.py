"""
Effect of fusion degree
=======================
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

for fusion_degree in ['auto', 0.1, 0.3, 0.6, 0.9, 1.0]:
    structure.fusion_degree = fusion_degree

    structure.plot()


# -

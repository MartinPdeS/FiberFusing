"""
Effect of translation
=====================
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

# %%
shift = (0, 0)
structure.translate(shift)
structure.plot()

# %%
shift = (20e-6, 0)
structure.translate(shift)
structure.plot()

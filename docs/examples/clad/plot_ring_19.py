"""
19x19 Ring - Clad
=================
"""

# %%
from FiberFusing.configuration.ring import FusedProfile_19x19 as FusedProfile
from PyOptik import MaterialBank

material = MaterialBank.fused_silica

wavelength = 15.5e-6

clad = FusedProfile(
    fiber_radius=62.5e-6,
    index=material.compute_refractive_index(wavelength),
)

clad.plot()

# -

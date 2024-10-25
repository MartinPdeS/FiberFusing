"""
5x5 Line - Clad
===============
"""

# %%
from FiberFusing.configuration.line import FusedProfile_05x05 as FusedProfile
from PyOptik import MaterialBank

material = MaterialBank.fused_silica

wavelength = 15.5e-6

clad = FusedProfile(
    fiber_radius=62.5e-6,
    fusion_degree=0.3,
    index=material.compute_refractive_index(wavelength),
)

clad.plot()

# -

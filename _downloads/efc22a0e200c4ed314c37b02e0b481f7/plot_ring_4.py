"""
4x4 Ring - Clad
===============
"""

# %%
from FiberFusing.configuration.ring import FusedProfile_04x04 as FusedProfile

clad = FusedProfile(
    fiber_radius=62.5e-6,
    fusion_degree=0.9,
    index=1.4444,
    core_position_scrambling=0
)

clad.plot()

# -

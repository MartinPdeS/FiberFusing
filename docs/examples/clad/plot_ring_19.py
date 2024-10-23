"""
19x19 Ring - Clad
=================
"""

# %%
from FiberFusing.configuration.ring import FusedProfile_19x19 as FusedProfile


clad = FusedProfile(
    fiber_radius=62.5e-6,
    index=1.4444,
    core_position_scrambling=0
)

clad.plot()

# -

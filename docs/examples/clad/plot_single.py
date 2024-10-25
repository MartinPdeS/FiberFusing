"""
1x1 Ring - Clad
===============
"""

# %%
from FiberFusing.configuration.ring import FusedProfile_01x01 as FusedProfile

clad = FusedProfile(
    fiber_radius=62.5e-6,
    index=1.4444,
)

clad.plot()

# -

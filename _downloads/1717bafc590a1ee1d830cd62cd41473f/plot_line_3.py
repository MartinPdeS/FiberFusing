"""
3x3 Line - Clad
===============
"""

# %%
from FiberFusing.configuration.line import FusedProfile_03x03 as FusedProfile


clad = FusedProfile(
    fiber_radius=62.5e-6,
    fusion_degree=0.1,
    index=1.4444,
    core_position_scrambling=0
)

clad.plot(show_cores=True, show_centers=True)

# -

"""
5x5 Line - Clad
===============
"""

# %%
from FiberFusing.configuration.line import FusedProfile_05x05 as FusedProfile


clad = FusedProfile(
    fiber_radius=62.5e-6,
    fusion_degree=0.3,
    index=1.4444,
    core_position_scrambling=0
)

clad.plot()

# -

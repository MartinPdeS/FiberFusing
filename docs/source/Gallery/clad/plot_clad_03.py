"""
3x3 Ring - Clad
===============
"""

from FiberFusing.configuration.ring import FusedProfile_03x03 as FusedProfile

clad = FusedProfile(
    fiber_radius=62.5,
    fusion_degree=0.3,
    index=1.4444,
    core_position_scrambling=0
)

figure = clad.plot()

_ = figure.show()


# -

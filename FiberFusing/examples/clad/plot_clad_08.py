"""
3x3 Line - Clad
===============
"""

from FiberFusing.configuration.line import FusedProfile_03x03 as FusedProfile


clad = FusedProfile(
    fiber_radius=62.5e-6,
    fusion_degree=0.3,
    index=1.4444,
    core_position_scrambling=0
)

figure = clad.plot()

_ = figure.show()


# -

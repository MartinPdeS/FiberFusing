"""
1x1 Ring - Clad
===============
"""

from FiberFusing.profile import Profile, StructureType

profile = Profile()

profile.add_center_fiber(fiber_radius=62.5e-6)

profile.plot(show_cores=True, show_centers=True)


# -

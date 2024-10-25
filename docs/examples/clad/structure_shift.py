"""
Effect of fusion degree
=======================
"""

# %%
from FiberFusing.configuration.line import FusedProfile_02x02 as FusedProfile


structure = FusedProfile(
    fiber_radius=62.5e-6,
    fusion_degree=0.1,
    index=1.4444,
)

for shift in [(0, 0), (20e-6, 0)]:
    structure.translate(shift)

    structure.plot()


# -

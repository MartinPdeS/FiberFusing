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
    core_position_scrambling=0
)

for fusion_degree in ['auto', 0.1, 0.3, 0.6, 0.9, 1.0]:
    structure.fusion_degree = fusion_degree

    structure.plot()


# -

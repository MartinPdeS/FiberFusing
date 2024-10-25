"""
Effect of core randomization
============================
"""

# %%
from FiberFusing.configuration.line import FusedProfile_02x02 as FusedProfile


structure = FusedProfile(
    fiber_radius=62.5e-6,
    fusion_degree=0.1,
    index=1.4444,
)


for factor in [0, 10e-6]:
    structure.randomize_core_position(random_factor=factor)

    structure.plot(show_centers=True, show_cores=True)


# -

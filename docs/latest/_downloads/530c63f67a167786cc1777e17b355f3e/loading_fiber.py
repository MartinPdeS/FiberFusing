"""
Loading and plotting a single fiber structure
=============================================
"""

from FiberFusing.fiber import load_fiber

fiber = load_fiber('SMF28', clad_refractive_index=1.444, position=(0, 0))

fiber.plot()

# %%
fiber = load_fiber('DCF1300S_42', clad_refractive_index=1.444, position=(0, 0))

fiber.plot()


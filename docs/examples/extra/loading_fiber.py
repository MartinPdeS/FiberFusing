"""
Loading and plotting a single fiber structure
=============================================
"""

from FiberFusing.fiber import FiberLoader

fiber_loader = FiberLoader()

fiber = fiber_loader.load_fiber('SMF28', clad_refractive_index=1.444, position=(0, 0))

fiber.plot()

# %%
fiber = fiber_loader.load_fiber('DCF1300S_42', clad_refractive_index=1.444, position=(0, 0))

fiber.plot()


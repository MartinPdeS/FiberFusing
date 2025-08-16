"""
3x3 Line - Geometry Visualization
=================================
This script demonstrates how to create and visualize a 3x3 line geometry using the FiberFusing library.
"""

from FiberFusing import Geometry, BoundaryMode, BackGround
from FiberFusing.fiber.catalogue import load_fiber
from FiberFusing.profile import Profile, StructureType



# %%
# Set up the background medium (air)
air_background = BackGround(index=1.0)

# %%
# Create the cladding structure based on the fused fiber profile
profile = Profile()

profile.add_structure(
    structure_type=StructureType.LINEAR,
    number_of_fibers=3,
    fusion_degree=0.3,
    fiber_radius=62.5e-6,
    compute_fusing=True
)

profile.index = 1.4444

# %%
# Load fibers (e.g., SMF-28) positioned at the cores of the cladding structure
fibers = [
    load_fiber('SMF28', wavelength=1.5e-6, position=core_position)
    for core_position in profile.cores
]

# %%
# Set up the geometry with the defined background, cladding structure, and resolution
geometry = Geometry(
    background=air_background,
    additional_structure_list=[profile],
    x_bounds=BoundaryMode.CENTERING,
    y_bounds=BoundaryMode.CENTERING,
    resolution=250
)

# %%
# Add the fibers to the geometry
geometry.add_fiber(*fibers)

# %%
# Plot the resulting geometry
geometry.plot()

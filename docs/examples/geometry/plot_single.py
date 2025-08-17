"""
1x1 Geometry Visualization
==========================
This script demonstrates how to create and visualize a 1x1 geometry using the FiberFusing library.
"""

from FiberFusing import Geometry, BoundaryMode, BackGround
from FiberFusing.fiber.catalogue import load_fiber
from FiberFusing.profile import Profile, StructureType
from PyOptik import MaterialBank

# %%
# Define the operational parameters
wavelength = 1.55e-6  # Wavelength in meters (1.55 micrometers)

# Set up the background medium (air)
air_background = BackGround(index=1.0)

# Create the profile structure based on the fused fiber profile
profile = Profile()

profile.add_center_fiber(
    fiber_radius=62.5e-6
)

profile.index = MaterialBank.fused_silica.compute_refractive_index(wavelength)  # Refractive index of silica at the specified wavelength


# Load the fiber (e.g., SMF-28) positioned at the core of the profile structure
fibers = [
    load_fiber('SMF28', wavelength=wavelength, position=core_position)
    for core_position in profile.cores
]

# Set up the geometry with the defined background, profile structure, and resolution
geometry = Geometry(
    background=air_background,
    additional_structure_list=[profile],
    x_bounds=BoundaryMode.CENTERING,
    y_bounds=BoundaryMode.CENTERING,
    resolution=250
)

# Add the fiber to the geometry
geometry.add_fiber(*fibers)

geometry.initialize_geometry()

# Plot the resulting geometry
geometry.plot()

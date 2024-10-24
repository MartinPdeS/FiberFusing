"""
1x1 Geometry Visualization
==========================
This script demonstrates how to create and visualize a 1x1 geometry using the FiberFusing library.
"""

from FiberFusing import Geometry, BackGround
from FiberFusing.fiber.catalogue import load_fiber
from FiberFusing.configuration.ring import FusedProfile_01x01
from PyOptik import MaterialBank

# %%
# Define the operational parameters
wavelength = 1.55e-6  # Wavelength in meters (1.55 micrometers)

# Set up the background medium (air)
air_background = BackGround(index=1.0)

# Create the cladding structure based on the fused fiber profile
cladding = FusedProfile_01x01(
    fiber_radius=62.5e-6,  # Radius of the fiber in the cladding (in meters)
    index=MaterialBank.fused_silica.compute_refractive_index(wavelength)  # Refractive index of silica at the specified wavelength
)

# Load the fiber (e.g., SMF-28) positioned at the core of the cladding structure
fibers = [
    load_fiber('SMF28', wavelength=wavelength, position=core_position)
    for core_position in cladding.cores
]

# Set up the geometry with the defined background, cladding structure, and resolution
geometry = Geometry(
    background=air_background,
    additional_structure_list=[cladding],
    x_bounds='centering',
    y_bounds='centering',
    resolution=250
)

# Add the fiber to the geometry
geometry.add_fiber(*fibers)

# Plot the resulting geometry
geometry.plot()

"""
1x1 Geometry Visualization
==========================
This script demonstrates how to create and visualize a 1x1 geometry using the FiberFusing library.
"""

from FiberFusing import Geometry, DomainAlignment, BackGround
from FiberFusing.fiber import FiberLoader
from FiberFusing.profile import Profile


# Set up the background medium (air)
air_background = BackGround(refractive_index=1.0)

# Create the profile structure based on the fused fiber profile
profile = Profile()

profile.add_center_fiber(
    fiber_radius=62.5e-6
)

profile.refractive_index = 1.4444  # Refractive index of silica at the specified wavelength


# Load the fiber (e.g., SMF-28) positioned at the core of the profile structure
fiber_loader = FiberLoader()
fibers = [
    fiber_loader.load_fiber('SMF28', clad_refractive_index=profile.refractive_index, position=core_position)
    for core_position in profile.cores
]

# Set up the geometry with the defined background, profile structure, and resolution
geometry = Geometry(
    x_bounds=DomainAlignment.CENTERING,
    y_bounds=DomainAlignment.CENTERING,
    resolution=250
)

# Add the fiber to the geometry
geometry.add_structure(air_background, profile, *fibers)

geometry.initialize()

# Plot the resulting geometry
geometry.plot()

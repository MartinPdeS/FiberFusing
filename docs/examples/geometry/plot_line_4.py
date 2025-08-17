"""
4x4 Line - Geometry Visualization
=================================
This script demonstrates how to create and visualize a 4x4 line geometry using the FiberFusing library.
"""

from FiberFusing import Geometry, BoundaryMode, BackGround
from FiberFusing.fiber import load_fiber
from FiberFusing.profile import Profile, StructureType
from PyOptik import MaterialBank

# %%
# Define the operational parameters
wavelength = 1.55e-6  # Wavelength in meters (1.55 micrometers)

# Set up the background medium (air)
air_background = BackGround(refractive_index=1.0)

# Create the cladding structure based on the fused fiber profile
profile = Profile()

profile.add_structure(
    structure_type=StructureType.LINEAR,
    number_of_fibers=4,
    fusion_degree=0.4,
    fiber_radius=62.5e-6,
    compute_fusing=True
)

profile.refractive_index = MaterialBank.fused_silica.compute_refractive_index(wavelength)  # Refractive index of silica at the specified wavelength

# Load fibers (e.g., SMF-28) positioned at the cores of the cladding structure
fibers = [
    load_fiber('SMF28', clad_refractive_index=profile.refractive_index, position=core_position)
    for core_position in profile.cores
]

# Set up the geometry with the defined background, cladding structure, and resolution
geometry = Geometry(
    x_bounds=BoundaryMode.CENTERING,
    y_bounds=BoundaryMode.CENTERING,
    resolution=250
)

# Add the fibers to the geometry
geometry.add_structure(air_background, profile, *fibers)

geometry.initialize()

# Plot the resulting geometry
geometry.plot()

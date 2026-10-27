.. _theory:

Theoretical background
======================


Numerical behavior and diagnostics
----------------------------------

Fusion moves equal-radius fiber centers closer together, then optimizes the
virtual connections to restore the summed area of the original fiber polygons.
This is a geometric model, rather than a general physical simulation of glass
flow. Circle boundaries are polygonal approximations; ``resolution`` is the
number of segments per quadrant (passed to Shapely as ``quad_segs``).

After adding fused structures, inspect ``profile.fusion_diagnostics``. Each entry
contains ``area_residual`` (absolute area error in squared geometry units) and
``relative_area_residual`` (absolute error divided by the original polygon-area
sum). ``FiberLine`` and ``FiberRing`` expose these same attributes after
``compute_optimal_structure()``. These diagnostics measure area conservation,
not agreement with experimental fibers or exact analytical circle areas.
Optimizer failure or nonfinite results raise ``RuntimeError``; a failed assembly
is not appended to a profile. Solver success alone does not impose a universal
residual threshold, so applications should check the reported relative error
against their required accuracy.

Profile rotation uses degrees about the origin. Translation and rotation move
both nominal and shifted cores exactly once and preserve areas. Position scaling
moves fiber centers about the origin while retaining fiber radii. It recomputes
fused connections and optimized cores; previously randomized offsets are reset
for fused assemblies. Failed recomputation leaves the original profile intact.
Cached unions are invalidated after profile edits. Modify profiles through their
methods rather than mutating the public geometry lists directly.

``randomize_core_positions(factor, seed=42)`` draws independent uniform shifts
per coordinate in ``[-factor, factor]`` around the nominal core. Alternatively,
pass a NumPy ``Generator`` using ``rng=``. Nominal cores remain unchanged, repeated
calls replace rather than accumulate offsets, and zero leaves existing shifted
cores unchanged. This replaces the former positive-only, global-RNG behavior.
Use the same coordinate units for the factor and geometry.

Raster masks approximate the polygon on the supplied sampling grid. Refine the
grid to assess discretization error; individual refinements need not improve
monotonically because boundary pixels change discretely.

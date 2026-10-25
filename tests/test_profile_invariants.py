"""Deterministic scientific and state-integrity regressions."""

from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
import pytest
from shapely import affinity
from shapely.geometry import Point

from FiberFusing.coordinate_system import CoordinateSystem
from FiberFusing.profile import Profile, StructureType
from FiberFusing.shapes.circle import Circle
from FiberFusing.structures import FiberLine, FiberRing


def coordinates(point):
    return np.array([point.x, point.y])


@pytest.mark.parametrize("cached", [False, True])
def test_transforms_apply_once(cached):
    profile = Profile().add_single_fiber(1, (2, 3))
    if cached:
        _ = profile.clad_structure
    original = profile.fiber_list[0]._shapely_object
    profile.rotate(90).translate((4, 5))
    expected = affinity.translate(affinity.rotate(original, 90, origin=(0, 0)), 4, 5)
    assert profile.clad_structure._shapely_object.equals_exact(expected, 1e-12)
    for point in (profile.fiber_list[0].core, profile.cores[0]):
        np.testing.assert_allclose(coordinates(point), [1, 7])


def test_assembly_edits_invalidate_cache():
    profile = Profile().add_single_fiber(1)
    area = profile.clad_structure.area
    profile.add_single_fiber(1, (3, 0))
    assert profile.clad_structure.area == pytest.approx(2 * area)
    profile.add_custom_fiber(Circle(radius=1, position=(6, 0)))
    assert profile.clad_structure.area == pytest.approx(3 * area)
    profile.scale_position(2)
    np.testing.assert_allclose([f.center.x for f in profile.fiber_list], [0, 6, 12], atol=1e-12)
    assert profile.clad_structure.area == pytest.approx(3 * area)


@pytest.mark.parametrize("value", [[], "wrong", -1, 2, np.nan, np.inf])
def test_bad_fusion_setter_preserves_state(value):
    profile = Profile().add_single_fiber(1)
    geometry = profile.clad_structure
    with pytest.raises(ValueError):
        profile.fusion_degree = value
    assert len(profile.fiber_list) == 1
    assert profile.clad_structure is geometry


@pytest.mark.parametrize(
    "kwargs",
    [
        dict(fusion_degree=np.nan),
        dict(number_of_fibers=0),
        dict(fiber_radius=np.inf),
        dict(position_shift=[np.nan, 0]),
        dict(scale_position=-1),
    ],
)
def test_invalid_assembly_is_atomic(kwargs):
    profile = Profile().add_single_fiber(1)
    options = dict(structure_type=StructureType.LINEAR, number_of_fibers=2, fiber_radius=1)
    options.update(kwargs)
    with pytest.raises(ValueError):
        profile.add_structure(**options)
    assert len(profile.fiber_list) == len(profile.structure_list) == 1


def test_failed_optimization_does_not_append():
    profile = Profile().add_single_fiber(1)
    with patch.object(FiberLine, "compute_optimal_structure", side_effect=RuntimeError("failed")):
        with pytest.raises(RuntimeError):
            profile.add_structure(StructureType.LINEAR, 2, 1, 0.4)
    assert len(profile.fiber_list) == len(profile.structure_list) == 1


def test_seeded_randomization_preserves_nominal_cores():
    profile = Profile()
    for x in range(100):
        profile.add_single_fiber(1, (x * 3, 0))
    nominal = np.array([coordinates(f.core) for f in profile.fiber_list])
    profile.randomize_core_positions(0.2, seed=42)
    first = np.array([coordinates(p) for p in profile.cores])
    profile.randomize_core_positions(0.2, rng=np.random.default_rng(42))
    np.testing.assert_array_equal(first, [coordinates(p) for p in profile.cores])
    np.testing.assert_array_equal(nominal, [coordinates(f.core) for f in profile.fiber_list])
    shifts = first - nominal
    assert shifts.min() < 0 < shifts.max()
    assert abs(shifts).max() <= 0.2
    assert abs(shifts.mean()) < 0.03
    with pytest.raises(ValueError):
        profile.randomize_core_positions(0.2, seed=1, rng=np.random.default_rng())
    with pytest.raises(ValueError):
        profile.randomize_core_positions(-1)
    np.testing.assert_array_equal(first, [coordinates(p) for p in profile.cores])


@pytest.mark.parametrize("cls", [FiberLine, FiberRing])
@pytest.mark.parametrize("radius", [1.0, 62.5e-6])
def test_fusion_area_validity_and_symmetry(cls, radius):
    structure = cls(3, radius)
    structure.set_fusion_degree(0.4)
    structure.initialize_cores()
    structure.init_connected_fibers()
    structure.compute_optimal_structure()
    geometry = structure.fused_structure._shapely_object
    target = sum(f.area for f in structure.fiber_list)
    assert geometry.is_valid
    assert structure.area_residual == pytest.approx(abs(geometry.area - target), abs=target * 1e-12)
    assert structure.relative_area_residual < 2e-3
    mirrored = affinity.scale(geometry, xfact=-1, yfact=1, origin=(0, 0))
    assert geometry.symmetric_difference(mirrored).area / target < 1e-8


def test_optimizer_reapplies_reported_minimum():
    structure = FiberLine(2, 1)
    structure.set_fusion_degree(0.4)
    structure.initialize_cores()
    structure.init_connected_fibers()
    with patch(
        "FiberFusing.connection.connection_optimization.minimize_scalar",
        return_value=SimpleNamespace(success=True, x=0.3, fun=0),
    ):
        assert structure.find_optimal_virtual_shift(None) == 0.3
    assert structure.virtual_shift == 0.3
    with patch(
        "FiberFusing.connection.connection_optimization.minimize_scalar",
        return_value=SimpleNamespace(success=False, x=0.3, fun=0, message="failed"),
    ):
        with pytest.raises(RuntimeError, match="failed"):
            structure.find_optimal_virtual_shift(None)


def test_buffer_resolution_preserves_polygon():
    circle = Circle(radius=2, position=(0, 0), resolution=32)
    assert circle._shapely_object.equals_exact(Point(0, 0).buffer(2, quad_segs=32), 0)


def test_raster_area_refines_towards_polygon_area():
    profile = Profile().add_single_fiber(1)
    errors = []
    for n in (31, 241):
        grid = CoordinateSystem(nx=n, ny=n, x_min=-1.5, x_max=1.5, y_min=-1.5, y_max=1.5)
        mask = profile.get_rasterized_mesh(grid)
        estimated = mask.sum() * (3 / (n - 1)) ** 2
        errors.append(abs(estimated - profile.clad_structure.area))
    assert errors[1] < errors[0]
    assert errors[1] / profile.clad_structure.area < 0.01


@pytest.mark.parametrize("cached", [False, True])
def test_fused_transform_and_rescaling(cached):
    profile = Profile()
    profile.add_structure(StructureType.LINEAR, 2, 62.5e-6, 0.4)
    original = profile.structure_list[0]._shapely_object
    original_cores = np.array([coordinates(p) for p in profile.cores])
    if cached:
        _ = profile.clad_structure
    profile.rotate(90).translate((1e-5, 2e-5))
    expected = affinity.translate(affinity.rotate(original, 90, origin=(0, 0)), 1e-5, 2e-5)
    assert profile.clad_structure._shapely_object.equals_exact(expected, 1e-15)
    expected_cores = np.column_stack((-original_cores[:, 1], original_cores[:, 0])) + [1e-5, 2e-5]
    np.testing.assert_allclose([coordinates(p) for p in profile.cores], expected_cores, atol=1e-15)
    centers = np.array([coordinates(f.center) for f in profile.fiber_list])
    profile.scale_position(0.9)
    np.testing.assert_allclose(
        [coordinates(f.center) for f in profile.fiber_list], 0.9 * centers, atol=1e-15
    )
    assert profile.clad_structure._shapely_object.is_valid
    assert profile.fusion_diagnostics[0]["relative_area_residual"] < 1e-6


@pytest.mark.parametrize("cls", [FiberLine, FiberRing])
def test_single_fiber_and_invalid_constructor(cls):
    with pytest.raises(ValueError):
        cls(0, 1)
    with pytest.raises(ValueError):
        cls(2, np.nan)
    structure = cls(1, 1)
    structure.initialize_cores()
    structure.init_connected_fibers()
    structure.compute_optimal_structure()
    assert structure.relative_area_residual == pytest.approx(0)


def test_failed_rescaling_preserves_profile():
    profile = Profile()
    profile.add_structure(StructureType.LINEAR, 2, 1, 0.4)
    geometry = profile.clad_structure
    cores = np.array([coordinates(p) for p in profile.cores])
    with patch.object(FiberLine, "compute_optimal_structure", side_effect=RuntimeError("failed")):
        with pytest.raises(RuntimeError):
            profile.scale_position(0.9)
    assert profile.clad_structure is geometry
    np.testing.assert_array_equal([coordinates(p) for p in profile.cores], cores)


@pytest.mark.parametrize("kwargs", [dict(fiber_radius=np.nan), dict(position=(np.inf, 0))])
def test_invalid_single_fiber_preserves_state(kwargs):
    profile = Profile().add_single_fiber(1)
    geometry = profile.clad_structure
    options = dict(fiber_radius=1, position=(0, 0))
    options.update(kwargs)
    with pytest.raises(ValueError):
        profile.add_single_fiber(**options)
    assert len(profile.fiber_list) == 1
    assert profile.clad_structure is geometry

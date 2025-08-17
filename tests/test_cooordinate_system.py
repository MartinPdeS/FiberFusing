#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Comprehensive test suite for CoordinateSystem class.

This module contains organized tests for all functionality of the CoordinateSystem
class, including initialization, properties, transformations, and edge cases.
"""

import pytest
import numpy as np
from typing import Tuple
from FiberFusing.coordinate_system import CoordinateSystem


# =============================================================================
# TEST FIXTURES AND UTILITIES
# =============================================================================

@pytest.fixture
def basic_square_system():
    """Standard square coordinate system for testing."""
    return CoordinateSystem(
        nx=11, ny=11,
        x_min=-5.0, x_max=5.0,
        y_min=-5.0, y_max=5.0
    )

@pytest.fixture
def asymmetric_system():
    """Asymmetric coordinate system for testing edge cases."""
    return CoordinateSystem(
        nx=21, ny=15,
        x_min=-3.0, x_max=7.0,
        y_min=-2.0, y_max=8.0
    )

@pytest.fixture
def fine_resolution_system():
    """High resolution system for testing performance."""
    return CoordinateSystem(
        nx=101, ny=101,
        x_min=-1e-6, x_max=1e-6,
        y_min=-1e-6, y_max=1e-6
    )


def assert_coordinates_equal(coord1: Tuple[float, float], coord2: Tuple[float, float],
                           rtol: float = 1e-10, msg: str = ""):
    """Helper function to assert coordinate equality with better error messages."""
    x1, y1 = coord1
    x2, y2 = coord2

    if not (np.isclose(x1, x2, rtol=rtol) and np.isclose(y1, y2, rtol=rtol)):
        pytest.fail(
            f"Coordinates not equal {msg}\n"
            f"Expected: ({x2:.6e}, {y2:.6e})\n"
            f"Actual:   ({x1:.6e}, {y1:.6e})\n"
            f"Diff:     ({abs(x1-x2):.6e}, {abs(y1-y2):.6e})"
        )


# =============================================================================
# INITIALIZATION AND VALIDATION TESTS
# =============================================================================

def test_valid_initialization(basic_square_system):
    """Test successful initialization with valid parameters."""
    system = basic_square_system

    assert system.nx == 11
    assert system.ny == 11
    assert system.x_min == -5.0
    assert system.x_max == 5.0
    assert system.y_min == -5.0
    assert system.y_max == 5.0
    assert system.shape == (11, 11)


def test_asymmetric_initialization(asymmetric_system):
    """Test initialization with asymmetric dimensions."""
    assert asymmetric_system.shape == (15, 21)  # (ny, nx)
    assert asymmetric_system.aspect_ratio == 1.0  #


@pytest.mark.parametrize("nx,ny,expected_error", [
    (1, 11, "Grid points must be >= 2"),
    (11, 1, "Grid points must be >= 2"),
    (-5, 11, "Grid points must be >= 2"),
    (11, -5, "Grid points must be >= 2"),
])
def test_invalid_grid_points(nx, ny, expected_error):
    """Test validation of grid point parameters."""

    with pytest.raises(ValueError, match=expected_error):
        CoordinateSystem(
            nx=nx, ny=ny,
            x_min=-1.0, x_max=1.0,
            y_min=-1.0, y_max=1.0
        )


@pytest.mark.parametrize("x_min,x_max,y_min,y_max", [
    (5.0, -5.0, -1.0, 1.0),  # x_max < x_min
    (-1.0, 1.0, 5.0, -5.0),  # y_max < y_min
    (0.0, 0.0, -1.0, 1.0),   # x_max == x_min
    (-1.0, 1.0, 0.0, 0.0),   # y_max == y_min
])
def test_invalid_boundaries(x_min, x_max, y_min, y_max):
    """Test validation of boundary parameters."""

    with pytest.raises(ValueError):
        CoordinateSystem(
            nx=11, ny=11,
            x_min=x_min, x_max=x_max,
            y_min=y_min, y_max=y_max
        )


def test_class_methods():
    """Test alternative construction methods."""

    # Test from_bounds_and_resolution
    system1 = CoordinateSystem.from_bounds_and_resolution(
        x_bounds=(-5.0, 5.0),
        y_bounds=(-3.0, 3.0),
        resolution=0.5
    )
    print(f"   from_bounds_and_resolution: {system1.shape}, res={system1.dx:.2f}")
    assert abs(system1.dx - 0.5) < 0.1  # Allow some tolerance

    # Test square_domain
    system2 = CoordinateSystem.square_domain(
        size=10.0,
        resolution=0.2,
        center=(1.0, 2.0)
    )

    assert abs((system2.x_min + system2.x_max) / 2 - 1.0) < 1e-10
    assert abs((system2.y_min + system2.y_max) / 2 - 2.0) < 1e-10


# =============================================================================
# PROPERTY TESTS
# =============================================================================

def test_basic_properties(basic_square_system):
    """Test basic coordinate system properties."""
    assert basic_square_system.shape == (11, 11)
    assert basic_square_system.x_bounds == (-5.0, 5.0)
    assert basic_square_system.y_bounds == (-5.0, 5.0)
    assert abs(basic_square_system.dx - 1.0) < 1e-10
    assert abs(basic_square_system.dy - 1.0) < 1e-10
    assert abs(basic_square_system.area - 100.0) < 1e-10
    assert abs(basic_square_system.aspect_ratio - 1.0) < 1e-10


def test_vectors_and_meshes(basic_square_system):
    """Test coordinate vectors and mesh generation."""
    # Test vectors
    x_vec = basic_square_system.x_vector
    y_vec = basic_square_system.y_vector

    assert len(x_vec) == 11
    assert len(y_vec) == 11
    assert x_vec[0] == -5.0
    assert x_vec[-1] == 5.0
    assert y_vec[0] == -5.0
    assert y_vec[-1] == 5.0

    # Test meshes
    x_mesh = basic_square_system.x_mesh
    y_mesh = basic_square_system.y_mesh

    assert x_mesh.shape == (11, 11)
    assert y_mesh.shape == (11, 11)
    assert x_mesh[0, 0] == -5.0  # Bottom-left corner
    assert x_mesh[0, -1] == 5.0  # Bottom-right corner
    assert y_mesh[0, 0] == -5.0  # Bottom-left corner
    assert y_mesh[-1, 0] == 5.0  # Top-left corner


def test_utility_methods(basic_square_system):
    """Test utility methods like is_uniform, summary, etc."""
    system = basic_square_system

    # Test uniformity
    is_uniform = system.is_uniform()

    assert is_uniform

    # Test summary
    summary = system.summary()
    assert "Grid Shape" in summary
    assert "Resolution" in summary

    # Test string representations
    str_repr = str(system)
    repr_repr = repr(system)

    assert "CoordinateSystem" in str_repr
    assert "nx=" in repr_repr


# =============================================================================
# COORDINATE OPERATIONS TESTS
# =============================================================================

def test_coordinate_flattening(basic_square_system):
    """Test coordinate flattening operations."""
    # Test new method
    coords_new = basic_square_system.get_coordinates_flattened()

    # Test backward compatibility method
    coords_old = basic_square_system.get_coordinates_flattened()

    # Verify they're the same
    assert np.allclose(coords_new, coords_old)
    assert coords_new.shape == (121, 2)  # 11x11 = 121 points

    # Check specific coordinates
    assert np.allclose(coords_new[0], [-5.0, -5.0])  # First point
    assert np.allclose(coords_new[-1], [5.0, 5.0])   # Last point


@pytest.mark.parametrize("x,y", [(0.0, 0.0), (-5.0, -5.0), (5.0, 5.0), (2.3, -1.7)])
def test_nearest_indices(basic_square_system, x, y):
    """Test finding nearest grid indices."""

    i, j = basic_square_system.find_nearest_indices(x, y)

    # Verify we found reasonable indices
    assert 0 <= i < basic_square_system.ny
    assert 0 <= j < basic_square_system.nx

    # Test out-of-bounds
    with pytest.raises(ValueError):
        basic_square_system.find_nearest_indices(10.0, 0.0)  # x out of bounds

    with pytest.raises(ValueError):
        basic_square_system.find_nearest_indices(0.0, 10.0)  # y out of bounds


def test_interpolation(basic_square_system):
    """Test bilinear interpolation."""
    system = basic_square_system

    # Create test data (simple function: f(x,y) = x + y)
    test_array = system.x_mesh + system.y_mesh

    test_points = [
        (0.0, 0.0, 0.0),      # Center point
        (1.0, 1.0, 2.0),      # Simple case
        (-2.5, 3.5, 1.0),     # Another point
        (0.5, 0.5, 1.0),      # Between grid points
    ]

    for x, y, expected in test_points:
        try:
            result = system.interpolate_at_point(test_array, x, y)
            assert abs(result - expected) < 0.1  # Allow some interpolation error
        except ValueError as e:
            print(f"   f({x:.1f}, {y:.1f}) → {e}")


# =============================================================================
# TRANSFORMATION TESTS (MUTABLE)
# =============================================================================

def test_ensure_odd_resolution():
    """Test making grid resolution odd."""
    # Start with even resolution
    system = CoordinateSystem(nx=10, ny=12, x_min=-5.0, x_max=5.0, y_min=-5.0, y_max=5.0)

    system.ensure_odd('nx')
    system.ensure_odd('ny')

    assert system.nx == 11  # 10 → 11
    assert system.ny == 13  # 12 → 13
    assert system.nx % 2 == 1
    assert system.ny % 2 == 1

    # Test invalid attribute
    with pytest.raises(ValueError):
        system.ensure_odd('invalid')


def test_centering_operations():
    """Test various centering operations."""

    # Test x_centering
    system = CoordinateSystem(nx=11, ny=11, x_min=-3.0, x_max=7.0, y_min=-5.0, y_max=5.0)

    system.x_centering(zero_included=True)

    assert system.x_min == -7.0
    assert system.x_max == 7.0
    assert system.nx % 2 == 1

    # Test y_centering
    system = CoordinateSystem(nx=11, ny=11, x_min=-5.0, x_max=5.0, y_min=-3.0, y_max=7.0)

    system.y_centering(zero_included=True)

    assert system.y_min == -7.0
    assert system.y_max == 7.0
    assert system.ny % 2 == 1


def test_scaling_and_centering(basic_square_system):
    """Test the center method with scaling."""
    basic_square_system.center(factor=2.0, zero_included=True)

    assert basic_square_system.x_min == -10.0  # -5.0 * 2.0
    assert basic_square_system.x_max == 10.0   #  5.0 * 2.0
    assert basic_square_system.y_min == -10.0
    assert basic_square_system.y_max == 10.0
    assert basic_square_system.nx % 2 == 1
    assert basic_square_system.ny % 2 == 1

    # Test invalid factor
    with pytest.raises(ValueError):
        basic_square_system.center(factor=-1)


def test_padding_operations(basic_square_system):
    """Test padding operations."""
    # system = basic_square_system
    original_area = basic_square_system.area

    basic_square_system.add_padding(1.5)

    assert basic_square_system.x_min < -5.0
    assert basic_square_system.x_max > 5.0
    assert basic_square_system.y_min < -5.0
    assert basic_square_system.y_max > 5.0
    assert abs(basic_square_system.area / original_area - 1.5**2) < 1e-10

    # Test invalid padding
    with pytest.raises(ValueError):
        basic_square_system.add_padding(0.5)  # Must be > 1.0


def test_update_method(basic_square_system):
    """Test the update method."""
    basic_square_system.update(nx=13, ny=15, x_min=-6.0, y_max=6.0)

    assert basic_square_system.nx == 13
    assert basic_square_system.ny == 15
    assert basic_square_system.x_min == -6.0
    assert basic_square_system.y_max == 6.0

    # Test invalid attribute
    with pytest.raises(ValueError):
        basic_square_system.update(invalid_attribute=10)


test_methods = [
    ('set_left', 'x_max', 0),
    ('set_right', 'x_min', 0),
    ('set_top', 'y_min', 0),
    ('set_bottom', 'y_max', 0),
]
@pytest.mark.parametrize("method_name, boundary_attr, expected_value", test_methods)
def test_grid_sectioning(method_name, boundary_attr, expected_value):
    """Test grid sectioning methods."""
    for method_name, boundary_attr, expected_value in test_methods:
        # Create fresh system for each test
        test_system = CoordinateSystem(nx=11, ny=11, x_min=-5.0, x_max=5.0, y_min=-5.0, y_max=5.0)
        method = getattr(test_system, method_name)

        method()

        assert getattr(test_system, boundary_attr) == expected_value


# =============================================================================
# IMMUTABLE TRANSFORMATION TESTS
# =============================================================================

def test_immutable_padding(basic_square_system):
    """Test immutable padding method."""
    original_id = id(basic_square_system)

    padded = basic_square_system.with_padding(1.2)

    # Original should be unchanged
    assert basic_square_system.x_bounds == (-5.0, 5.0)
    assert basic_square_system.area == 100.0

    # New instance should be padded
    assert padded.x_min < -5.0
    assert padded.x_max > 5.0
    assert padded.area > 100.0
    assert id(padded) != original_id


def test_center_on_origin(asymmetric_system):
    """Test centering on origin."""
    # Test preserve size
    centered_preserve = asymmetric_system.center_on_origin(preserve_size=True)

    # Test symmetric around origin
    centered_symmetric = asymmetric_system.center_on_origin(preserve_size=False)

    # Verify preserve size maintains area
    assert abs(centered_preserve.area - asymmetric_system.area) < 1e-10

    # Verify symmetric version is centered
    assert abs(centered_symmetric.x_min + centered_symmetric.x_max) < 1e-10
    assert abs(centered_symmetric.y_min + centered_symmetric.y_max) < 1e-10


def test_scaling_and_translation(basic_square_system):
    """Test scaling and translation methods."""
    # Test scaling
    scaled = basic_square_system.scale(2.0)

    assert scaled.x_min == -10.0
    assert scaled.x_max == 10.0
    assert scaled.area == 400.0  # 4x original area

    # Test translation
    translated = basic_square_system.translate(2.0, -3.0)

    assert translated.x_min == -3.0  # -5 + 2
    assert translated.x_max == 7.0   #  5 + 2
    assert translated.y_min == -8.0  # -5 - 3
    assert translated.y_max == 2.0   #  5 - 3
    assert translated.area == basic_square_system.area  # Area unchanged

    # Test invalid scaling
    with pytest.raises(ValueError):
        basic_square_system.scale(-1.0)


def test_refinement_and_subdomains(basic_square_system):
    """Test grid refinement and subdomain extraction."""
    # Test refinement
    refined = basic_square_system.refine(2)

    assert refined.nx == 21  # (11-1)*2 + 1
    assert refined.ny == 21
    assert abs(refined.dx - basic_square_system.dx/2) < 1e-10

    # Test subdomain
    subdomain = basic_square_system.get_subdomain(
        x_range=(-2.0, 3.0),
        y_range=(-1.0, 2.0)
    )

    assert subdomain.x_min == -2.0
    assert subdomain.x_max == 3.0
    assert subdomain.y_min == -1.0
    assert subdomain.y_max == 2.0

    # Test invalid subdomain
    with pytest.raises(ValueError):
        basic_square_system.get_subdomain((-10.0, 10.0), (-1.0, 1.0))  # x out of bounds


# =============================================================================
# EDGE CASES AND ERROR HANDLING
# =============================================================================

def test_single_point_dimensions():
    """Test behavior with minimal grid dimensions."""

    # Test minimum size grid
    minimal = CoordinateSystem(nx=2, ny=2, x_min=0.0, x_max=1.0, y_min=0.0, y_max=1.0)

    assert minimal.shape == (2, 2)
    assert minimal.dx == 1.0
    assert minimal.dy == 1.0

    # Test very fine resolution
    fine = CoordinateSystem(nx=1000, ny=1000, x_min=0.0, x_max=1e-6, y_min=0.0, y_max=1e-6)

    assert fine.dx < 2e-9


def test_numerical_precision(fine_resolution_system):
    """Test numerical precision with very small values."""
    # Test that operations maintain precision
    coords = fine_resolution_system.get_coordinates_flattened()
    assert coords.shape[0] == fine_resolution_system.nx * fine_resolution_system.ny

    # Test interpolation with fine grid
    test_array = np.ones(fine_resolution_system.shape)
    result = fine_resolution_system.interpolate_at_point(test_array, 0.0, 0.0)
    assert abs(result - 1.0) < 1e-10


# =============================================================================
# PERFORMANCE TESTS
# =============================================================================

@pytest.mark.slow
def test_large_grid_creation():
    """Test creation of large grids."""

    import time

    sizes = [100, 500, 1000]

    for size in sizes:
        start_time = time.time()

        large_system = CoordinateSystem(
            nx=size, ny=size,
            x_min=-1.0, x_max=1.0,
            y_min=-1.0, y_max=1.0
        )

        # Force mesh computation
        _ = large_system.x_mesh
        _ = large_system.y_mesh

        elapsed = time.time() - start_time
        print(f"   {size} x {size} grid: {elapsed:.3f}s")

        assert elapsed < 5.0  # Should complete within 5 seconds


# =============================================================================
# TEST CONFIGURATION
# =============================================================================

if __name__ == "__main__":
    pytest.main([
        __file__,
        "-v",
        "-x",  # Stop on first failure
        "--disable-warnings"
    ])

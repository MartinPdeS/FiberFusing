import pytest
import numpy as np
from FiberFusing.coordinate_system import CoordinateSystem
from FiberFusing.fiber.generic_fiber import GenericFiber


@pytest.fixture
def generic_fiber():
    """Fixture for a GenericFiber instance with default values."""
    return GenericFiber(wavelength=1.55e-6)


def test_initialization(generic_fiber):
    """Test the initialization of GenericFiber."""
    assert generic_fiber.wavelength == 1.55e-6
    assert generic_fiber.position == (0, 0)
    assert len(generic_fiber.structure_list) > 0  # air structure should be added


def test_set_position(generic_fiber):
    """Test the set_position method."""
    new_position = (10.0, 20.0)
    generic_fiber.set_position(new_position)
    for structure in generic_fiber.structure_list:
        if structure.radius is not None:
            assert structure.position == new_position


def test_set_position_invalid():
    """Test set_position with invalid input."""
    fiber = GenericFiber(wavelength=1.55e-6)
    with pytest.raises(ValueError):
        fiber.set_position((10.0,))  # Invalid tuple length


def test_update_wavelength(generic_fiber):
    """Test the update_wavelength method."""
    new_wavelength = 1.3e-6
    generic_fiber.wavelength = new_wavelength
    assert generic_fiber.wavelength == new_wavelength


def test_update_wavelength_invalid():
    """Test update_wavelength with invalid input."""
    fiber = GenericFiber(wavelength=1.55e-6)
    with pytest.raises(ValueError):
        fiber.wavelength = -1.0e-6


def test_NA_to_core_index(generic_fiber):
    """Test the NA_to_core_index method."""
    NA = 0.2
    index_clad = 1.45
    core_index = generic_fiber.NA_to_core_index(NA, index_clad)
    assert np.isclose(core_index, np.sqrt(NA**2 + index_clad**2))


def test_NA_to_core_index_invalid(generic_fiber):
    """Test NA_to_core_index with invalid input."""
    with pytest.raises(ValueError):
        generic_fiber.NA_to_core_index(-0.1, 1.45)


def test_core_index_to_NA(generic_fiber):
    """Test the core_index_to_NA method."""
    interior_index = 1.47
    exterior_index = 1.45
    NA = generic_fiber.core_index_to_NA(interior_index, exterior_index)
    assert np.isclose(NA, np.sqrt(interior_index**2 - exterior_index**2))


def test_core_index_to_NA_invalid(generic_fiber):
    """Test core_index_to_NA with invalid input."""
    with pytest.raises(ValueError):
        generic_fiber.core_index_to_NA(1.4, 1.5)


def test_add_air(generic_fiber):
    """Test the add_air method."""
    initial_count = len(generic_fiber.structure_list)
    generic_fiber.add_air()
    assert len(generic_fiber.structure_list) == initial_count + 1


def test_shift_coordinates(generic_fiber):
    """Test the shift_coordinates method."""
    coordinate_system = CoordinateSystem(nx=10, ny=10, x_min=-1, x_max=1, y_min=-1, y_max=1)
    shifted_coords = generic_fiber.shift_coordinates(coordinate_system, 5.0, 10.0)
    assert shifted_coords.shape == (100, 2)


def test_get_shifted_distance_mesh(generic_fiber):
    """Test the get_shifted_distance_mesh method."""
    coordinate_system = CoordinateSystem(nx=10, ny=10, x_min=-1, x_max=1, y_min=-1, y_max=1)
    distance_mesh = generic_fiber.get_shifted_distance_mesh(coordinate_system, 1.0, 1.0)
    assert distance_mesh.shape == (10, 10)


if __name__ == "__main__":
    pytest.main(["-W", "error", __file__])

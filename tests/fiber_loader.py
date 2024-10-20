import pytest
from FiberFusing.fiber.generic_fiber import GenericFiber
from FiberFusing.fiber.catalogue import load_fiber, make_fiber


@pytest.fixture
def sample_structure_list():
    """Fixture that returns a sample list of fiber structures for testing."""
    return [
        {'name': 'core', 'index': 1.45, 'radius': 5e-6},
        {'name': 'cladding', 'index': 1.44, 'radius': 62.5e-6}
    ]


@pytest.fixture
def sample_fiber_name():
    """Fixture that returns a sample fiber name."""
    return "SMF28"


@pytest.fixture
def sample_wavelength():
    """Fixture that returns a sample wavelength."""
    return 1.55e-6  # Wavelength in meters


def test_load_fiber(sample_fiber_name, sample_wavelength):
    """Test the load_fiber function with a valid fiber name."""
    fiber = load_fiber(fiber_name=sample_fiber_name, wavelength=sample_wavelength, remove_cladding=False)
    assert isinstance(fiber, GenericFiber)
    assert fiber.wavelength == sample_wavelength
    assert len(fiber.structure_list) > 0, "The fiber should contain at least one structure."


def test_load_fiber_with_position(sample_fiber_name, sample_wavelength):
    """Test the load_fiber function with a specified position."""
    position = (1e-6, 2e-6)  # Arbitrary position
    fiber = load_fiber(fiber_name=sample_fiber_name, wavelength=sample_wavelength, position=position)
    assert fiber.position == position, "The fiber position should match the specified position."


def test_load_fiber_without_cladding(sample_fiber_name, sample_wavelength):
    """Test the load_fiber function with cladding removed."""
    fiber = load_fiber(fiber_name=sample_fiber_name, wavelength=sample_wavelength, remove_cladding=True)
    for structure in fiber.structure_list:
        assert 'cladding' not in structure.name.lower(), "Cladding should be removed from the fiber."


def test_make_fiber(sample_structure_list, sample_wavelength):
    """Test the make_fiber function with a sample structure list."""
    fiber = make_fiber(wavelength=sample_wavelength, structure_list=sample_structure_list)
    assert isinstance(fiber, GenericFiber)
    assert len(fiber.structure_list) == len(sample_structure_list) + 1, "The fiber should contain the specified number of structures."


def test_make_fiber_with_position(sample_structure_list, sample_wavelength):
    """Test the make_fiber function with a specified position."""
    position = (2e-6, 3e-6)  # Arbitrary position
    fiber = make_fiber(wavelength=sample_wavelength, structure_list=sample_structure_list, position=position)
    assert fiber.position == position, "The fiber position should match the specified position."


# Run the tests if the file is executed directly
if __name__ == "__main__":
    pytest.main(["-W error", __file__])

import pytest
import numpy as np
from FiberFusing.coordinate_system import CoordinateSystem


def test_initialization():
    # Test initialization with valid values
    system = CoordinateSystem(nx=11, ny=11, min_x=-5.0, max_x=5.0, min_y=-5.0, max_y=5.0)
    assert system.nx == 11
    assert system.ny == 11
    assert system.min_x == -5.0
    assert system.max_x == 5.0
    assert system.min_y == -5.0
    assert system.max_y == 5.0
    assert system.shape == (11, 11)


def test_shape_property():
    system = CoordinateSystem(nx=15, ny=20, min_x=-5.0, max_x=5.0, min_y=-5.0, max_y=5.0)
    assert system.shape == (20, 15)


def test_x_y_bounds_properties():
    system = CoordinateSystem(nx=11, ny=11, min_x=-5.0, max_x=5.0, min_y=-3.0, max_y=3.0)

    # Test x_bounds property
    assert system.x_bounds == (-5.0, 5.0)
    system.min_x, system.max_x = (-10.0, 10.0)
    assert system.min_x == -10.0
    assert system.max_x == 10.0

    # Test y_bounds property
    assert system.y_bounds == (-3.0, 3.0)
    system.min_y, system.max_y = (-8.0, 8.0)
    assert system.min_y == -8.0
    assert system.max_y == 8.0


def test_to_unstructured_coordinate():
    system = CoordinateSystem(nx=3, ny=3, min_x=-1.0, max_x=1.0, min_y=-1.0, max_y=1.0)
    coords = system.to_unstructured_coordinate()

    # Ensure the output shape matches the expected size
    assert coords.shape == (system.nx * system.ny, 2)

    # Check specific coordinates
    expected_coords = np.array([
        [-1.0, -1.0], [0.0, -1.0], [1.0, -1.0],
        [-1.0, 0.0], [0.0, 0.0], [1.0, 0.0],
        [-1.0, 1.0], [0.0, 1.0], [1.0, 1.0]
    ])
    assert np.allclose(coords, expected_coords)


def test_ensure_odd():
    system = CoordinateSystem(nx=10, ny=10, min_x=-5.0, max_x=5.0, min_y=-5.0, max_y=5.0)
    system.ensure_odd('nx')
    system.ensure_odd('ny')
    assert system.nx == 11
    assert system.ny == 11

    with pytest.raises(ValueError):
        system.ensure_odd('invalid')


def test_x_centering():
    system = CoordinateSystem(nx=11, ny=11, min_x=-3.0, max_x=7.0, min_y=-5.0, max_y=5.0)
    system.x_centering(zero_included=True)
    assert system.min_x == -7.0
    assert system.max_x == 7.0
    assert system.nx % 2 == 1


def test_y_centering():
    system = CoordinateSystem(nx=11, ny=11, min_x=-5.0, max_x=5.0, min_y=-3.0, max_y=7.0)
    system.y_centering(zero_included=True)
    assert system.min_y == -7.0
    assert system.max_y == 7.0
    assert system.ny % 2 == 1


def test_center_method():
    system = CoordinateSystem(nx=11, ny=11, min_x=-2.0, max_x=2.0, min_y=-2.0, max_y=2.0)
    system.center(factor=2.0, zero_included=True)
    assert system.min_x == -4.0
    assert system.max_x == 4.0
    assert system.min_y == -4.0
    assert system.max_y == 4.0
    assert system.nx % 2 == 1
    assert system.ny % 2 == 1

    with pytest.raises(ValueError):
        system.center(factor=-1)


def test_add_padding():
    system = CoordinateSystem(nx=11, ny=11, min_x=-5.0, max_x=5.0, min_y=-5.0, max_y=5.0)
    system.add_padding(1.5)
    assert system.min_x < -5.0
    assert system.max_x > 5.0
    assert system.min_y < -5.0
    assert system.max_y > 5.0

    with pytest.raises(ValueError):
        system.add_padding(-0.5)


def test_update_method():
    system = CoordinateSystem(nx=11, ny=11, min_x=-5.0, max_x=5.0, min_y=-5.0, max_y=5.0)
    system.update(nx=13, ny=15, min_x=-6.0, max_y=6.0)
    assert system.nx == 13
    assert system.ny == 15
    assert system.min_x == -6.0
    assert system.max_y == 6.0

    with pytest.raises(ValueError):
        system.update(invalid_attribute=10)


def test_set_left():
    system = CoordinateSystem(nx=11, ny=11, min_x=-5.0, max_x=5.0, min_y=-5.0, max_y=5.0)
    initial_dx = system.dx
    system.set_left()
    assert system.max_x == 0
    assert system.min_x == pytest.approx(-((system.nx - 1) * initial_dx))


def test_set_right():
    system = CoordinateSystem(nx=11, ny=11, min_x=-5.0, max_x=5.0, min_y=-5.0, max_y=5.0)
    initial_dx = system.dx
    system.set_right()
    assert system.min_x == 0
    assert system.max_x == pytest.approx((system.nx - 1) * initial_dx)


def test_set_top():
    system = CoordinateSystem(nx=11, ny=11, min_x=-5.0, max_x=5.0, min_y=-5.0, max_y=5.0)
    initial_dy = system.dy
    system.set_top()
    assert system.max_y == ((system.ny - 1) * initial_dy)
    assert system.min_y == 0


def test_set_bottom():
    system = CoordinateSystem(nx=11, ny=11, min_x=-5.0, max_x=5.0, min_y=-5.0, max_y=5.0)
    initial_dy = system.dy
    system.set_bottom()

    assert system.y_bounds[1] == 0
    assert system.y_bounds[0] == -(system.ny - 1) * initial_dy


# Run the tests if the file is executed directly
if __name__ == "__main__":
    pytest.main(["-W error", __file__])

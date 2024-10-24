import pytest
import numpy as np
import shapely.geometry as geo
from FiberFusing.coordinate_system import CoordinateSystem
from FiberFusing.components.polygon import Polygon
from unittest.mock import patch

@pytest.fixture
def sample_polygon():
    # Returns a simple polygon for testing
    coordinates = [(0, 0), (1, 0), (1, 1), (0, 1)]
    return Polygon(coordinates=coordinates)


@pytest.fixture
def sample_multipolygon():
    # Returns a MultiPolygon for testing
    poly1 = geo.Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
    poly2 = geo.Polygon([(2, 2), (3, 2), (3, 3), (2, 3)])
    multipolygon = geo.MultiPolygon([poly1, poly2])
    return Polygon(instance=multipolygon)


def test_initialization_with_coordinates():
    coordinates = [(0, 0), (1, 0), (1, 1), (0, 1)]
    polygon = Polygon(coordinates=coordinates)
    assert isinstance(polygon._shapely_object, geo.Polygon)
    assert polygon._shapely_object.exterior.coords[:4] == coordinates


def test_initialization_with_instance():
    polygon_instance = geo.Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
    polygon = Polygon(instance=polygon_instance)
    assert polygon._shapely_object.equals(polygon_instance)


def test_initialization_error():
    with pytest.raises(ValueError):
        Polygon()


def test_get_hole_no_holes(sample_polygon):
    hole = sample_polygon.get_hole()
    assert hole.is_empty, 'Hole should be marked as empty'


def test_remove_non_polygon_elements():
    collection = geo.GeometryCollection([
        geo.Point(0, 0),
        geo.LineString([(0, 0), (1, 1)]),
        geo.Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])
    ])
    polygon = Polygon(instance=collection)
    polygon.remove_non_polygon_elements()
    assert isinstance(polygon._shapely_object, geo.MultiPolygon)
    assert len(polygon._shapely_object.geoms) == 1


def test_keep_largest_polygon(sample_multipolygon):
    initial_num_polygons = len(sample_multipolygon._shapely_object.geoms)
    assert initial_num_polygons == 2, "Multipolygon do not shows the correct number of polygon"

    sample_multipolygon.keep_largest_polygon()
    assert isinstance(sample_multipolygon._shapely_object, geo.Polygon)


@patch('matplotlib.pyplot.show')
def test_plot(sample_polygon):
    sample_polygon.plot()
    # Check if the plot contains polygon elements; visual validation may be necessary.


def test_contains_points(sample_polygon):
    points = np.array([[0.5, 0.5], [1.5, 1.5]])
    result = sample_polygon.contains_points(points)
    assert np.array_equal(result, np.array([True, False]))


def test_rasterize(sample_polygon):
    coordinate_system = CoordinateSystem(
        nx=10, ny=10, min_x=-1, max_x=1, min_y=-1, max_y=1
    )

    result = sample_polygon.rasterize(coordinate_system)
    assert result.shape == (10, 10)


def test_polygon_hole_contains_points():
    coordinates = [(0, 0), (2, 0), (2, 2), (0, 2)]
    hole_coordinates = [(0.5, 0.5), (1.5, 0.5), (1.5, 1.5), (0.5, 1.5)]
    polygon_with_hole = geo.Polygon(coordinates, [hole_coordinates])
    polygon = Polygon(instance=polygon_with_hole)

    points = np.array([[0.3, 0.3], [1.0, 1.0], [0.1, 0.1]])
    result = polygon.contains_points(points)
    assert np.array_equal(result, np.array([True, False, True]))


if __name__ == "__main__":
    pytest.main(["-W error", __file__])

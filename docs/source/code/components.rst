_code_components:

Components Module
-----------------

.. autoclass:: FiberFusing.components.point.Point
    :members:
    :inherited-members:
    :member-order: bysource

    The `Point` class manages individual points in the coordinate system. It is used as a building block for defining fiber positions and manipulating coordinates.

.. autoclass:: FiberFusing.components.linestring.LineString
    :members:
    :inherited-members:
    :member-order: bysource

    The `LineString` class represents linear structures connecting points, useful for defining fiber alignments and connections. It includes methods for creating and manipulating these linear structures.

.. autoclass:: FiberFusing.components.polygon.Polygon
    :members:
    :inherited-members:
    :member-order: bysource

    The `Polygon` class manages polygonal shapes, which are essential for modeling complex geometries like fiber intersections and combined areas. This class supports operations such as intersection, union, and transformation.

.. autoclass:: FiberFusing.components.polygon.EmptyPolygon
    :members:
    :inherited-members:
    :member-order: bysource

    The `EmptyPolygon` class represents an empty polygon structure, used as a placeholder for initializing and managing polygonal geometries that may be populated later in the modeling process.


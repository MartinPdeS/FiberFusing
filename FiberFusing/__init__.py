from .geometry import Geometry, DomainAlignment  # noqa: F401
from .geometries.point import Point  # noqa: F401
from .geometries.linestring import LineString  # noqa: F401
from .geometries.polygon import Polygon, EmptyPolygon  # noqa: F401
from .shapes import Circle, Square  # noqa: F401
from .background import BackGround  # noqa: F401
from .optical_structure import CircleOpticalStructure  # noqa: F401
from .graded_index import GradedIndex  # noqa: F401
micro = 1e-6


try:
    from ._version import version as __version__  # noqa: F401

except ImportError:
    __version__ = "0.0.0"

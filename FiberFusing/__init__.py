from .geometry import Geometry  # noqa: F401
from .components.point import Point  # noqa: F401
from .components.linestring import LineString  # noqa: F401
from .components.polygon import Polygon, EmptyPolygon  # noqa: F401
from .buffer import Circle, Square  # noqa: F401
from .background import BackGround  # noqa: F401
from .optical_structure import CircleOpticalStructure  # noqa: F401
micro = 1e-6


try:
    from ._version import version as __version__  # noqa: F401

except ImportError:
    __version__ = "0.0.0"

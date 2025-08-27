from pydantic import ConfigDict

config_dict = ConfigDict(
    extra='forbid',
    arbitrary_types_allowed=True,
    kw_only=True
)

from .base_class import Alteration  # noqa: F401
from .point import Point  # noqa: F401
from .linestring import LineString  # noqa: F401
from .polygon import Polygon, EmptyPolygon  # noqa: F401


import FiberFusing._buffer as _buffer


class Fiber(_buffer.Circle):
    radius: float = None
    core: _buffer.Point = None
    center: _buffer.Point = None

    def __new__(cls, radius: float, center: list, name: str = ''):
        Instance = _buffer.Circle.__new__(cls, radius=radius, center=center)
        return Instance

    def __init__(self, radius: float, center: list, name: str = ''):
        self.radius = radius
        self.name = name
        self.center = center
        self.core = _buffer.Point([center.x, center.y])

        super(Fiber, self).__init__(radius=radius, center=center)

    def _render_(self, Ax):
        super()._render_(Ax)

        self.core._render_(Ax)
        self.center._render_(Ax)

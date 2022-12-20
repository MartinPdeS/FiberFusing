import numpy
from dataclasses import dataclass, field
from collections import defaultdict


class Namespace:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@dataclass
class Axes(object):
    n_x: int
    n_y: int
    x_bound: float
    y_bound: float
    symmetries: defaultdict[dict] = field(default_factory=lambda: {'left': 0, 'right': 0, 'top': 0, 'bottom': 0})

    def __post_init__(self):
        x_axis = numpy.linspace(*self.x_bound, self.n_x)
        y_axis = numpy.linspace(*self.y_bound, self.n_y)

        self._full_x_axis = None
        self._full_y_axis = None

        self.x = Namespace(n=self.n_x,
                           bounds=self.x_bound,
                           Vector=x_axis,
                           d=numpy.abs(x_axis[0] - x_axis[1]))

        self.y = Namespace(n=self.n_y,
                           bounds=self.y_bound,
                           Vector=y_axis,
                           d=numpy.abs(y_axis[0] - y_axis[1]))

        self.x.Mesh, self.y.Mesh = numpy.meshgrid(self.x.Vector, self.y.Vector)

        self.rho = numpy.sqrt(self.x.Mesh**2 + self.y.Mesh**2)

        self.dA = self.x.d * self.y.d

        self.Shape = numpy.array([self.n_x, self.n_y])

    @property
    def full_x_axis(self):
        if self._full_x_axis is None:
            self._full_x_axis, self._full_y_axis = self.get_full_axis()
        return self._full_x_axis

    @property
    def full_y_axis(self):
        if self._full_y_axis is None:
            self._full_x_axis, self._full_y_axis = self.get_full_axis()
        return self._full_y_axis

    def _extend_axis_(self, Axis: numpy.ndarray, sign: str):
        d = Axis[1] - Axis[0]

        if sign == "Plus":
            start = Axis[-1] + d
            Next = numpy.arange(0, Axis.size) * d + start
            Next = [Axis, Next]

        if sign == "Minus":
            stop = Axis[0]
            Next = numpy.arange(-Axis.size, 0) * d + stop
            Next = [Next, Axis]

        return numpy.concatenate(Next)

    def get_full_axis(self, symmetries: dict = None):
        if symmetries is None:
            symmetries = self.symmetries

        full_x_axis = self.x.Vector
        full_y_axis = self.y.Vector

        full_x_axis = self._add_right_axis_symmetry_(full_x_axis, symmetries=symmetries)

        full_x_axis = self._add_left_axis_symmetry_(full_x_axis, symmetries=symmetries)

        full_y_axis = self._add_top_axis_symmetry_(full_y_axis, symmetries=symmetries)

        full_y_axis = self._add_bottom_axis_symmetry_(full_y_axis, symmetries=symmetries)

        return full_x_axis, full_y_axis

    def _add_right_axis_symmetry_(self, full_x_axis, symmetries):
        match symmetries['right']:
            case 0: return full_x_axis

            case 1: return self._extend_axis_(Axis=full_x_axis, sign="Minus")

            case -1: return self._extend_axis_(Axis=full_x_axis, sign="Minus")

    def _add_left_axis_symmetry_(self, full_x_axis, symmetries):
        match symmetries['left']:
            case 0: return full_x_axis

            case 1: return self._extend_axis_(Axis=full_x_axis, sign="Plus")

            case -1: return self._extend_axis_(Axis=full_x_axis, sign="Plus")

    def _add_top_axis_symmetry_(self, full_y_axis, symmetries):
        match symmetries['top']:
            case 0: return full_y_axis

            case 1: return self._extend_axis_(Axis=full_y_axis, sign="Plus")

            case -1: return self._extend_axis_(Axis=full_y_axis, sign="Plus")

    def _add_bottom_axis_symmetry_(self, full_y_axis, symmetries):
        match symmetries['bottom']:
            case 0: return full_y_axis

            case 1: return self._extend_axis_(Axis=full_y_axis, sign="Minus")

            case -1: return self._extend_axis_(Axis=full_y_axis, sign="Minus")

import numpy
import logging
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
        xAxis = numpy.linspace(*self.x_bound, self.n_x)
        yAxis = numpy.linspace(*self.y_bound, self.n_y)

        self._FullxAxis = None
        self._FullyAxis = None

        self.x = Namespace(N=self.n_x,
                           Bounds=self.x_bound,
                           Vector=xAxis,
                           d=numpy.abs(xAxis[0] - xAxis[1]))

        self.y = Namespace(N=self.n_y,
                           Bounds=self.y_bound,
                           Vector=yAxis,
                           d=numpy.abs(yAxis[0] - yAxis[1]))

        self.x.Mesh, self.y.Mesh = numpy.mgrid[self.x_bound[0]:self.x_bound[1]: complex(self.n_x),
                                               self.y_bound[0]:self.y_bound[1]: complex(self.n_y)]

        self.rho = numpy.sqrt(self.x.Mesh**2 + self.y.Mesh**2)

        self.dA = self.x.d * self.y.d

        self.Shape = numpy.array([self.n_x, self.n_y])

    @property
    def FullxAxis(self):
        if self._FullxAxis is None:
            self._FullxAxis, self._FullyAxis = self.GetFullAxis()
        return self._FullxAxis

    @property
    def FullyAxis(self):
        if self._FullyAxis is None:
            self._FullxAxis, self._FullyAxis = self.GetFullAxis()
        return self._FullyAxis

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

    def GetFullAxis(self, symmetries: dict = None):
        if symmetries is None:
            symmetries = self.symmetries

        FullxAxis = self.x.Vector
        FullyAxis = self.y.Vector

        FullxAxis = self._add_right_axis_symmetry_(FullxAxis, symmetries=symmetries)

        FullxAxis = self._add_left_axis_symmetry_(FullxAxis, symmetries=symmetries)

        FullyAxis = self._add_top_axis_symmetry_(FullyAxis, symmetries=symmetries)

        FullyAxis = self._add_bottom_axis_symmetry_(FullyAxis, symmetries=symmetries)

        return FullxAxis, FullyAxis

    def _add_right_axis_symmetry_(self, FullxAxis, symmetries):
        match symmetries['right']:
            case 0: return FullxAxis

            case 1: return self._extend_axis_(Axis=FullxAxis, sign="Minus")

            case -1: return self._extend_axis_(Axis=FullxAxis, sign="Minus")

    def _add_left_axis_symmetry_(self, FullxAxis, symmetries):
        match symmetries['left']:
            case 0: return FullxAxis

            case 1: return self._extend_axis_(Axis=FullxAxis, sign="Plus")

            case -1: return self._extend_axis_(Axis=FullxAxis, sign="Plus")

    def _add_top_axis_symmetry_(self, FullyAxis, symmetries):
        match symmetries['top']:
            case 0: return FullyAxis

            case 1: return self._extend_axis_(Axis=FullyAxis, sign="Plus")

            case -1: return self._extend_axis_(Axis=FullyAxis, sign="Plus")

    def _add_bottom_axis_symmetry_(self, FullyAxis, symmetries):
        match symmetries['bottom']:
            case 0: return FullyAxis

            case 1: return self._extend_axis_(Axis=FullyAxis, sign="Minus")

            case -1: return self._extend_axis_(Axis=FullyAxis, sign="Minus")

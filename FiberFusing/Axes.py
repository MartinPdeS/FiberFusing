import numpy
from dataclasses import dataclass


class Namespace:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@dataclass
class Axes(object):
    n_x: int
    n_y: int
    x_bound: float
    y_bound: float

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


# -

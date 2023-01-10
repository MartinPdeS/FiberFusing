import numpy

import FiberFusing._buffer as _buffer


class FiberRing():
    def __init__(self, angle_list, fusion_degree, fiber_radius):
        self.fiber_radius = fiber_radius
        self.fusion_degree = fusion_degree
        self.angle_list = angle_list
        self.NFiber = len(angle_list)

        self._Fibers = None
        self._CoreShift = None
        self._centers = None
        self._MaxDistance = None

    @property
    def MaxDistance(self):
        if self._MaxDistance is None:
            self.ComputeMaxDistance()
        return self._MaxDistance

    @property
    def Fibers(self):
        if self._Fibers is None:
            self.ComputeFibers()
        return self._Fibers

    @property
    def centers(self):
        if self._centers is None:
            self.Computecenters()
        return self._centers

    @property
    def CoreShift(self):
        if self._CoreShift is None:
            self.ComputeCoreShift()
        return self._CoreShift

    def ComputeFibers(self):
        self._Fibers = []

        for n, point in enumerate(self.centers):
            fiber = _buffer.CircleComposition(radius=self.fiber_radius, position=point, name=f' Fiber {n}')
            self._Fibers.append(fiber)

    def ComputeCoreShift(self):
        if self.NFiber == 1:
            self._CoreShift = 0
            return

        else:
            alpha = (2 - self.NFiber) * numpy.pi / (2 * self.NFiber)

            self._CoreShift = (1 + numpy.cos(alpha)) - numpy.sqrt(self.NFiber) * numpy.cos(alpha)

            self._CoreShift = (self.fiber_radius - (self._CoreShift * self.fiber_radius) * self.fusion_degree)

            self._CoreShift *= 1 / (numpy.cos(alpha))

    def Computecenters(self):
        self._centers = [_buffer.PointComposition(position=[0, self.CoreShift]).rotate(angle=angle, origin=[0, 0]) for angle in self.angle_list ]

    def ComputeMaxDistance(self):
        x, y = self.Fibers[0].exterior.xy
        x = numpy.asarray(x)
        y = numpy.asarray(y)

        self._MaxDistance = numpy.sqrt(x**2 + y**2).max()

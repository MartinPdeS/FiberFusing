import numpy, logging
from dataclasses import dataclass, field
from collections import defaultdict



class Namespace:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)



@dataclass
class Axes(object):
    Nx: int
    Ny: int
    XBound: float
    YBound: float
    Symmetries: defaultdict[dict] = field(default_factory=lambda: {'Left': 0, 'Right': 0, 'Top': 0, 'Bottom': 0})
    
    def __post_init__(self):

        xAxis = numpy.linspace(*self.XBound, self.Nx)
        yAxis = numpy.linspace(*self.YBound, self.Ny)

        self._FullxAxis = None
        self._FullyAxis = None


        self.x = Namespace(N      = self.Nx,
                           Bounds = self.XBound,
                           Vector = xAxis,
                           d      = numpy.abs( xAxis[0] - xAxis[1] ))

        self.y = Namespace(N      = self.Ny,
                           Bounds = self.YBound,
                           Vector = yAxis,
                           d      = numpy.abs( yAxis[0] - yAxis[1] ))

        self.x.Mesh, self.y.Mesh = numpy.mgrid[self.XBound[0]:self.XBound[1]: complex(self.Nx),
                                               self.YBound[0]:self.YBound[1]: complex(self.Ny)]

        self.rho = numpy.sqrt(self.x.Mesh**2 + self.y.Mesh**2)

        self.dA  = self.x.d * self.y.d

        self.Shape = numpy.array([self.Nx, self.Ny])




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


    def ExtendAxis(self, Axis: numpy.ndarray, sign: str):
        d = Axis[1] - Axis[0]

        if sign == "Plus":
            start = Axis[-1] + d
            Next  = numpy.arange(0, Axis.size) * d + start
            Next  = [Axis, Next]

        if sign == "Minus":
            stop = Axis[0]
            Next  = numpy.arange(-Axis.size, 0) * d + stop
            Next  = [Next, Axis]

        return numpy.concatenate(Next)


    def GetFullAxis(self, Symmetries: dict=None):
        if Symmetries is None:
            Symmetries = self.Symmetries

        FullxAxis = self.x.Vector
        FullyAxis = self.y.Vector

        FullxAxis = self.AddRightAxisSymmetry(FullxAxis, Symmetries=Symmetries)

        FullxAxis = self.AddLeftAxisSymmetry(FullxAxis, Symmetries=Symmetries)

        FullyAxis = self.AddTopAxisSymmetry(FullyAxis, Symmetries=Symmetries)

        FullyAxis = self.AddBottomAxisSymmetry(FullyAxis, Symmetries=Symmetries)

        return FullxAxis, FullyAxis


    def AddRightAxisSymmetry(self, FullxAxis, Symmetries):
        match Symmetries['Right']:
            case 0: return FullxAxis

            case 1: return self.ExtendAxis(Axis=FullxAxis, sign="Minus")

            case -1: return self.ExtendAxis(Axis=FullxAxis, sign="Minus")


    def AddLeftAxisSymmetry(self, FullxAxis, Symmetries):
        match Symmetries['Left']:
            case 0: return FullxAxis

            case 1: return self.ExtendAxis(Axis=FullxAxis, sign="Plus")

            case -1: return self.ExtendAxis(Axis=FullxAxis, sign="Plus")


    def AddTopAxisSymmetry(self, FullyAxis, Symmetries):
        match Symmetries['Top']:
            case 0: return FullyAxis

            case 1: return self.ExtendAxis(Axis=FullyAxis, sign="Plus")

            case -1: return self.ExtendAxis(Axis=FullyAxis, sign="Plus")


    def AddBottomAxisSymmetry(self, FullyAxis, Symmetries):
        match Symmetries['Bottom']:
            case 0: return FullyAxis

            case 1: return self.ExtendAxis(Axis=FullyAxis, sign="Minus")

            case -1: return self.ExtendAxis(Axis=FullyAxis, sign="Minus")

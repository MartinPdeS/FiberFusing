
import logging, numpy, cv2
from dataclasses import dataclass

import MPSPlots.Plots as Plots 
import FiberFusing.Utils as Utils
from FiberFusing.Axes import Axes


@dataclass
class Geometry(object):
    """ Class represent the refractive index (RI) geometrique profile which
    can be used to retrieve the supermodes.

    Parameters
    ----------
    Objects:
        Geometrique object representing the element of the RI profile.
    Xbound: 
        X-dimension boundary for the rasterized profile.
    Ybound: 
        Y-dimension boundary for the rasterized profile.
    Nx: 
        Number of point for X dimensions discretization.
    Ny: 
        Number of point for Y dimensions discretization.
    """

    Objects: list
    Xbound: list
    Ybound: list
    Nx: int = 100
    Ny: int = 10
    GConv: float = 0
    IndexScrambling: float = 0
    ResizeFactor: int = 5

    def __post_init__(self):
        self._Mesh = None
        self._Gradient = None
        self.Axes  = Axes( XBound=self.Xbound, YBound=self.Ybound,  Nx=self.Nx, Ny=self.Ny )
        self.UpScaleAxes = Axes( XBound=self.Xbound, YBound=self.Ybound,  Nx=self.Nx*self.ResizeFactor, Ny=self.Ny*self.ResizeFactor )
        self.GetIndices()

    def GetGradient(self, Mesh: numpy.ndarray, Axes: Axes) -> numpy.ndarray:
        Xgrad, Ygrad = Utils.gradientO4( Mesh**2, Axes.x.d, Axes.y.d )

        gradient = (Xgrad * Axes.x.Mesh + Ygrad * Axes.y.Mesh)

        return gradient


    def GetFullMesh(self, LeftSymmetry, RightSymmetry, TopSymmetry, BottomSymmetry):

        FullMesh = self.Mesh

        if BottomSymmetry in [1,-1]:
            FullMesh = numpy.concatenate((FullMesh[::-1, :], FullMesh), axis=1)


        if TopSymmetry in [1, -1]:
            FullMesh = numpy.concatenate((FullMesh, FullMesh[::-1, :]), axis=1)


        if RightSymmetry in [1, -1]:
            FullMesh = numpy.concatenate((FullMesh, FullMesh[::-1, :]), axis=0)


        if LeftSymmetry in [1, -1]:
            FullMesh = numpy.concatenate((FullMesh[::-1, :], FullMesh), axis=0)


        return FullMesh


    @property
    def Mesh(self):
        if self._Mesh is None:
            self._Mesh, _, self._Gradient, _ = self.GenerateMesh()
        return self._Mesh

    @property
    def Gradient(self):
        if self._Gradient is None:
            self._Mesh, _, self._Gradient, _ = self.GenerateMesh()
        return self._Gradient


    @property
    def AllObjects(self) -> list:
        return [*self.Objects]

    @property
    def MaxIndex(self) -> float:
        ObjectList = self.Objects
        return max( [obj.Index for obj in ObjectList] )[0]

    @property
    def MinIndex(self) -> float:
        ObjectList = self.Objects
        return min( [obj.Index for obj in ObjectList] )[0]

    @property
    def xMax(self) -> float:
        return self.Axes.x.Bounds[0]

    @property
    def xMin(self) -> float:
        return self.Axes.x.Bounds[1]

    @property
    def yMax(self) -> float:
        return self.Axes.y.Bounds[0]

    @property
    def yMin(self) -> list:
        return self.Axes.y.Bounds[1]

    @property
    def Shape(self) -> list:
        return numpy.array( [self.Axes.x.N, self.Axes.y.N] )


    def GetIndices(self) -> None:
        self.Indices = []
        for obj in self.Objects:
            self.Indices.append(float(obj.Index))


    def Rotate(self, Angle: float) -> None:
        for obj in self.Objects:
            obj = obj.Rotate(Angle=Angle)


    def GenerateMesh(self) -> numpy.ndarray:
        UpScaleMesh = numpy.zeros(self.UpScaleAxes.Shape)

        self.coords = numpy.vstack( (self.UpScaleAxes.x.Mesh.flatten(), self.UpScaleAxes.y.Mesh.flatten()) ).T

        for polygone in self.Objects:
            polygone.Rasterize(Coordinate=self.coords, Shape=self.UpScaleAxes.Shape)
            UpScaleMesh[numpy.where(polygone.Raster > 0)] = 0
            UpScaleMesh += polygone.Raster * polygone.Index + numpy.random.rand(1)*self.IndexScrambling

        
        RescaledMesh = cv2.resize(UpScaleMesh, dsize=self.Axes.Shape, interpolation=cv2.INTER_AREA)

        RawGradient = self.GetGradient(Mesh=UpScaleMesh, Axes=self.UpScaleAxes)

        RescaledGradient = cv2.resize(RawGradient, dsize=self.Axes.Shape, interpolation=cv2.INTER_AREA)

        return RescaledMesh, UpScaleMesh, RescaledGradient, RawGradient


    def Plot(self) -> None:
        """ Method plot the rasterized RI profile."""

        Figure = Plots.Scene(UnitSize=(6,6))
        Colorbar0 = Plots.ColorBar(Discreet=True, Position='right', Format='%.4f')
        Colorbar1 = Plots.ColorBar(LogNorm=True, Position='right', Format='%.4f')

        ax0 = Plots.Axis(Row = 0, 
                         Col = 0, 
                         xLabel = r'x [$\mu m$]', 
                         yLabel = r'y [$\mu m$]', 
                         Title = f'Refractive index structure', 
                         Legend = False, Colorbar = Colorbar0)

        ax1 = Plots.Axis(Row = 0, 
                         Col = 1, 
                         xLabel = r'x [$\mu m$]', 
                         yLabel = r'y [$\mu m$]', 
                         Title = f'Refractive index gradient', 
                         Legend = False, Colorbar = Colorbar1)

        artist = Plots.Mesh(X=self.Axes.x.Vector, Y=self.Axes.y.Vector, Scalar=self.Mesh, ColorMap='Blues')

        gradient = Plots.Mesh(X=self.Axes.x.Vector, Y=self.Axes.y.Vector, Scalar=self.Gradient, ColorMap='seismic')

        ax0.AddArtist(artist)
        ax1.AddArtist(gradient)

        Figure.AddAxes(ax0, ax1)

        return Figure





















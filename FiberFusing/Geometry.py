
import logging
import numpy
from dataclasses import dataclass
from PIL import Image
import MPSPlots.CMAP
from MPSPlots.Render2D import Scene2D, ColorBar, Axis, Mesh
import FiberFusing.Utils as Utils
from FiberFusing.Axes import Axes


@dataclass
class Geometry(object):
    """ Class represent the refractive index (RI) geometrique profile which
    can be used to retrieve the supermodes.
    """

    Clad: object
    """ Geometrique object representing the fiber structure clad. """
    BackGround: object
    """ Geometrique object representing the background (usually air). """
    Cores: list
    """ List of geometrique object representing the fiber structure cores. """
    Xbound: list
    """ X boundary to render the structure [float, float, 'auto', 'auto right', 'auto left']. """
    Ybound: list
    """ Y boundary to render the structure [float, float, 'auto', 'auto top', 'auto bottom']. """
    Nx: int = 100
    """ Number of point (x-direction) to evaluate the rendering """
    Ny: int = 100
    """ Number of point (y-direction) to evaluate the rendering """
    IndexScrambling: float = 0
    """ Index scrambling for degeneracy lifting """
    ResizeFactor: int = 5
    """ Oversampling factor for gradient evaluation """

    def __post_init__(self):
        self.Objects = [self.BackGround, *self.Cores, self.Clad]
        self._Mesh = None
        self._Gradient = None

        minx, miny, maxx, maxy = self.Clad.Object.bounds

        if isinstance(self.Xbound, str):
            self._parse_Xbound_()

        if isinstance(self.Ybound, str):
            self._parse_Ybound_()

        self.Axes = Axes(XBound=self.Xbound, YBound=self.Ybound, Nx=self.Nx, Ny=self.Ny)
        self.UpScaleAxes = Axes(XBound=self.Xbound, YBound=self.Ybound, Nx=self.Nx * self.ResizeFactor, Ny=self.Ny * self.ResizeFactor)
        self.GetIndices()

    def _parse_Xbound_(self):
        minx, miny, maxx, maxy = self.Clad.Object.bounds
        string_Xbound = self.Xbound.lower()

        if 'auto' in string_Xbound:
            minx, miny, maxx, maxy = self.Clad.Object.bounds
            self.Xbound = numpy.array([minx, maxx]) * 1.3

        if 'right' in string_Xbound:
            self.Xbound[0] = 0

        if 'left' in string_Xbound:
            self.Xbound[1] = 0

    def _parse_Ybound_(self):
        minx, miny, maxx, maxy = self.Clad.Object.bounds
        string_Ybound = self.Ybound.lower()

        if 'auto' in string_Ybound:
            minx, miny, maxx, maxy = self.Clad.Object.bounds
            self.Ybound = numpy.array([minx, maxx]) * 1.3

        if 'top' in string_Ybound:
            self.Ybound[0] = 0

        if 'bottom' in string_Ybound:
            self.Ybound[1] = 0

    def GetGradient(self, Mesh: numpy.ndarray, Axes: Axes) -> numpy.ndarray:
        Xgrad, Ygrad = Utils.gradientO4(Mesh**2, Axes.x.d, Axes.y.d)

        gradient = (Xgrad * Axes.x.Mesh + Ygrad * Axes.y.Mesh)

        return gradient

    def GetFullMesh(self, LeftSymmetry, RightSymmetry, TopSymmetry, BottomSymmetry):

        FullMesh = self.Mesh

        if BottomSymmetry in [1, -1]:
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
        return numpy.array([self.Axes.x.N, self.Axes.y.N])

    def GetIndices(self) -> None:
        self.Indices = []
        for obj in self.Objects:
            self.Indices.append(float(obj.Index))

    def Rotate(self, Angle: float) -> None:
        for obj in self.Objects:
            obj = obj.Rotate(Angle=Angle)

    def DownscaleImage(self, Array, Size) -> numpy.ndarray:
        image = Image.fromarray(Array)

        return numpy.asarray(image.resize(Size, resample=Image.Resampling.BOX))

    def GenerateMesh(self) -> numpy.ndarray:
        UpScaleMesh = numpy.zeros(self.UpScaleAxes.Shape)

        self.coords = numpy.vstack((self.UpScaleAxes.x.Mesh.flatten(), self.UpScaleAxes.y.Mesh.flatten())).T

        for polygone in self.Objects:
            polygone.Rasterize(Coordinate=self.coords, Shape=self.UpScaleAxes.Shape)
            UpScaleMesh[numpy.where(polygone.Raster > 0)] = 0
            UpScaleMesh += polygone.Raster * polygone.Index + numpy.random.rand(1) * self.IndexScrambling

        Mesh = self.DownscaleImage(Array=UpScaleMesh, Size=self.Axes.Shape)

        UpscaleGradient = self.GetGradient(Mesh=UpScaleMesh, Axes=self.UpScaleAxes)

        Gradient = self.DownscaleImage(Array=UpscaleGradient, Size=self.Axes.Shape)

        return Mesh, UpScaleMesh, Gradient, UpscaleGradient

    def Plot(self) -> None:
        """
        Method plot the rasterized RI profile.
        """

        Figure = Scene2D(UnitSize=(6, 6))
        Colorbar0 = ColorBar(Discreet=True, Position='right', Format='%.4f')
        Colorbar1 = ColorBar(LogNorm=True, Position='right', Format='%.4f', Symmetric=True)

        ax0 = Axis(Row=0,
                   Col=0,
                   xLabel=r'x [$\mu m$]',
                   yLabel=r'y [$\mu m$]',
                   Title='Refractive index structure',
                   Legend=False,
                   Colorbar=Colorbar0)

        ax1 = Axis(Row=0,
                   Col=1,
                   xLabel=r'x [$\mu m$]',
                   yLabel=r'y [$\mu m$]',
                   Title='Refractive index gradient',
                   Legend=False,
                   Colorbar=Colorbar1)

        artist = Mesh(X=self.Axes.x.Vector, Y=self.Axes.y.Vector, Scalar=self.Mesh, ColorMap='Blues')

        gradient = Mesh(X=self.Axes.x.Vector, Y=self.Axes.y.Vector, Scalar=self.Gradient, ColorMap=MPSPlots.CMAP.BWR)

        ax0.AddArtist(artist)
        ax1.AddArtist(gradient)

        Figure.AddAxes(ax0, ax1)

        return Figure

# -

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

    clad: object
    """ Geometrique object representing the fiber structure clad. """
    background: object
    """ Geometrique object representing the background (usually air). """
    cores: list
    """ List of geometrique object representing the fiber structure cores. """
    x_bound: list
    """ X boundary to render the structure [float, float, 'auto', 'auto right', 'auto left']. """
    y_bound: list
    """ Y boundary to render the structure [float, float, 'auto', 'auto top', 'auto bottom']. """
    n_x: int = 100
    """ Number of point (x-direction) to evaluate the rendering """
    n_y: int = 100
    """ Number of point (y-direction) to evaluate the rendering """
    index_scrambling: float = 0
    """ Index scrambling for degeneracy lifting """
    resize_factor: int = 5
    """ Oversampling factor for gradient evaluation """

    def __post_init__(self):
        self.Objects = [self.background, self.clad, *self.cores]
        self._Mesh = None
        self._Gradient = None

        minx, miny, maxx, maxy = self.clad.Object.bounds

        if isinstance(self.x_bound, str):
            self._parse_x_bound_()

        if isinstance(self.y_bound, str):
            self._parse_y_bound_()

        self.Axes = Axes(x_bound=self.x_bound, y_bound=self.y_bound, n_x=self.n_x, n_y=self.n_y)
        self.UpScaleAxes = Axes(x_bound=self.x_bound, y_bound=self.y_bound, n_x=self.n_x * self.resize_factor, n_y=self.n_y * self.resize_factor)
        self.GetIndices()

    def _parse_x_bound_(self):
        minx, miny, maxx, maxy = self.clad.Object.bounds
        string_x_bound = self.x_bound.lower()

        if 'auto' in string_x_bound:
            minx, miny, maxx, maxy = self.clad.Object.bounds
            self.x_bound = numpy.array([minx, maxx]) * 1.3

        if 'right' in string_x_bound:
            self.x_bound[0] = 0

        if 'left' in string_x_bound:
            self.x_bound[1] = 0

    def _parse_y_bound_(self):
        minx, miny, maxx, maxy = self.clad.Object.bounds
        string_y_bound = self.y_bound.lower()

        if 'auto' in string_y_bound:
            minx, miny, maxx, maxy = self.clad.Object.bounds
            self.y_bound = numpy.array([miny, maxy]) * 1.3

        if 'top' in string_y_bound:
            self.y_bound[0] = 0

        if 'bottom' in string_y_bound:
            self.y_bound[1] = 0

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
        return min([obj.Index for obj in ObjectList])[0]

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
            UpScaleMesh += polygone.Raster * polygone.Index + numpy.random.rand(1) * self.index_scrambling

        Mesh = self.DownscaleImage(Array=UpScaleMesh, Size=self.Axes.Shape)

        UpscaleGradient = self.GetGradient(Mesh=UpScaleMesh, Axes=self.UpScaleAxes)

        Gradient = self.DownscaleImage(Array=UpscaleGradient, Size=self.Axes.Shape)

        return Mesh, UpScaleMesh, Gradient, UpscaleGradient

    def Plot(self) -> None:
        """
        Method plot the rasterized RI profile.
        """
        Figure = Scene2D(unit_size=(6, 6), tight_layout=True)
        colorbar0 = ColorBar(discreet=True, position='right', numeric_format='%.4f')
        colorbar1 = ColorBar(log_norm=True, position='right', numeric_format='%.1e', symmetric=True)

        ax0 = Axis(row=0,
                   col=0,
                   x_label=r'x [$\mu m$]',
                   y_label=r'y [$\mu m$]',
                   title='Refractive index structure',
                   show_legend=False,
                   colorbar=colorbar0)

        ax1 = Axis(row=0,
                   col=1,
                   x_label=r'x [$\mu m$]',
                   y_label=r'y [$\mu m$]',
                   title='Refractive index gradient',
                   show_legend=False,
                   colorbar=colorbar1)

        artist = Mesh(x=self.Axes.x.Vector, y=self.Axes.y.Vector, scalar=self.Mesh, colormap='Blues')

        gradient = Mesh(x=self.Axes.x.Vector, y=self.Axes.y.Vector, scalar=self.Gradient, colormap=MPSPlots.CMAP.BWR)

        ax0.AddArtist(artist)
        ax1.AddArtist(gradient)

        Figure.AddAxes(ax0, ax1)

        return Figure

# -
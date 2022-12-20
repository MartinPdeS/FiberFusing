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
        self.compute_index_range()

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

    def get_gradient_mesh(self, Mesh: numpy.ndarray, Axes: Axes) -> numpy.ndarray:
        Xgrad, Ygrad = Utils.gradientO4(Mesh**2, Axes.x.d, Axes.y.d)

        gradient = (Xgrad * Axes.x.Mesh + Ygrad * Axes.y.Mesh)

        return gradient

    def get_full_mesh(self, left_symmetry: int, right_symmetry: int, top_symmetry: int, bottom_symmetry: int) -> numpy.ndarray:
        full_mesh = self.Mesh

        if bottom_symmetry in [1, -1]:
            full_mesh = numpy.concatenate((full_mesh[::-1, :], full_mesh), axis=1)

        if top_symmetry in [1, -1]:
            full_mesh = numpy.concatenate((full_mesh, full_mesh[::-1, :]), axis=1)

        if right_symmetry in [1, -1]:
            full_mesh = numpy.concatenate((full_mesh, full_mesh[::-1, :]), axis=0)

        if left_symmetry in [1, -1]:
            full_mesh = numpy.concatenate((full_mesh[::-1, :], full_mesh), axis=0)

        return full_mesh

    @property
    def Mesh(self) -> numpy.ndarray:
        if self._Mesh is None:
            self._Mesh, _, self._Gradient, _ = self.generate_mesh()
        return self._Mesh

    @property
    def Gradient(self) -> numpy.ndarray:
        if self._Gradient is None:
            self._Mesh, _, self._Gradient, _ = self.generate_mesh()
        return self._Gradient

    @property
    def max_index(self) -> float:
        ObjectList = self.Objects
        return max([obj.index for obj in ObjectList])[0]

    @property
    def min_index(self) -> float:
        ObjectList = self.Objects
        return min([obj.index for obj in ObjectList])[0]

    @property
    def max_x(self) -> float:
        return self.Axes.x.Bounds[0]

    @property
    def min_x(self) -> float:
        return self.Axes.x.Bounds[1]

    @property
    def max_y(self) -> float:
        return self.Axes.y.Bounds[0]

    @property
    def min_y(self) -> list:
        return self.Axes.y.Bounds[1]

    @property
    def Shape(self) -> list:
        return numpy.array([self.Axes.x.N, self.Axes.y.N])

    def compute_index_range(self) -> None:
        self.Indices = []

        for obj in self.Objects:
            self.Indices.append(float(obj.index))

    def Rotate(self, angle: float) -> None:
        for obj in self.Objects:
            obj = obj.rotate(angle=angle)

    def get_downscale_array(self, array, size) -> numpy.ndarray:
        array = Image.fromarray(array)

        return numpy.asarray(array.resize(size, resample=Image.Resampling.BOX))

    def generate_mesh(self) -> numpy.ndarray:
        UpScaleMesh = numpy.zeros([self.UpScaleAxes.y.n, self.UpScaleAxes.x.n])

        self.coords = numpy.vstack((self.UpScaleAxes.x.Mesh.flatten(), self.UpScaleAxes.y.Mesh.flatten())).T

        for polygone in self.Objects:
            raster = polygone.get_rasterized_mesh(coordinate=self.coords, n_x=self.UpScaleAxes.x.n, n_y=self.UpScaleAxes.y.n).astype(numpy.float64)

            rand = (numpy.random.rand(1) - 0.5) * self.index_scrambling

            raster *= polygone.index + rand

            UpScaleMesh[numpy.where(raster != 0)] = 0

            UpScaleMesh += raster

        Mesh = self.get_downscale_array(array=UpScaleMesh, size=self.Axes.Shape)

        UpscaleGradient = self.get_gradient_mesh(Mesh=UpScaleMesh, Axes=self.UpScaleAxes)

        Gradient = self.get_downscale_array(array=UpscaleGradient, size=self.Axes.Shape)

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
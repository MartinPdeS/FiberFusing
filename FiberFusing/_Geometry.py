
import os, logging, numpy
from dataclasses import dataclass
from typing import Union

from matplotlib.path             import Path
from shapely                     import affinity
from scipy.ndimage.filters       import gaussian_filter
from shapely.geometry            import box

from SuPyMode.Tools.Special      import gradientO4
from SuPyMode.Tools.utils        import ToList, Axes
from SuPyMode.Plotting.Plots     import Scene, Axis, Mesh, Contour, ColorBar
from SuPyMode.Geometry.Utils     import Rotate


from SuPyMode.Geometry.Utils     import BufferPolygon
from SuPyMode.Geometry.Fused2    import Fused2
from SuPyMode.Geometry.Fused3    import Fused3
from SuPyMode.Geometry.Fused4    import Fused4
from SuPyMode.Geometry.BaseClass import Circle, BackGround


class Gradient:
    def __init__(self, Center, Nin, Nout, Rout):
        if Nin == Nout:
            Nin = Nout + 1e-9
        self.Nin    = Nin
        self.Nout   = Nout
        self.Rout   = Rout
        if isinstance(Center, Point):
            Center = Center.xy
        self.Center = Center

    def Evaluate(self, Xmesh, Ymesh):
        A = -(self.Rout * self.Nout) / (self.Nin-self.Nout)
        B = - A * self.Nin
        rho = numpy.hypot( Xmesh-self.Center[0], Ymesh-self.Center[1] )
        return B/(rho-A)

class Namespace:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@dataclass
class Geometry(object):
    """ Class represent the refractive index (RI) geometrique profile which
    can be used to retrieve the supermodes.

    Parameters
    ----------
    Objects : type
        Geometrique object representing the element of the RI profile.
    Xbound : :class:`list`
        X-dimension boundary for the rasterized profile.
    Ybound : :class:`list`
        Y-dimension boundary for the rasterized profile.
    Nx : :class:`int`
        Number of point for X dimensions discretization.
    Ny : :class:`int`
        Number of point for Y dimensions discretization.
    """

    Clad: object
    Objects: list
    Xbound: list
    Ybound: list
    Nx: int = 100
    Ny: int = 10
    GConv: float = 0
    BackGroundIndex: float = 1.

    def __post_init__(self):
        self.Objects    = ToList(self.Objects)
        self.Boundaries = [self.Xbound, self.Ybound]
        self.Shape      = [self.Nx, self.Ny]

        self.Axes  = Axes( {'Xbound'    : self.Xbound,
                            'Ybound'    : self.Ybound,
                            'Nx'        : self.Nx,
                            'Ny'        : self.Ny } )

        self.BackGround = BackGround(Radius=1000, Index=1) 
        self.GetAllIndex()


    def GetFullMesh(self, LeftSymmetry, RightSymmetry, TopSymmetry, BottomSymmetry):

        FullMesh = self._Mesh

        if BottomSymmetry in [1,-1]:
            FullMesh = numpy.concatenate((FullMesh[::-1, :], FullMesh), axis=1)


        if TopSymmetry in [1, -1]:
            FullMesh = numpy.concatenate((FullMesh, FullMesh[::-1, :]), axis=1)


        if RightSymmetry in [1, -1]:
            FullMesh = numpy.concatenate((FullMesh[...], FullMesh[::-1, :]), axis=0)


        if LeftSymmetry in [1, -1]:
            FullMesh = numpy.concatenate((FullMesh[::-1, :], FullMesh[...]), axis=0)


        return FullMesh


    @property
    def Mesh(self):
        if self._Mesh is None:
            self.CreateMesh()
        return self._Mesh

    @property
    def AllObjects(self):
        return [self.BackGround, self.Clad, *self.Objects]

    @property
    def MaxIndex(self):
        ObjectList = [self.Clad] + self.Objects
        return max( [obj.Index for obj in ObjectList] )[0]

    @property
    def MinIndex(self):
        ObjectList = [self.Clad] + self.Objects
        return min( [obj.Index for obj in ObjectList] )[0]

    @property
    def xMax(self):
        return self.Boundaries[0][1]

    @property
    def xMin(self):
        return self.Boundaries[0][0]

    @property
    def yMax(self):
        return self.Boundaries[1][1]

    @property
    def yMin(self):
        return self.Boundaries[1][0]


    def GetAllIndex(self,):
        self.AllIndex = []
        for obj in self.AllObjects:
            self.AllIndex.append(float(obj.Index))



    def Rotate(self, Angle):
        for object in self.AllObjects:
            object = affinity.rotate(object.Object, Angle, (0,0))


    def AddToMesh(self, polygone):
        self._Mesh[numpy.where(polygone.Raster > 0)] = 0
        self._Mesh += polygone.Raster * polygone.Index


    def CreateMesh(self):
        self._Mesh = numpy.zeros(self.Shape)

        self.X, self.Y = numpy.mgrid[self.xMin: self.xMax: complex(self.Shape[0]),
                                     self.yMin: self.yMax: complex(self.Shape[1]) ]

        self.coords = numpy.vstack((self.X.flatten(), self.Y.flatten())).T

        for o in [self.BackGround, self.Clad, *self.Objects]:
            o.Rasterize(Coordinate=self.coords, Shape=self.Shape)
            self.AddToMesh(o)

        self._Mesh = gaussian_filter(self._Mesh, sigma=self.GConv)


    def Plot(self, ReturnFig: bool=False):
        """ The methode plot the rasterized RI profile.

        """

        self.CreateMesh()

        Fig = Scene('SuPyMode Figure', UnitSize=(6,6))
        Colorbar = ColorBar(Discreet=True, Position='right')

        ax = Axis(Row              = 0,
                  Col              = 0,
                  xLabel           = r'x [$\mu m$]',
                  yLabel           = r'y [$\mu m$]',
                  Title            = f'Refractive index structure',
                  Legend           = False,
                  Grid             = False,
                  Equal            = True,
                  Colorbar         = Colorbar,
                  xScale           = 'linear',
                  yScale           = 'linear')

        artist = Mesh(X           = self.X,
                      Y           = self.Y,
                      Scalar      = self._Mesh,
                      ColorMap    = 'Blues',
                      )

        ax.AddArtist(artist)

        Fig.AddAxes(ax)

        if ReturnFig:
            Fig.Render()
            return Fig.Figure

        Fig.Show()




    def _Gradient(self):

        Ygrad, Xgrad = gradientO4( self._Mesh.T**2, self.Axes.dx, self.Axes.dy )

        return Ygrad, Xgrad


    def Gradient(self, Plot=False):

        #blurred = gaussian_filter(self.mesh, sigma=0)

        Ygrad, Xgrad = gradientO4( self._Mesh.T**2, self.Axes.dx, self.Axes.dy )

        gradient = (Xgrad * self.Axes.XX + Ygrad * self.Axes.YY)

        return gradient.T






















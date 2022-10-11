#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy
from shapely.geometry        import Point, LineString, MultiPolygon, Polygon, GeometryCollection
import matplotlib.pyplot     as plt
import matplotlib.cm         as cm
from matplotlib              import colors
from matplotlib.path         import Path
from matplotlib.patches      import PathPatch
from matplotlib.collections  import PatchCollection
from mpl_toolkits.axes_grid1 import make_axes_locatable

from dataclasses import dataclass


import matplotlib
matplotlib.style.use('ggplot')


@dataclass
class ColorBar:
    Color: str = 'viridis'
    Discreet: bool = False
    Position: str = 'left'
    Orientation: str = "vertical"
    Symmetric: bool = False
    Format: str = ':.3f'
    LogNorm: bool = False

    def Render(self, Ax, Scalar, Image):
        divider = make_axes_locatable(Ax._ax)
        cax = divider.append_axes(self.Position, size="10%", pad=0.15)

        if self.Discreet:
            Values = numpy.unique(Scalar)
            Norm = colors.BoundaryNorm(Values, Values.size+1, extend='both')
            Norm.autoscale(Scalar)
            Image.set_norm(Norm)
            ticks = numpy.unique(Scalar)
            plt.colorbar(mappable=Image, norm=Norm, boundaries=ticks, cax=cax, orientation=self.Orientation)
            return

        if self.Symmetric:
            Norm = colors.CenteredNorm()
            Norm.autoscale(Scalar)
            Image.set_norm(Norm)
            plt.colorbar(mappable=Image, norm=Norm, cax=cax, orientation=self.Orientation)
            return

        if self.LogNorm:
            Norm = matplotlib.colors.SymLogNorm(linthresh=0.03)
            Norm.autoscale(Scalar)
            Image.set_norm(Norm)
            plt.colorbar(mappable=Image, norm=Norm, cax=cax, orientation=self.Orientation)
            return
        
        plt.colorbar(mappable=Image, norm=None, cax=cax, orientation=self.Orientation)



@dataclass
class AddShapely:
    Object: list
    Text: str = ''
    facecolor: str ='lightblue'
    edgecolor: str ='red'
    Alpha: float = 0.5
    Color: str = 'lightblue'
    LineWidth: float = 2


    def Render(self, Ax, **kwargs):

        Color = self.Object.Color if 'Color' in self.Object.__dir__() else self.Color

        Text = self.Object.Name if 'Name' in self.Object.__dir__() else self.Text

        Alpha = self.Object.Alpha if 'Alpha' in self.Object.__dir__() else self.Alpha


        if isinstance(self.Object, LineString):
            Image = Ax._ax.plot(*self.Object.xy, color='k', linewidth=self.LineWidth)

        if isinstance(self.Object, Point):
            Image = Ax._ax.scatter(self.Object.x, self.Object.y, color='k', linewidth=self.LineWidth)

        if isinstance(self.Object, Polygon):
            Image = PlotPolygon(Ax._ax, self.Object, facecolor=Color, edgecolor=self.edgecolor, alpha=Alpha)
            if Text != '':
                Ax._ax.text(self.Object.centroid.x, self.Object.centroid.y, Text)
                point = Ax._ax.scatter(self.Object.centroid.x, self.Object.centroid.y, color='k')




        if isinstance(self.Object, (GeometryCollection, MultiPolygon)):
            for e in self.Object.geoms:
                artist = AddShapely(Object=e, facecolor=Color, edgecolor=self.edgecolor, Alpha=Alpha, Color=Color)
                Ax.AddArtist(artist)

        if isinstance(self.Object, list):
            for e in self.Object:
                artist = AddShapely(Object=e, facecolor=Color, edgecolor=self.edgecolor, Alpha=Alpha, Color=Color)
                Ax.AddArtist(artist)

        if self.Text is not None and isinstance(self.Object, Point):
            Ax._ax.text(self.Object.x, self.Object.y, self.Text)





@dataclass
class Contour:
    X: numpy.ndarray
    Y: numpy.ndarray
    Scalar: numpy.ndarray
    ColorMap: str = 'viridis'
    xLabel: str = ''
    yLabel: str = ''
    IsoLines: list = None

    def Render(self, Ax):
        Image = Ax.contour(self.X,
                            self.Y,
                            self.Scalar,
                            level = self.IsoLines,
                            colors="black",
                            linewidth=.5 )

        Image = Ax.contourf(self.X,
                            self.Y,
                            self.Scalar,
                            level = self.IsoLines,
                            cmap=self.ColorMap,
                            norm=colors.LogNorm() )


@dataclass
class Mesh:
    X: numpy.ndarray
    Y: numpy.ndarray
    Scalar: numpy.ndarray
    ColorMap: str = 'viridis'
    Label: str = ''

    def Render(self, Ax):

        Image = Ax._ax.pcolormesh(self.Y, self.X, self.Scalar.T, cmap=self.ColorMap, shading='auto')
        Image.set_edgecolor('face')

        if Ax.Colorbar is not None:
            Ax.Colorbar.Render(Ax=Ax, Scalar=self.Scalar, Image=Image)

        return Image


@dataclass
class Line:
    X: numpy.ndarray
    Y: numpy.ndarray
    Label: str = None
    Fill: bool = False
    Color: str = None

    def Render(self, Ax):

        Ax._ax.plot(self.X, self.Y, label=self.Label)

        if self.Fill:
            Ax._ax.fill_between(self.X, self.Y.min(), self.Y, color=self.Color, alpha=0.7)



@dataclass
class Axis:
    Row: int
    Col: int
    xLabel: str = ''
    yLabel: str = ''
    Title: str = ''
    Grid: bool = True
    Legend: bool = False
    xScale: str = 'linear'
    yScale: str = 'linear'
    xLimits: list = None
    yLimits: list = None
    Equal: bool = False
    Colorbar: ColorBar = None
    WaterMark: str = ''

    def __post_init__(self):

        self._ax = None
        self.Artist  = []

        self.Labels  = {'x': self.xLabel,
                        'y': self.yLabel,
                        'Title': self.Title}


    def AddArtist(self, *Artist):
        for art in Artist:
            self.Artist.append(art)

    def Render(self):
        for art in self.Artist:
            Image = art.Render(self)

        if self.Legend:
            self._ax.legend(fancybox=True, facecolor='white', edgecolor='k')


        self._ax.grid(self.Grid)

        if self.xLimits is not None: self._ax.set_xlim(self.xLimits)
        if self.yLimits is not None: self._ax.set_ylim(self.yLimits)

        self._ax.set_xlabel(self.Labels['x'])
        self._ax.set_ylabel(self.Labels['y'])
        self._ax.set_title(self.Labels['Title'])

        self._ax.set_xscale(self.xScale)
        self._ax.set_yscale(self.yScale)

        self._ax.text(0.5, 0.1, self.WaterMark, transform=self._ax.transAxes,
                fontsize=30, color='white', alpha=0.2,
                ha='center', va='baseline', rotation='0')

        if self.Equal:
            self._ax.set_aspect("equal")






class Scene:
    UnitSize = (10, 3)
    plt.rcParams['ytick.labelsize'] = 10
    plt.rcParams['xtick.labelsize'] = 10
    plt.rcParams["font.size"]       = 10
    plt.rcParams["font.family"]     = "serif"
    plt.rcParams['axes.edgecolor']  = 'black'
    plt.rcParams['axes.linewidth']  = 1.5
    plt.rcParams['legend.fontsize'] = 'small'

    def __init__(self, Title='', UnitSize=None):
        self.AxisGenerated = False
        self._Axis = []
        self.Title = Title
        self.nCols = 1
        self.nRows = None
        if UnitSize is not None: self.UnitSize = UnitSize


    @property
    def Axis(self):
        if not self.AxisGenerated:

            self.GenerateAxis()

        return self._Axis


    def AddAxes(self, *Axis):
        for ax in Axis:
            self._Axis.append(ax)

        return self


    def GetMaxColsRows(self):
        RowMax, ColMax = 0,0
        for ax in self._Axis:
            RowMax = ax.Row if ax.Row > RowMax else RowMax
            ColMax = ax.Col if ax.Col > ColMax else ColMax

        return RowMax, ColMax


    def GenerateAxis(self):
        RowMax, ColMax = self.GetMaxColsRows()

        FigSize = [ self.UnitSize[0]*(ColMax+1), self.UnitSize[1]*(RowMax+1) ]

        self.Figure, Ax  = plt.subplots(ncols=ColMax+1, nrows=RowMax+1, figsize=FigSize)

        if not isinstance(Ax, numpy.ndarray): Ax = numpy.asarray([[Ax]])
        if Ax.ndim == 1: Ax = numpy.asarray([Ax])

        self.Figure.suptitle(self.Title)

        for ax in self._Axis:
            ax._ax = Ax[ax.Row, ax.Col]

        self.AxisGenerated = True

        return self



    def Render(self):
        for ax in self.Axis:
            ax.Render()

        plt.tight_layout()

        return self


    def Show(self):
        self.Render()
        plt.show()



def PlotPolygon(ax, poly,  **kwargs):
    if poly.is_empty: return
    if isinstance(poly, MultiPolygon):
        for e in poly.geoms:
            PlotPolygon(ax, e, **kwargs)
        return

    path = Path.make_compound_path(
        Path(numpy.asarray(poly.exterior.coords)[:, :2]),
        *[Path(numpy.asarray(ring.coords)[:, :2]) for ring in poly.interiors])

    patch = PathPatch(path, **kwargs)
    collection = PatchCollection([patch], **kwargs)
    
    ax.add_collection(collection, autolim=True)
    ax.autoscale_view()
    if 'Name' in poly.__dict__ and poly.Name is not None:
        ax.text(poly.centroid.x, poly.centroid.y, poly.Name)
    # return collection



def PlotShapely(*Object):
        Fig = Scene('', UnitSize=(6,6))
        Colorbar = ColorBar(Discreet=True, Position='right')

        ax = Axis(Row              = 0,
                  Col              = 0,
                  xLabel           = r'x',
                  yLabel           = r'y',
                  Title            = f'Debug',
                  Legend           = False,
                  Grid             = False,
                  Equal            = True,
                  Colorbar         = None,
                  xScale           = 'linear',
                  yScale           = 'linear')


        Fig.AddAxes(ax)
        Fig.GenerateAxis()
        
        for n, obj in enumerate(Object):
            obj.Name = f" {n}"
            obj.__render__(ax)


        

        Fig.Show()


# -

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy
import FiberFusing.Buffer as Buffer
from matplotlib.path import Path
from MPSPlots.Render2D import Scene2D, Axis


class Circle(Buffer.Circle):
    Radius: float = None
    Core: Buffer.Point = None
    Center: Buffer.Point = None
    Index = None

    def __new__(cls, Radius: float, Center: tuple = (0, 0), Name: str = '', Index: float = None):
        Center = Buffer.Point(Center) if isinstance(Center, (tuple, list)) else Center
        Instance = Buffer.Circle.__new__(cls, Radius=Radius, Center=Center)
        return Instance

    @property
    def Object(self):
        return self

    def __init__(self, Radius: float, Center: tuple = (0, 0), Name: str = '', Index: float = None):
        Center = Buffer.Point(Center) if isinstance(Center, (tuple, list)) else Center
        self.Radius = Radius
        self.Name = Name
        self.Center = Center
        self.Core = Buffer.Point([Center.x, Center.y])
        self.Core.facecolor = 'k'
        self.Index = Index

        super(Circle, self).__init__(Radius=Radius, Center=Center)

    def Rasterize(self, Coordinate: numpy.ndarray, Shape: list):

        Exterior = Path(list(self.exterior.coords))

        Exterior = Exterior.contains_points(Coordinate).reshape(Shape)

        Exterior = Exterior.astype(float)

        self.Raster = Exterior

    def Plot(self, **kwargs):
        figure = Scene2D(title='SuPyMode Figure', unit_size=(6, 6))

        ax = Axis(row=0,
                  col=0,
                  x_label=r'x',
                  y_label=r'y',
                  title='Circle',
                  show_grid=True,
                  equal=True)

        figure.AddAxes(ax)

        figure._render_()

        self.__render__(ax)

        return figure

# -

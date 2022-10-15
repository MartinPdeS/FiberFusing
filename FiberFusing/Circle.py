#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy
import FiberFusing.Buffer as Buffer
import MPSPlots.Plots as Plots
from matplotlib.path import Path


class Circle(Buffer.Circle):
    Radius: float=None
    Core: Buffer.Point=None
    Center: Buffer.Point=None
    Index = None

    def __new__(cls, Radius: float, Center: list, Name: str = '', Index: float=None):
        Center = Buffer.Point(Center) if isinstance(Center, (tuple, list)) else Center
        Instance = Buffer.Circle.__new__(cls, Radius=Radius, Center=Center)
        return Instance

    def __init__(self, Radius: float, Center: list, Name: str = '', Index: float=None):
        Center = Buffer.Point(Center) if isinstance(Center, (tuple, list)) else Center
        self.Radius = Radius
        self.Name = Name
        self.Center = Center
        self.Core = Buffer.Point([Center.x, Center.y])
        self.Core.facecolor='k'
        self.Index = Index

        super(Circle, self).__init__(Radius=Radius, Center=Center)

    def Rasterize(self, Coordinate: numpy.ndarray, Shape: list):

        Exterior = Path(list( self.exterior.coords))

        Exterior = Exterior.contains_points(Coordinate).reshape(Shape)

        Exterior = Exterior.astype(float)

        self.Raster = Exterior


    def Plot(self, **kwargs):
        Fig = Plots.Scene('SuPyMode Figure', UnitSize=(6,6))

        ax = Plots.Axis(Row      = 0,
                        Col      = 0,
                        xLabel   = r'x',
                        yLabel   = r'y',
                        Title    = f'Circle',
                        Grid     = True,
                        Equal    = True)

        Fig.AddAxes(ax).GenerateAxis()

        self.__render__(ax)

        Fig.Show()

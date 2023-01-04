#!/usr/bin/env python
# -*- coding: utf-8 -*-

import FiberFusing.Buffer as Buffer
from MPSPlots.Render2D import Scene2D, Axis


class Circle(_buffer.Circle):
    Radius: float = None
    Core: Buffer.Point = None
    center: Buffer.Point = None
    Index = None

    def __new__(cls, Radius: float, center: tuple = (0, 0), Name: str = '', Index: float = None):
        center = Buffer.Point(center) if isinstance(center, (tuple, list)) else center
        Instance = Buffer.Circle.__new__(cls, Radius=Radius, center=center)
        return Instance

    @property
    def Object(self):
        return self

    def __init__(self, Radius: float, center: tuple = (0, 0), Name: str = '', Index: float = None):
        center = Buffer.Point(center) if isinstance(center, (tuple, list)) else center
        self.Radius = Radius
        self.Name = Name
        self.center = center
        self.Core = Buffer.Point([center.x, center.y])
        self.Core.facecolor = 'k'
        self.Index = Index

        super(Circle, self).__init__(Radius=Radius, center=center)

    def plot(self, **kwargs) -> Scene2D:
        figure = Scene2D(title='SuPyMode Figure', unit_size=(6, 6))

        ax = Axis(row=0,
                  col=0,
                  x_label='x',
                  y_label='y',
                  show_grid=True,
                  equal=True)

        figure.add_axes(ax)

        figure._render_()

        self._render_(ax)

        return figure


# a = Circle(Radius=10).plot().Show()
# -

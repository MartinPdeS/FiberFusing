
import numpy, logging
import matplotlib.pyplot as plt

import FiberFusing.Buffer as Buffer 
import MPSPlots.Plots as Plots


class Fiber(Buffer.Circle):
    Radius: float=None
    Core: Buffer.Point=None
    Center: Buffer.Point=None

    def __new__(cls, Radius: float, Center: list, Name: str = ''):
        Instance = Buffer.Circle.__new__(cls, Radius=Radius, Center=Center)
        return Instance

    def __init__(self, Radius: float, Center: list, Name: str = ''):
        self.Radius = Radius
        self.Name = Name
        self.Center = Center
        self.Core = Buffer.Point([Center.x, Center.y])
        self.Core.facecolor='k'

        super(Fiber, self).__init__(Radius=Radius, Center=Center)


    def __str__(self):
        return f" Center: {self.Center} \t Core position: {self.Core} \t Radius: {self.Radius}"



    def __render__(self, Ax):
        super().__render__(Ax)

        self.Core.__render__(Ax)
        self.Center.__render__(Ax)

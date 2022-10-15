#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest, inspect
from pyface.api import GUI

from FiberFusing import Geometry, Fused2, Fused3, Fused4, Fused7, Circle, BackGround
from utils import BaseStepTest, TestFactory, Close

PLOTTIME = 1000 # one seconde
N=150

Index = 1.5
Air = BackGround(Index=1) 


class CouplerTestCase(unittest.TestCase, BaseStepTest):

    @TestFactory('1x1 coupler')
    def step00(self):
        Clad = Circle(Radius=62.5, Index=Index, Center=(0,0))

        self.Geo = Geometry(Objects = [Air, Clad],
                           Xbound  = [-120, 120],
                           Ybound  = [-120, 120],
                           Nx      = N,
                           Ny      = N)

        self.Geo.Rotate(90)

        GUI.invoke_after(PLOTTIME, Close)
        self.Geo.Plot().Show()



    @TestFactory('2x2 coupler')
    def step01(self):
        Clad = Fused2(FiberRadius = 62.5, Fusion = 0.5, Index=Index)

        Cores = [ Circle(Center=Core, Radius=4.1, Index=Index+0.005) for Core in Clad.Cores]

        self.Geo = Geometry(Objects = [Air, Clad] + Cores,
                           Xbound  = [-120, 120],
                           Ybound  = [-120, 120],
                           Nx      = N,
                           Ny      = N)

        self.Geo.Rotate(90)

        GUI.invoke_after(PLOTTIME, Close)
        self.Geo.Plot().Show()




    @TestFactory('3x3 coupler')
    def step02(self):
        Clad = Fused3(FiberRadius=62.5, Fusion=0.5, Index=Index)

        Cores = [ Circle(Center=Core, Radius=4.1, Index=Index+0.005) for Core in Clad.Cores]

        self.Geo = Geometry(Objects = [Air, Clad] + Cores,
                           Xbound  = [-130, 130],
                           Ybound  = [-130, 130],
                           Nx      = N,
                           Ny      = N)

        self.Geo.Rotate(90)

        GUI.invoke_after(PLOTTIME, Close)
        self.Geo.Plot().Show()




    @TestFactory('4x4 coupler')
    def step03(self):
        Clad = Fused4(FiberRadius = 62.5, Fusion = 0.5, Index = 1.5)

        Cores = [ Circle(Center=Core, Radius=4.1, Index=Index+0.005) for Core in Clad.Cores]

        self.Geo = Geometry(Objects = [Air, Clad] + Cores,
                           Xbound  = [-150, 150],
                           Ybound  = [-150, 150],
                           Nx      = N,
                           Ny      = N)

        self.Geo.Rotate(90)

        GUI.invoke_after(PLOTTIME, Close)
        self.Geo.Plot().Show()




    @TestFactory('7x7 coupler')
    def step04(self):
        Clad = Fused7(FiberRadius = 62.5, Fusion = 0.5, Index = 1.5)

        Cores = [ Circle(Center=Core, Radius=4.1, Index=Index+0.005) for Core in Clad.Cores]

        self.Geo = Geometry(Objects = [Air, Clad] + Cores,
                           Xbound  = [-180, 180],
                           Ybound  = [-180, 180],
                           Nx      = N,
                           Ny      = N)

        self.Geo.Rotate(90)

        GUI.invoke_after(PLOTTIME, Close)
        self.Geo.Plot().Show()




def suite():
    suite = unittest.TestSuite()

    suite.addTest(CouplerTestCase('test_steps'))

    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner(failfast=True)
    runner.run(suite())
























# - 
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest.mock import patch

from FiberFusing import Geometry, Fused2, Fused3, Fused4, Fused7, Circle, BackGround


Index = 1.5
Air = BackGround(Index=1)


@patch("matplotlib.pyplot.show")
def test_fused1(patch):
    clad = Circle(Radius=62.5, Index=1.4, center=(0, 0))

    clad.Plot().Show().Close()


@patch("matplotlib.pyplot.show")
def test_fused1_raster(patch):
    clad = Circle(Radius=62.5, Index=1.4, center=(0, 0))

    clad.Plot().Show().Close()

    geometry = Geometry(background=BackGround(Index=1), clad=clad, cores=[], x_bound=[-150, 0], y_bound=[-150, 0], n_x=20, n_y=20)

    geometry.Plot().Show()


@patch("matplotlib.pyplot.show")
def test_fused2(patch):
    clad = Fused2(Fusion=0.8, FiberRadius=62.5, Index=1.4)

    clad.Plot().Show().Close()


@patch("matplotlib.pyplot.show")
def test_fused2_raster(patch):
    clad = Fused2(Fusion=0.8, FiberRadius=62.5, Index=1.4)

    clad.Plot().Show().Close()

    geometry = Geometry(background=BackGround(Index=1), clad=clad, cores=[], x_bound=[-150, 0], y_bound=[-150, 0], n_x=20, n_y=20)

    geometry.Plot().Show()


@patch("matplotlib.pyplot.show")
def test_fused3(patch):
    clad = Fused3(Fusion=0.8, FiberRadius=62.5, Index=1.4)

    clad.Plot().Show().Close()


@patch("matplotlib.pyplot.show")
def test_fused3_raster(patch):
    clad = Fused3(Fusion=0.8, FiberRadius=62.5, Index=1.4)

    clad.Plot().Show().Close()

    geometry = Geometry(background=BackGround(Index=1), clad=clad, cores=[], x_bound=[-150, 0], y_bound=[-150, 0], n_x=20, n_y=20)

    geometry.Plot().Show()


@patch("matplotlib.pyplot.show")
def test_fused4(patch):
    clad = Fused4(Fusion=0.8, FiberRadius=62.5, Index=1.4)

    clad.Plot().Show().Close()


@patch("matplotlib.pyplot.show")
def test_fused4_raster(patch):
    clad = Fused4(Fusion=0.8, FiberRadius=62.5, Index=1.4)

    clad.Plot().Show().Close()

    geometry = Geometry(background=BackGround(Index=1), clad=clad, cores=[], x_bound=[-150, 0], y_bound=[-150, 0], n_x=20, n_y=20)

    geometry.Plot().Show()


@patch("matplotlib.pyplot.show")
def test_fused7(patch):
    clad = Fused7(Fusion=0.6, FiberRadius=62.5, Index=1.4)

    clad.Plot().Show().Close()


@patch("matplotlib.pyplot.show")
def test_fused7_raster(patch):
    clad = Fused7(Fusion=0.6, FiberRadius=62.5, Index=1.4)

    geometry = Geometry(background=BackGround(Index=1), clad=clad, cores=[], x_bound=[-150, 0], y_bound=[-150, 0], n_x=20, n_y=20)

    geometry.Plot().Show()


from FiberFusing.Buffer import Circle, Polygon
import shapely.geometry as geo

a = geo.Point([0, 1])
b = geo.Point([0, 3])
c = geo.Point([1, 1])
polygon = Polygon([a, b, c])

# polygon = polygon.Scale(100)
polygon = polygon.Translate([100, 0])

circle0 = Circle(Radius=10, center=(1, 1))
# circle0 = circle0.Scale(100)
# circle0 = circle0.Translate([100, 0])
# circle0.center = [200, 200]

# circle0.Plot().Show()

# -

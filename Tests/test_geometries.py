#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest.mock import patch

from FiberFusing import Geometry, Fused2, Fused3, Fused4, Fused7, Circle, BackGround


index = 1.5
air = BackGround(index=1)

kwargs = {'background': air,
           'x_bound': 'auto',
           'y_bound': 'auto',
           'n_x': 20,
           'n_y': 20}


@patch("matplotlib.pyplot.show")
def test_fused1(patch):
    clad = Circle(radius=62.5, index=1.4, center=(0, 0))

    clad.Plot().Show().Close()


@patch("matplotlib.pyplot.show")
def test_fused1_raster(patch):
    clad = Circle(radius=62.5, index=1.4, center=(0, 0))

    clad.Plot().Show().Close()

    geometry = Geometry(clad=clad, cores=[], **kwargs)

    geometry.Plot().Show()


@patch("matplotlib.pyplot.show")
def test_fused2(patch):
    clad = Fused2(fusion_degree=0.8, fiber_radius=62.5, index=1.4)

    clad.Plot().Show().Close()


@patch("matplotlib.pyplot.show")
def test_fused2_raster(patch):
    clad = Fused2(fusion_degree=0.8, fiber_radius=62.5, index=1.4)

    clad.Plot().Show().Close()

    geometry = Geometry(clad=clad, cores=[], **kwargs)

    geometry.Plot().Show()


@patch("matplotlib.pyplot.show")
def test_fused3(patch):
    clad = Fused3(fusion_degree=0.8, fiber_radius=62.5, index=1.4)

    clad.Plot().Show().Close()


@patch("matplotlib.pyplot.show")
def test_fused3_raster(patch):
    clad = Fused3(fusion_degree=0.8, fiber_radius=62.5, index=1.4)

    clad.Plot().Show().Close()

    geometry = Geometry(clad=clad, cores=[], **kwargs)

    geometry.Plot().Show()


@patch("matplotlib.pyplot.show")
def test_fused4(patch):
    clad = Fused4(fusion_degree=0.8, fiber_radius=62.5, index=1.4)

    clad.Plot().Show().Close()


@patch("matplotlib.pyplot.show")
def test_fused4_raster(patch):
    clad = Fused4(fusion_degree=0.8, fiber_radius=62.5, index=1.4)

    clad.Plot().Show().Close()

    geometry = Geometry(clad=clad, cores=[], **kwargs)

    geometry.Plot().Show()


@patch("matplotlib.pyplot.show")
def test_fused7(patch):
    clad = Fused7(fusion_degree=0.6, fiber_radius=62.5, index=1.4)

    clad.Plot().Show().Close()


@patch("matplotlib.pyplot.show")
def test_fused7_raster(patch):
    clad = Fused7(fusion_degree=0.6, fiber_radius=62.5, index=1.4)

    geometry = Geometry(clad=clad, cores=[], **kwargs)

    geometry.Plot().Show()

# -

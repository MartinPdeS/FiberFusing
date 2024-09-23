#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy

from matplotlib.path import Path
from matplotlib.patches import PathPatch
from matplotlib.collections import PatchCollection


def plot_polygon(ax, poly, **kwargs):
    path = Path.make_compound_path(
        Path(numpy.asarray(poly.exterior.coords)[:, :2]),
        *[Path(numpy.asarray(ring.coords)[:, :2]) for ring in poly.interiors])

    patch = PathPatch(path, **kwargs)
    collection = PatchCollection([patch], alpha=0.3, **kwargs)

    ax.add_collection(collection, autolim=True)
    ax.autoscale_view()
    return collection

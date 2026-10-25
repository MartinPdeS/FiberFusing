"""Verify plotting without an external style or wrapper package."""

import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import matplotlib.pyplot as plt
import pytest

from FiberFusing import Point
from FiberFusing.plottings import plotting


class Demo:
    """Small drawable used to exercise figure ownership and layout."""

    @plotting()
    def plot(self, axes):
        """Draw one line."""
        axes.plot([1, 2], [3, 4])

    @plotting(ncols=2)
    def panels(self, axes):
        """Draw on two axes."""
        for axis in axes:
            axis.plot([1, 2], [3, 4])

    @plotting()
    def broken(self, axes):
        """Fail after axes creation."""
        raise RuntimeError("Drawing failed")


@pytest.fixture(autouse=True)
def close_figures():
    """Keep plotting tests independent."""
    yield
    plt.close("all")


def test_real_point_returns_figure_without_display():
    """A public plot supports headless use."""
    with patch("matplotlib.pyplot.show") as show:
        figure = Point(position=(0.0, 0.0)).plot(show=False)
    assert isinstance(figure, plt.Figure)
    assert len(figure.axes[0].collections) == 1
    show.assert_not_called()


def test_preserves_supplied_axes_and_can_save(tmp_path):
    """Caller-owned axes are reused, with display controls and export intact."""
    figure, axis = plt.subplots()
    with patch("matplotlib.pyplot.show") as show:
        result = Demo().plot(axes=axis, show=False, save_as=tmp_path / "plot.png", xlim=(0, 5))
    assert result is figure
    assert len(figure.axes) == 1
    assert axis.get_xlim() == (0.0, 5.0)
    assert (tmp_path / "plot.png").stat().st_size > 0
    show.assert_not_called()


def test_multiple_panels():
    """Multi-panel methods accept both new and caller-supplied layouts."""
    figure = Demo().panels(show=False)
    assert len(figure.axes) == 2
    supplied, axes = plt.subplots(1, 2)
    assert Demo().panels(axes=axes, show=False) is supplied
    assert all(len(axis.lines) == 1 for axis in supplied.axes)


def test_rejects_incorrect_layout_and_mixed_figures():
    """A layout error does not silently draw into the wrong panel."""
    first, axis = plt.subplots()
    second, other = plt.subplots()
    with pytest.raises(ValueError, match="Expected 2 axes"):
        Demo().panels(axes=axis, show=False)
    with pytest.raises(ValueError, match="same figure"):
        Demo().panels(axes=[axis, other], show=False)
    assert plt.fignum_exists(first.number)
    assert plt.fignum_exists(second.number)


def test_scoped_style_restores_settings():
    """Local style overrides do not modify the caller's Matplotlib defaults."""
    before = plt.rcParams["axes.facecolor"]
    figure = Demo().plot(show=False, style={"axes.facecolor": "pink"})
    assert figure.axes[0].get_facecolor() == (1.0, 0.7529411764705882, 0.796078431372549, 1.0)
    assert plt.rcParams["axes.facecolor"] == before


def test_failure_closes_only_created_figures():
    """Failed plotting cannot leak a new figure or close a caller's figure."""
    before = plt.get_fignums()
    with pytest.raises(RuntimeError, match="Drawing failed"):
        Demo().broken(show=False)
    assert plt.get_fignums() == before
    figure, axis = plt.subplots()
    with pytest.raises(RuntimeError):
        Demo().broken(axes=axis, show=False)
    assert plt.fignum_exists(figure.number)


def test_import_and_plot_with_external_package_blocked():
    """Importing and rendering works even when the former dependency is unavailable."""
    code = """
import importlib.abc
import sys
class Block(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == "MPSPlots" or fullname.startswith("MPSPlots."):
            raise ImportError("External plotting package is blocked")
sys.meta_path.insert(0, Block())
from FiberFusing import Point
figure = Point(position=(0.0, 0.0)).plot(show=False)
assert len(figure.axes) == 1
assert "MPSPlots" not in sys.modules
"""
    subprocess.run(
        [sys.executable, "-c", code],
        cwd=Path(__file__).resolve().parents[1],
        env={**os.environ, "MPLBACKEND": "Agg"},
        check=True,
        capture_output=True,
        text=True,
    )

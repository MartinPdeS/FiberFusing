"""Validate explicit release metadata and the distributed fiber catalog."""

import runpy
from importlib.resources import files
from pathlib import Path

import yaml

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


def test_release_metadata_agrees():
    """Wheel, Python API, and Conda use the same explicit version."""
    root = Path(__file__).resolve().parents[1]
    # Conda stages tests separately from the project sources; catalog checks
    # below still exercise its installed package in that environment.
    if not (root / "pyproject.toml").is_file():
        import pytest

        pytest.skip("Project metadata is not staged in this installed-package test")
    project = tomllib.loads((root / "pyproject.toml").read_text())["project"]
    package = runpy.run_path(str(root / "FiberFusing/_version.py"))
    recipe = yaml.safe_load(
        (root / "conda.recipe/meta.yaml")
        .read_text()
        .replace("{{ PY_VER }}", "3.11")
        .replace("{{ PYTHON }}", "python")
    )
    assert project["version"] == package["__version__"] == str(recipe["package"]["version"])
    assert "version" not in project.get("dynamic", [])


def test_installed_fiber_catalog():
    """Named catalog records remain available in installed distributions."""
    catalog = files("FiberFusing.fiber").joinpath("fiber_files")
    for name in ["SMF28.yaml", "HI1060.yaml", "1550BHP.yaml"]:
        record = catalog.joinpath(name)
        assert record.is_file()
        assert yaml.safe_load(record.read_text())["layers"]

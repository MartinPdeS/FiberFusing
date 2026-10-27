"""Check the documentation version without depending on a release tag."""

import runpy
from pathlib import Path

import pytest


def test_documentation_uses_package_version(monkeypatch):
    """Sphinx and the switcher use the package's explicit version."""
    pytest.importorskip("martinpdes_docs")
    root = Path(__file__).resolve().parents[1]
    if not (root / "docs/source/conf.py").is_file():
        pytest.skip("Documentation sources are not staged.")
    monkeypatch.setenv("tag", "v9.9.9")
    config = runpy.run_path(str(root / "docs/source/conf.py"))
    expected = runpy.run_path(str(root / "FiberFusing/_version.py"))["__version__"]
    assert config["version"] == config["release"] == expected
    assert config["html_theme_options"]["switcher"]["version_match"] == expected

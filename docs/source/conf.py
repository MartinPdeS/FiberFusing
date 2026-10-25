"""Shared Sphinx configuration for FiberFusing."""

from pathlib import Path

from martinpdes_docs import configure


docs_source = Path(__file__).resolve().parent

globals().update(
    configure(
        project="FiberFusing",
        package="FiberFusing",
        repository="MartinPdeS/FiberFusing",
        logo="_static/logo.png",
        favicon="_static/favicon.png",
        gallery_default_thumb=str(docs_source / "_static" / "icon.png"),
        gallery_options={
            "examples_dirs": "../examples",
            "gallery_dirs": "gallery",
            "abort_on_example_error": True,
            "capture_repr": (),
        },
    )
)

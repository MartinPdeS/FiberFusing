"""Shared Sphinx configuration for FiberFusing."""

from pathlib import Path

from martinpdes_docs import configure


docs_source = Path(__file__).resolve().parent

globals().update(
    configure(
        project="FiberFusing",
        package="FiberFusing",
        repository="MartinPdeS/FiberFusing",
        logo="_static/thumbnail.png",
        favicon="_static/thumbnail.png",
        gallery_default_thumb=str(docs_source / "_static" / "thumbnail.png"),
        gallery_options={
            "examples_dirs": "../examples",
            "gallery_dirs": "gallery",
            "abort_on_example_error": True,
            "capture_repr": (),
        },
    )
)


def document_wrapped_plots(app, what, name, obj, options, lines):
    """Render original NumPy docstrings before processing plotting wrappers.

    MPSPlots appends an indented docstring fragment to decorated methods. Its
    section headings are not valid reStructuredText in that position. Keep the
    original method documentation and document the wrapper options as a note.
    """
    import inspect

    if name.startswith("FiberFusing.") and hasattr(obj, "__wrapped__"):
        original = inspect.getdoc(inspect.unwrap(obj))
        if original:
            lines[:] = original.splitlines()
            lines.extend(
                [
                    "",
                    ".. note::",
                    "   Plotting wrappers also accept ``show``, ``save_as``,",
                    "   ``figure_size``, ``tight_layout``, ``axes``, ``xscale``,",
                    "   ``yscale``, ``xlim``, ``ylim``, and ``style`` options.",
                ]
            )


def setup(app):
    """Normalize decorated plotting documentation before NumPy doc processing."""
    app.connect("autodoc-process-docstring", document_wrapped_plots, priority=100)

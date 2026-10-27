Plotting
========

FiberFusing uses Matplotlib directly. Plot methods return a Matplotlib Figure
and accept ``show=False`` for scripts, notebooks, and headless use::

    from FiberFusing import Point

    figure = Point(position=(0.0, 0.0)).plot(show=False)
    figure.savefig("point.png")

Supply ``axes=`` to draw into an existing figure. ``Geometry.plot`` requires
two axes, while single-panel methods require one. All supplied axes must belong
to the same figure. Plot methods also accept ``save_as``, ``figure_size``,
``tight_layout``, ``xscale``, ``yscale``, ``xlim``, and ``ylim``.

The ``style`` argument accepts a Matplotlib style name or dictionary and applies
only during that call. With no style argument, the caller's Matplotlib settings
are preserved. No external plotting-style package is required. Existing
interactive behavior is retained: plots display by default, so set
``show=False`` when automatic display is unwanted.

|logo|

.. list-table::
   :widths: 35 65
   :header-rows: 1

   * - Badge
     - Status
   * - Python versions
     - |python|
   * - Documentation
     - |docs|
   * - Continuous integration
     - |ci/cd|
   * - Test coverage
     - |coverage|
   * - Google Colab
     - |colab|
   * - PyPI package
     - |PyPi|
   * - PyPI downloads
     - |PyPi_download|
   * - Anaconda package
     - |anaconda|
   * - Anaconda downloads
     - |anaconda_download|

FiberFusing
===========

**FiberFusing** is an open-source Python package for parametrized fused-fiber
cross-sections and refractive-index meshes. Define a fiber arrangement, adjust
its fusion degree, and combine the resulting profile with optical fibers and a
background medium.

Features
--------

- Circular and linear fiber arrangements with adjustable fusion degree.
- Geometric connection optimization with area-conservation diagnostics.
- Fiber catalog loading and refractive-index mesh generation.
- Core-position perturbations with reproducible random seeds.
- Matplotlib plots with supplied-axes support and headless rendering.

Installation
------------

Install from PyPI using the Python interpreter for your simulations:

.. code-block:: bash

   python -m pip install FiberFusing

Alternatively, install from the MartinPdeS Anaconda channel:

.. code-block:: bash

   conda install -c MartinPdeS fiberfusing

Verify the installation with:

.. code-block:: bash

   python -c "import FiberFusing; print(FiberFusing.__version__)"

Python compatibility
--------------------

FiberFusing supports **Python 3.10, 3.11, 3.12, 3.13, and 3.14**. The full test
suite runs on all five versions in
`GitHub Actions <https://github.com/MartinPdeS/FiberFusing/actions/workflows/tests.yml>`_.

The package contains pure Python code. Its universal wheel and Conda ``noarch``
package can be installed on these Python versions without compiling FiberFusing.
Release artifacts are currently built and installation-checked on Python 3.11;
source tests also run on Python 3.13 and 3.14.

First simulation
----------------

Build a circular arrangement of three fibers with a cladding radius of
62.5 micrometers. Lengths in this example use meters; refractive indices are
dimensionless.

.. code-block:: python

   from FiberFusing import Geometry, DomainAlignment, BackGround
   from FiberFusing.fiber import FiberLoader
   from FiberFusing.profile import Profile, StructureType

   air_background = BackGround(refractive_index=1.0)

   profile = Profile()

   profile.add_structure(
      structure_type=StructureType.CIRCULAR,
      number_of_fibers=3,
      fusion_degree=0.4,
      fiber_radius=62.5e-6
   )

   profile.refractive_index = 1.4444

   fiber_loader = FiberLoader()
   fibers = [
      fiber_loader.load_fiber('SMF28', clad_refractive_index=profile.refractive_index, position=core_position)
      for core_position in profile.cores
   ]

   geometry = Geometry(
      x_bounds=DomainAlignment.CENTERING,
      y_bounds=DomainAlignment.CENTERING,
      resolution=350
   )

   geometry.add_structure(air_background, profile, *fibers)

   geometry.initialize()

   geometry.plot()

|example_3x3|

For headless workflows, use ``geometry.plot(show=False)`` to obtain a Matplotlib
figure without opening a window. See the
`plotting guide <https://martinpdes.github.io/FiberFusing/docs/latest/plotting.html>`_
for supplied axes, styling, and export options.

Documentation and examples
--------------------------

See the `online documentation
<https://martinpdes.github.io/FiberFusing/docs/latest/>`_ for the API and
numerical behavior, and the `example gallery
<https://martinpdes.github.io/FiberFusing/docs/latest/gallery/index.html>`_
for runnable fiber configurations.

Developer setup
---------------

Clone the repository, select Python 3.10 or newer, and install the development
and testing dependencies:

.. code-block:: bash

   git clone https://github.com/MartinPdeS/FiberFusing.git
   cd FiberFusing
   python -m pip install -e ".[testing,dev,release]"

Run checks with the same interpreter:

.. code-block:: bash

   MPLBACKEND=Agg python -m pytest
   python -m ruff check FiberFusing tests
   make release-check PYTHON=python

See ``CONTRIBUTING.md`` for documentation builds, installed-package checks, and
release commands. Versions are explicit and releases use the shared
``martinpdes-maintenance`` tool.

Contact
-------

For questions or contributions, open an issue on
`GitHub <https://github.com/MartinPdeS/FiberFusing/issues>`_ or contact
`Martin Poinsinet de Sivry-Houle
<mailto:martin.poinsinet-de-sivry@polymtl.ca?subject=FiberFusing>`_.

.. |python| image:: https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue
   :target: https://github.com/MartinPdeS/FiberFusing/actions/workflows/tests.yml
   :alt: Supported and tested Python versions: 3.10, 3.11, 3.12, 3.13, 3.14

.. |PyPi| image:: https://badge.fury.io/py/FiberFusing.svg
   :target: https://pypi.org/project/FiberFusing/
   :alt: PyPi

.. |PyPi_download| image:: https://img.shields.io/pypi/dm/fiberfusing.svg
   :target: https://pypistats.org/packages/fiberfusing
   :alt: PyPi download statistics

.. |logo| image:: https://github.com/MartinPdeS/FiberFusing/raw/master/docs/images/logo.png
   :alt: FiberFusing navy and coral seven-core logo
   :width: 720px

.. |docs| image:: https://github.com/martinpdes/fiberfusing/actions/workflows/deploy_documentation.yml/badge.svg
   :target: https://martinpdes.github.io/FiberFusing/
   :alt: Documentation Status

.. |coverage| image:: https://raw.githubusercontent.com/MartinPdeS/FiberFusing/python-coverage-comment-action-data/badge.svg
   :target: https://htmlpreview.github.io/?https://github.com/MartinPdeS/FiberFusing/blob/python-coverage-comment-action-data/htmlcov/index.html
   :alt: Unittest coverage

.. |ci/cd| image:: https://github.com/martinpdes/fiberfusing/actions/workflows/tests.yml/badge.svg
   :target: https://github.com/MartinPdeS/FiberFusing/actions
   :alt: Unittest Status

.. |anaconda_download| image:: https://anaconda.org/martinpdes/fiberfusing/badges/downloads.svg
   :alt: Anaconda downloads
   :target: https://anaconda.org/martinpdes/fiberfusing

.. |anaconda| image:: https://anaconda.org/martinpdes/fiberfusing/badges/version.svg
   :alt: Anaconda version
   :target: https://anaconda.org/martinpdes/fiberfusing

.. |example_3x3| image:: https://github.com/MartinPdeS/FiberFusing/raw/master/docs/images/example_3x3.png
   :alt: Three-fiber fused cross-section and refractive-index mesh

.. |colab| image:: https://colab.research.google.com/assets/colab-badge.svg
   :target: https://colab.research.google.com/github/MartinPdeS/FiberFusing/blob/master/notebook.ipynb

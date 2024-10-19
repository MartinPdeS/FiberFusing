FiberFusing
===========

|logo|


.. list-table::
   :widths: 10 25 25
   :header-rows: 0

   * - Meta
     - |python|
     - |docs|
   * - Testing
     - |ci/cd|
     - |coverage|
   * - PyPi
     - |PyPi|
     - |PyPi_download|
   * - Anaconda
     - |anaconda|
     - |anaconda_download|


FiberFusing is a Python package designed for simulating the fiber fusing process. With this tool, users can define an initial fiber configuration and simulate the fusion process as a function of the fusion degree parameter. The package currently supports seven predefined structures:

1x1, 2x2, 3x3, 4x4, 6x6, 7x7, and 19x19 configurations.

As follows, an example of 3x3 fused fiber.
|example_3x3|


----

Documentation
**************
For the most up-to-date documentation, visit the official `FiberFusing Docs <https://fiberfusing.readthedocs.io/en/latest/>`_ or click the badge below:

|docs|

----

Installation
************
Getting started with FiberFusing is easy. Simply install via `pip`:

.. code-block:: bash

    pip install FiberFusing

|PyPi|

----

Testing
*******
To run tests locally after cloning the GitHub repository, you’ll need to install the dependencies and run the following commands:

.. code-block:: bash

    git clone https://github.com/MartinPdeS/FiberFusing.git
    cd FiberFusing
    pip install FiberFusing[testing]
    pytest

For more detailed testing instructions, consult the documentation.

----

Coding examples
***************
Explore a wide range of examples demonstrating the usage of FiberFusing in the `Examples section <https://martinpdes.github.io/FiberFusing/gallery/index.html>`_ of the documentation.

----

Contributing & Contact
***********************
FiberFusing is an open project and collaboration is encouraged! If you're interested in contributing or have any questions, feel free to reach out.

**Author:** `Martin Poinsinet de Sivry-Houle <https://github.com/MartinPdeS>`_
**Email:** `martin.poinsinet-de-sivry@polymtl.ca <mailto:martin.poinsinet-de-sivry@polymtl.ca?subject=FiberFusing>`_

We welcome feedback and contributions to improve FiberFusing and expand its capabilities.

----

.. |python| image:: https://img.shields.io/pypi/pyversions/fiberfusing.svg
   :target: https://www.python.org/
   :alt: Python version

.. |PyPi| image:: https://badge.fury.io/py/FiberFusing.svg
   :target: https://pypi.org/project/FiberFusing/
   :alt: PyPi

.. |PyPi_download| image:: https://img.shields.io/pypi/dm/fiberfusing.svg
   :target: https://pypistats.org/packages/fiberfusing
   :alt: PyPi download statistics

.. |logo| image:: https://github.com/MartinPdeS/FiberFusing/raw/master/docs/images/logo.png
   :alt: FiberFusing's logo

.. |docs| image:: https://github.com/martinpdes/fiberfusing/actions/workflows/deploy_documentation.yml/badge.svg
   :target: https://martinpdes.github.io/FiberFusing/
   :alt: Documentation Status

.. |coverage| image:: https://raw.githubusercontent.com/MartinPdeS/FiberFusing/python-coverage-comment-action-data/badge.svg
   :target: https://htmlpreview.github.io/?https://github.com/MartinPdeS/FiberFusing/blob/python-coverage-comment-action-data/htmlcov/index.html
   :alt: Unittest coverage

.. |ci/cd| image:: https://github.com/martinpdes/fiberfusing/actions/workflows/deploy_coverage.yml/badge.svg
   :target: https://martinpdes.github.io/FiberFusing/actions
   :alt: Unittest Status

.. |anaconda_download| image:: https://anaconda.org/martinpdes/fiberfusing/badges/downloads.svg
   :alt: Anaconda downloads
   :target: https://anaconda.org/martinpdes/fiberfusing

.. |anaconda| image:: https://anaconda.org/martinpdes/fiberfusing/badges/version.svg
   :alt: Anaconda version
   :target: https://anaconda.org/martinpdes/fiberfusing

.. |example_3x3| image:: https://github.com/MartinPdeS/FiberFusing/raw/master/docs/images/example_3x3.png
   :alt: Example for 3 fiber structure
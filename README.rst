|Logo|


|python|
|PyPi|
|PyPi_download|
|docs|
|Unittest|

FiberFusing
===========
Python package for fiber fusing simulations. This package allow the user to defined an initial fibre configuration and simulate the fusion process as a funciton of the fusion degree parameter. At the moment a total of seven pre-defined structure are present: 1x1, 2x2, 3x3, 4x4, 6x6, 7x7, 19x19.


----

Documentation
**************
All the latest available documentation is available `here <https://fiberfusing.readthedocs.io/en/latest/>`_ or you can click the following badge:

|docs|





----

Installation
************
As simple as it gets using pip

.. code-block:: python

   >>> pip install FiberFusing

|PyPi|





----

Testing
*******

To test localy (with cloning the GitHub repository) you'll need to install the dependencies and run the coverage command as

.. code:: console

   >>> git clone https://github.com/MartinPdeS/FiberFusing.git
   >>> cd FiberFusing
   >>> pip install -r requirements/requirements.txt
   >>> coverage run --source=FiberFusing --module pytest --verbose tests
   >>> coverage report --show-missing

----



Coding examples
***************
Plenty of examples are available online, I invite you to check the `examples <https://fiberfusing.readthedocs.io/en/latest/Examples.html>`_
section of the documentation.





----

Contact Information
*******************
As of 2021 the project is still under development if you want to collaborate it would be a pleasure. I encourage you to contact me.

FiberFusing was written by `Martin Poinsinet de Sivry-Houle <https://github.com/MartinPdS>`_  .

Email:`martin.poinsinet-de-sivry@polymtl.ca <mailto:martin.poinsinet-de-sivry@polymtl.ca?subject=FiberFusing>`_ .


.. |Unittest| image:: https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/MartinPdeS/49dc3e2c41180ac9018ae803a8acd177/raw

.. |python| image:: https://img.shields.io/pypi/pyversions/fiberfusing.svg
   :target: https://www.python.org/

.. |PyPi| image:: https://badge.fury.io/py/FiberFusing.svg
   :target: https://pypi.org/project/FiberFusing/

.. |PyPi_download| image:: https://img.shields.io/pypi/dm/fiberfusing.svg
   :target: https://pypistats.org/packages/fiberfusing

.. |Logo| image:: https://github.com/MartinPdeS/FiberFusing/raw/master/docs/images/logo.png

.. |docs| image:: https://readthedocs.org/projects/fiberfusing/badge/?version=latest
   :target: https://fiberfusing.readthedocs.io/en/latest/?badge=latest

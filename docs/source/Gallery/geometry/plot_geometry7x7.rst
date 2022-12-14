
.. DO NOT EDIT.
.. THIS FILE WAS AUTOMATICALLY GENERATED BY SPHINX-GALLERY.
.. TO MAKE CHANGES, EDIT THE SOURCE PYTHON FILE:
.. "Gallery/geometry/plot_geometry7x7.py"
.. LINE NUMBERS ARE GIVEN BELOW.

.. only:: html

    .. note::
        :class: sphx-glr-download-link-note

        Click :ref:`here <sphx_glr_download_Gallery_geometry_plot_geometry7x7.py>`
        to download the full example code

.. rst-class:: sphx-glr-example-title

.. _sphx_glr_Gallery_geometry_plot_geometry7x7.py:


7x7 Geometry
============

.. GENERATED FROM PYTHON SOURCE LINES 5-30



.. image-sg:: /Gallery/geometry/images/sphx_glr_plot_geometry7x7_001.png
   :alt: , Refractive index structure, Refractive index gradient
   :srcset: /Gallery/geometry/images/sphx_glr_plot_geometry7x7_001.png
   :class: sphx-glr-single-img


.. rst-class:: sphx-glr-script-out

 .. code-block:: none


    Scene2D(unit_size=(6, 6), tight_layout=True, title='')





|

.. code-block:: python3
   :lineno-start: 6


    from FiberFusing import Geometry, Fused7, Circle, BackGround
    from PyOptik import ExpData

    Wavelength = 1.55e-6
    index = ExpData('FusedSilica').GetRI(Wavelength)

    air = BackGround(index=1.0)

    clad = Fused7(fiber_radius=60, fusion_degree=0.6, index=index)

    cores = [Circle(center=core, radius=4.1, index=index + 0.005) for core in clad.cores]

    geo = Geometry(background=air,
                   clad=clad,
                   cores=cores,
                   x_bound='auto',
                   y_bound='auto',
                   n_x=180,
                   n_y=180)

    geo.Plot().Show()


    # -


.. rst-class:: sphx-glr-timing

   **Total running time of the script:** ( 0 minutes  6.600 seconds)


.. _sphx_glr_download_Gallery_geometry_plot_geometry7x7.py:

.. only:: html

  .. container:: sphx-glr-footer sphx-glr-footer-example


    .. container:: sphx-glr-download sphx-glr-download-python

      :download:`Download Python source code: plot_geometry7x7.py <plot_geometry7x7.py>`

    .. container:: sphx-glr-download sphx-glr-download-jupyter

      :download:`Download Jupyter notebook: plot_geometry7x7.ipynb <plot_geometry7x7.ipynb>`


.. only:: html

 .. rst-class:: sphx-glr-signature

    `Gallery generated by Sphinx-Gallery <https://sphinx-gallery.github.io>`_

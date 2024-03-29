
.. DO NOT EDIT.
.. THIS FILE WAS AUTOMATICALLY GENERATED BY SPHINX-GALLERY.
.. TO MAKE CHANGES, EDIT THE SOURCE PYTHON FILE:
.. "gallery/clad/plot_clad_03.py"
.. LINE NUMBERS ARE GIVEN BELOW.

.. only:: html

    .. note::
        :class: sphx-glr-download-link-note

        :ref:`Go to the end <sphx_glr_download_gallery_clad_plot_clad_03.py>`
        to download the full example code

.. rst-class:: sphx-glr-example-title

.. _sphx_glr_gallery_clad_plot_clad_03.py:


3x3 Ring - Clad
===============

.. GENERATED FROM PYTHON SOURCE LINES 5-21



.. image-sg:: /gallery/clad/images/sphx_glr_plot_clad_03_001.png
   :alt: plot clad 03
   :srcset: /gallery/clad/images/sphx_glr_plot_clad_03_001.png
   :class: sphx-glr-single-img





.. code-block:: python3


    from FiberFusing.configuration.ring import FusedProfile_03x03 as FusedProfile

    clad = FusedProfile(
        fiber_radius=62.5,
        fusion_degree=0.3,
        index=1.4444,
        core_position_scrambling=0
    )

    figure = clad.plot()

    _ = figure.show()


    # -


.. rst-class:: sphx-glr-timing

   **Total running time of the script:** (0 minutes 1.409 seconds)


.. _sphx_glr_download_gallery_clad_plot_clad_03.py:

.. only:: html

  .. container:: sphx-glr-footer sphx-glr-footer-example




    .. container:: sphx-glr-download sphx-glr-download-python

      :download:`Download Python source code: plot_clad_03.py <plot_clad_03.py>`

    .. container:: sphx-glr-download sphx-glr-download-jupyter

      :download:`Download Jupyter notebook: plot_clad_03.ipynb <plot_clad_03.ipynb>`


.. only:: html

 .. rst-class:: sphx-glr-signature

    `Gallery generated by Sphinx-Gallery <https://sphinx-gallery.github.io>`_

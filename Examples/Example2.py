"""
2x2 Coupler
===========

.. image:: ../../images/Example2/Geometry.png
   :width: 400
   :align: center

"""

# sphinx_gallery_thumbnail_path = '../images/Example2/Geometry.png'


from FiberFusing import Geometry, Fused2, Circle, BackGround
from PyOptik import ExpData

Wavelength = 1.55e-6
index = ExpData('FusedSilica').GetRI(Wavelength)

air = BackGround(index=1.0)

clad = Fused2(fiber_radius=60, fusion_degree=0.8, index=index)

clad.Plot().Show()

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

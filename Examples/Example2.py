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
Index = ExpData('FusedSilica').GetRI(Wavelength)

Air = BackGround(index=1)

Clad = Fused2(fiber_radius=60, fusion_degree=0.6, index=Index)

Cores = [Circle(center=Core, radius=4.1, index=Index + 0.005) for Core in Clad.Cores]

Geo = Geometry(background=Air,
               clad=Clad,
               cores=Cores,
               x_bound=[-110, 0],
               y_bound=[-90, 0],
               n_x=30,
               n_y=30)

Geo.Rotate(90)

Geo.Plot().Show()


# -

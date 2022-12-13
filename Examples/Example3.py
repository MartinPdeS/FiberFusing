"""
3x3 Coupler
===========

.. image:: ../../images/Example3/Geometry.png
   :width: 400
   :align: center
"""

# sphinx_gallery_thumbnail_path = '../images/Example3/Geometry.png'

from FiberFusing import Geometry, Fused3, Circle, BackGround
from PyOptik import ExpData

Wavelength = 1.55e-6
Index = ExpData('FusedSilica').GetRI(Wavelength)

Air = BackGround(index=1)

Clad = Fused3(fiber_radius=60, fusion_degree=0.3, index=Index)

Cores = [Circle(center=Core, radius=4.1, index=Index + 0.005) for Core in Clad.Cores]

Geo = Geometry(background=Air,
               clad=Clad,
               cores=Cores,
               x_bound='auto',
               y_bound='auto',
               n_x=180,
               n_y=180)

Geo.Plot().Show()

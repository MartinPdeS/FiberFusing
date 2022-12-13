"""
1x1 Coupler
===========

.. image:: ../../images/Example1/Geometry.png
   :width: 400
   :align: center
"""

# sphinx_gallery_thumbnail_path = '../images/Example1/Geometry.png'


from FiberFusing import Geometry, Circle, BackGround
from SuPyMode.Solver import SuPySolver
from PyOptik import ExpData

Wavelength = 1.55e-6
Index = ExpData('FusedSilica').GetRI(Wavelength)

Air = BackGround(index=1) 

Clad = Circle(center=(0, 0), radius=62.5, index=Index)

Core = Circle(center=Clad.center, radius=4.1, index=Index + 0.005)

Geo = Geometry(background=Air,
               clad=Clad,
               cores=[Core],
               x_bound=[-70, 70],
               y_bound=[-70, 70],
               n_x=180,
               n_y=180)

Geo.Plot().Show()

"""
1x1 Coupler
===========

.. image:: ../../images/Example1/Geometry.png
   :width: 400
   :align: center
"""

# sphinx_gallery_thumbnail_path = '../images/Example1/Geometry.png'


from FiberFusing      import Geometry, Circle, BackGround
from SuPyMode.Solver  import SuPySolver
from PyOptik          import ExpData

Wavelength = 1.55e-6
Index = ExpData('FusedSilica').GetRI(Wavelength)

Air = BackGround(Index=1) 

Clad = Circle( Center=(0,0), Radius = 62.5, Index = Index)

Core = Circle( Center=Clad.Center, Radius = 4.1, Index = Index+0.005 )

Geo = Geometry(Objects = [Air, Clad, Core],
               Xbound  = [-70, 70],
               Ybound  = [-70, 70],
               Nx      = 180,
               Ny      = 180)

Geo.Plot().Show()

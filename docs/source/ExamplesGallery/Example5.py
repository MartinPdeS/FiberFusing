"""
7x7 Coupler
===========

.. image:: ../../images/Example5/Geometry.png
   :width: 400
   :align: center
"""

# sphinx_gallery_thumbnail_path = '../images/Example5/Geometry.png'



from FiberFusing      import Geometry, Fused7, Circle, BackGround
from SuPyMode.Solver  import SuPySolver
from PyOptik          import ExpData

Wavelength = 1.55e-6
Index = ExpData('FusedSilica').GetRI(Wavelength)

Air = BackGround(Index=1) 

Clad = Fused7(FiberRadius=62.5, Fusion=0.3, Index=Index)

Cores = [ Circle(Center=Core, Radius=4.1, Index=Index+0.005) for Core in Clad.Cores]

Geo = Geometry(Objects = [Air, Clad] + Cores,
               Xbound  = [-190, 0],
               Ybound  = [-190, 190],
               Nx      = 50,
               Ny      = 100)

Geo.Plot().Show()


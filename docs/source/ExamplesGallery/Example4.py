"""
4x4 Coupler
===========

.. image:: ../../images/Example4/Geometry.png
   :width: 400
   :align: center

"""

# sphinx_gallery_thumbnail_path = '../images/Example4/Geometry.png'


from FiberFusing      import Geometry, Fused4, Circle, BackGround
from SuPyMode.Solver  import SuPySolver
from PyOptik          import ExpData

Wavelength = 1.55e-6
Index = ExpData('FusedSilica').GetRI(Wavelength)

Air = BackGround(Index=1) 

Clad = Fused4(FiberRadius = 62.5, Fusion = 0.5, Index = Index)

Cores =  [ Circle(Center=Core, Radius=4.1, Index=Index+0.005) for Core in Clad.Cores]

Geo = Geometry(Objects = [Air, Clad] + Cores,
               Xbound  = [-150, 0],
               Ybound  = [-150, 0],
               Nx      = 80,
               Ny      = 80)

Geo.Plot().Show()

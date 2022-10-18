"""
3x3 Coupler
===========

.. image:: ../../images/Example3/Geometry.png
   :width: 400
   :align: center
"""

# sphinx_gallery_thumbnail_path = '../images/Example3/Geometry.png'



from FiberFusing      import Geometry, Fused3, Circle, BackGround
from SuPyMode.Solver  import SuPySolver
from PyOptik          import ExpData

Wavelength = 1.55e-6
Index = ExpData('FusedSilica').GetRI(Wavelength)

Air = BackGround(Index=1) 

Clad = Fused3(FiberRadius = 60, Fusion = 0.3, Index = Index)

Cores = [ Circle(Center=Core, Radius=4.1, Index=Index+0.005) for Core in Clad.Cores]

Geo = Geometry(Objects = [Air, Clad] + Cores,
               Xbound  = [-120, 120],
               Ybound  = [-100, 130],
               Nx      = 180,
               Ny      = 180)

Geo.Plot().Show()

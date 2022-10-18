"""
2x2 Coupler
===========

.. image:: ../../images/Example2/Geometry.png
   :width: 400
   :align: center

"""

# sphinx_gallery_thumbnail_path = '../images/Example2/Geometry.png'


from FiberFusing      import Geometry, Fused2, Circle, BackGround
from SuPyMode.Solver  import SuPySolver
from PyOptik          import ExpData

Wavelength = 1.55e-6
Index = ExpData('FusedSilica').GetRI(Wavelength)

Air = BackGround(Index=1) 

Clad = Fused2(FiberRadius=60, Fusion=0.6, Index=Index)

Cores = [ Circle(Center=Core, Radius=4.1, Index=Index+0.005) for Core in Clad.Cores]

Geo = Geometry(Objects = [Air, Clad] + Cores,
               Xbound  = [-110, 0],
               Ybound  = [-90, 0],
               Nx      = 20,
               Ny      = 20)

Geo.Rotate(90)

Geo.Plot().Show()




# -
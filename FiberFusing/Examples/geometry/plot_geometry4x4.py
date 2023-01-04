"""
4x4 Geometry
============
"""


from FiberFusing import Geometry, Fused4, Circle, BackGround
from PyOptik import ExpData

Wavelength = 1.55e-6
index = ExpData('FusedSilica').GetRI(Wavelength)

air = BackGround(index=1.0)

clad = Fused4(fiber_radius=60, fusion_degree=0.8, index=index)

cores = [Circle(center=core, radius=4.1, index=index + 0.005) for core in clad.cores]

geo = Geometry(background=air,
               clad=clad,
               cores=cores,
               x_bound='auto',
               y_bound='auto',
               n_x=180,
               n_y=180)

geo.plot().show()


# -

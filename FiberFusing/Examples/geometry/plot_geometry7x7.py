"""
7x7 Geometry
============
"""

from FiberFusing import Geometry, Fused7, Circle, BackGround

air = BackGround(index=1.0)

clad = Fused7(fiber_radius=60, fusion_degree=0.6, index=1.4444)

cores = [Circle(center=core, radius=4.1, index=1.4444 + 0.005) for core in clad.cores]

geo = Geometry(background=air,
               clad=clad,
               cores=cores,
               x_bound='auto',
               y_bound='auto',
               n_x=180,
               n_y=180)

geo.plot().show()


# -

"""
1x1 Geometry
============
"""

from FiberFusing import Geometry, Circle, BackGround

air = BackGround(index=1)

clad = Circle(center=(0, 0), radius=62.5, index=1.4444)

core = Circle(center=clad.center, radius=4.1, index=1.4444 + 0.005)

Geo = Geometry(background=air,
               clad=clad,
               cores=[core],
               x_bound=[-70, 70],
               y_bound=[-70, 70],
               n_x=180,
               n_y=180)

Geo.plot().show()


# -

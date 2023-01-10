"""
1x1 Clad
===========
"""


from FiberFusing._buffer import PointComposition, LineStringComposition, CircleComposition
import shapely.geometry as geo

a = geo.Point([1,3])
print(list(a))
# a = PointComposition(position=(0, 1))
# b = PointComposition(position=(0, 3))

# c = a + b
# c.rotate(angle=30)

# d = LineStringComposition(coordinates=[a, b])

# d.rotate(angle=30)


# perp = d.get_perpendicular()
# # d.plot().show()

# perp.translate(c)
# perp.make_length(length=5)
# perp.plot().show()

# print(perp.boundary)










# a = CircleComposition(center=(0, 0), radius=2)
# a.scale(factor=0.1)
# a.plot().show()
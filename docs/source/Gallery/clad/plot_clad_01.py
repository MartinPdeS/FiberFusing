"""
1x1 Ring - Clad
===============
"""


from FiberFusing import Circle

clad = Circle(
    radius=62.5e-6,
    position=(0, 0),
    index=1.4444,
)

figure = clad.plot()

_ = figure.show()

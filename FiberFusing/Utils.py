


from shapely.ops import nearest_points

import FiberFusing.Buffer as Buffer 




def NearestPoints(Object0, Object1):
    if isinstance(Object0, Buffer.Polygon ):
        P = nearest_points(Object0.exterior, Object1.exterior)
        return Buffer.Point(P[0])


def Union(*Objects):
    Output = Buffer.Polygon()
    for geo in Objects:
        Output = Output.union(geo)

    return Buffer.ToBuffer(Output)


def Intersection(*Objects):
    Output = Objects[0]
    for geo in Objects[1:]:
        Output = Output.intersection(geo)

    return Buffer.ToBuffer(Output)












#



import math
from typing import Tuple
from kernel.geometry.angles import angle

Point = Tuple[float, float]  # Define Point type


def distance_2points(p1: Point, p2: Point):
    x1, y1 = p1
    x2, y2 = p2
    # distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    distance = math.dist((x1, y1), (x2, y2))
    return distance


def point_on_line(p1: Point, p2: Point, t):  # t is between 0 and 1:( t = 0 → at p1 , t = 0.5 → midpoint ,t = 1 → at p2)
    x1, y1 = p1
    x2, y2 = p2
    return x1 + t*(x2 - x1), y1 + t*(y2 - y1)


def point_on_line_dist(surface_startpoint: Point, surface_endpoint: Point, distance):
    x_surface_startpoint, y_surface_startpoint = surface_startpoint
    angle_rad = angle(surface_endpoint, surface_startpoint, False)
    d = distance
    x_new = x_surface_startpoint+d*math.cos(angle_rad)
    y_new = y_surface_startpoint+d*math.sin(angle_rad)

    x_new = round(x_new, 2)
    y_new = round(y_new, 2)

    return x_new, y_new


def midpoint(p1: Point, p2: Point):
    x1, y1 = p1
    x2, y2 = p2
    return (x1 + x2) / 2, (y1 + y2) / 2

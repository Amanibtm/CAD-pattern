import math
from typing import Tuple

Point = Tuple[float, float]  # Define Point type
Vector = Tuple[float, float]


def angle(point1: Point, point2: Point, degree=True):
    x1, y1 = point1
    x2, y2 = point2

    dx = x2 - x1
    dy = y2 - y1

    angle_rad = math.atan2(dy, dx)
    angle_deg = math.degrees(angle_rad)

    # Make angle between 0° and 360°
    if angle_deg < 0:
        angle_deg += 360

    if degree:
        return angle_deg
    return angle_rad


def angle_diff(a, b):
    # smallest signed difference a - b in [-pi, pi]
    d = (a - b + math.pi) % (2*math.pi) - math.pi
    return d


def direction_from_angle(angle_degree):
    theta = math.radians(angle_degree)   # 30 degrees
    direct = (math.cos(theta), math.sin(theta))
    return direct


def direction(P1: Point, P2: Point) -> Vector:
    dx = P2[0] - P1[0]
    dy = P2[1] - P1[1]
    L = math.hypot(dx, dy)
    return dx / L, dy / L

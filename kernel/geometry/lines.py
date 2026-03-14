import math
from typing import Tuple

Point = Tuple[float, float]


def calculate_line_endpoint(start: Point, distance: float, angle_deg: float) -> Point:
    """Pure math: calculate endpoint from start, distance, angle"""
    x, y = start
    angle_rad = math.radians(angle_deg)

    x_end = x + distance * math.cos(angle_rad)
    y_end = y + distance * math.sin(angle_rad)

    return round(x_end, 2), round(y_end, 2)


def calculate_perpendicular_points(center: Point, distance: float, angle_deg: float) -> Tuple[Point, Point]:
    """Pure math: calculate points at ±90° from center"""
    x, y = center
    angle_rad = math.radians(angle_deg)

    # Right point (-90°)
    x_right = x + distance * math.cos(angle_rad - math.pi / 2)
    y_right = y + distance * math.sin(angle_rad - math.pi / 2)

    # Left point (+90°)
    x_left = x + distance * math.cos(angle_rad + math.pi / 2)
    y_left = y + distance * math.sin(angle_rad + math.pi / 2)

    return (
        (round(x_right, 2), round(y_right, 2)),
        (round(x_left, 2), round(y_left, 2))
    )

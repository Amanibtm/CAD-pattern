from typing import Tuple

Point = Tuple[float, float]
Vector = Tuple[float, float]


def move_point_by_direction(startpoint, distance, direction: Vector) -> Point:
    x, y = startpoint
    dx, dy = direction   # MUST be unit vector

    x_new = x + distance * dx
    y_new = y + distance * dy

    x_new = round(x_new, 2)
    y_new = round(y_new, 2)

    return x_new, y_new

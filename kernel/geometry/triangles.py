import math
from kernel.geometry.angles import angle_diff, angle

from typing import Tuple
Point = Tuple[float, float]


def triangle_apex(A: Point, B: Point, length_AC, length_BC) -> Tuple[Point, Point]:
    Ax, Ay = A
    Bx, By = B

    # Step 1: distance between A and B
    dx = Bx - Ax
    dy = By - Ay
    d = math.hypot(dx, dy)

    # Impossible triangle check
    if d == 0:
        raise ValueError("A and B cannot be the same point.")
    if d > length_AC + length_BC:
        raise ValueError("Triangle impossible: sides too short.")
    if d < abs(length_AC - length_BC):
        raise ValueError("Triangle impossible: one side too long.")

    # Step 2: unit direction from A to B
    ux = dx / d
    uy = dy / d

    # Step 3: projection length
    x = (length_AC**2 - length_BC**2 + d**2) / (2*d)

    # Step 4: height
    h = math.sqrt(max(length_AC**2 - x**2, 0))

    # Step 5: point on AB at distance x from A
    Px = Ax + ux * x
    Py = Ay + uy * x

    # Step 6: perpendicular direction
    perp_x = -uy
    perp_y = ux

    # Two possible apex points
    C1 = (Px + perp_x * h, Py + perp_y * h)
    C2 = (Px - perp_x * h, Py - perp_y * h)

    return C1, C2


def perpendicular_to_bisector_toward_direction(
    bis_p1, bis_p2,      # two points defining bisector line (tuples)
    dir_p1, dir_p2,      # two points defining direction line (tuples)
    origin=None,         # point where perpendicular starts; if None use midpoint of bisector
    length=1.0           # length of the produced perpendicular line (same units as coords)
):
    """
    Returns (origin_point, end_point, chosen_angle_deg).
    The returned line is perpendicular to the bisector and points toward the direction line.
    """

    # safety checks
    if bis_p1 == bis_p2:
        raise ValueError("bisector points must not be identical")
    if dir_p1 == dir_p2:
        raise ValueError("direction line points must not be identical")

    # angles (radians)
    angle_bis = angle(bis_p1, bis_p2, False)
    angle_dir = angle(dir_p1, dir_p2, False)

    # two perpendicular candidates
    p1 = angle_bis + math.pi/2
    p2 = angle_bis - math.pi/2

    # choose candidate whose absolute angular difference to angle_dir is smaller
    d1 = abs(angle_diff(p1, angle_dir))
    d2 = abs(angle_diff(p2, angle_dir))
    chosen = p1 if d1 <= d2 else p2

    # choose origin
    if origin is None:
        origin = ((bis_p1[0] + bis_p2[0]) / 2.0, (bis_p1[1] + bis_p2[1]) / 2.0)

    # compute end point
    ex = origin[0] + length * math.cos(chosen)
    ey = origin[1] + length * math.sin(chosen)

    chosen_deg = math.degrees(chosen) % 360

    return origin, (ex, ey), chosen_deg

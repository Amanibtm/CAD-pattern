from kernel.constants import left
from kernel.geometry.lines import calculate_line_endpoint
from services.json.operations import add_line  # Keep JSON separate

from typing import Tuple

Point = Tuple[float, float]
Vector = Tuple[float, float]


def line_dist_deg(ctx, startpoint: Point, distance: float, angle_deg: float):
    """Legacy Cairo adapter"""
    # Use pure math
    endpoint = calculate_line_endpoint(startpoint, distance, angle_deg)

    # Drawing
    ctx.new_sub_path()
    ctx.move_to(*startpoint)
    ctx.line_to(*endpoint)
    ctx.stroke()

    # JSON saving (separate concern)
    add_line(startpoint, endpoint)

    return endpoint


def line(ctx, startpoint: Point, endpoint: Point):
    x_start, y_start = startpoint
    x_end, y_end = endpoint
    ctx.new_sub_path()
    ctx.move_to(x_start, y_start)
    ctx.line_to(x_end, y_end)
    ctx.stroke()
    json_return = add_line((x_start, y_start), (x_end, y_end))
    return json_return


def bezier_curve(ctx, startpoint: Point, endpoint: Point, width: float = None, leg_side: str = left,
                 drop_p1: float = 0.3, drop_p2: float = 0.7, entry_p1: float = 0.5, entry_p2: float = 1) -> Tuple[Point, Point]:
    """Legacy Cairo adapter for bezier_curve"""
    from kernel.curves.bezier_construction import calculate_bezier_control_points
    from services.json.operations import add_cubic_bezier

    # Use pure math
    ctrl1, ctrl2 = calculate_bezier_control_points(
        startpoint, endpoint, width, leg_side, drop_p1, drop_p2, entry_p1, entry_p2
    )

    # Drawing
    ctx.new_sub_path()
    ctx.move_to(*startpoint)
    ctx.curve_to(*ctrl1, *ctrl2, *endpoint)
    ctx.stroke()

    # JSON saving
    add_cubic_bezier(startpoint, ctrl1, ctrl2, endpoint)

    return ctrl1, ctrl2


def circle(ctx, cc: Point, radius: float, angle1: float, angle2: float):  # radius in points , and angles in radians
    ctx.new_sub_path()
    x_cc, y_cc = cc
    ctx.arc(x_cc, y_cc, radius, angle1, angle2)
    ctx.stroke()


def sides_90(ctx, startpoint: Point, dart_width: float, bisector_angle: float, draw=True) -> Tuple[Point, Point]:
    """Legacy Cairo adapter for sides_90"""
    from kernel.geometry.lines import calculate_perpendicular_points

    # Use pure math
    right_point, left_point = calculate_perpendicular_points(
        startpoint, dart_width, bisector_angle
    )
    ctx.new_sub_path()
    if draw:
        line(ctx, startpoint, right_point)
        line(ctx, startpoint, left_point)
        ctx.stroke()

    return right_point, left_point

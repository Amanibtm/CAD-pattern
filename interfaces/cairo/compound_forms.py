import cairo
from kernel.constants import right
from typing import List, Tuple

from kernel.curves.bezier_construction import compound_wavy_curve_math, calculate_bezier_control_points

Point = Tuple[float, float]


def compound_wavy_curve_draw(ctx: cairo.Context, startpoint: Point, endpoint: Point, first_side: str = right,
                             first_side_width: float = 1.5, second_side_width: float = 1.5) -> List[List[List[Point]]]:

    curve_data = compound_wavy_curve_math(startpoint, endpoint, first_side, first_side_width, second_side_width)

    curves = []
    first_dart = curve_data['first_semi_dart']
    second_dart = curve_data['second_semi_dart']

    # Draw first dart - NO NEED TO CHECK FOR None VALUES!
    leg_point = first_dart['right_leg'] if curve_data['sides']['first_side'] == right else first_dart['left_leg']
    side = curve_data['sides']['first_side']

    # Calculate and draw Bezier curve
    ctrl1, ctrl2 = calculate_bezier_control_points(first_dart['start_point'], leg_point,
                                                   width=first_side_width, leg_side=side)
    ctrl1_closed, ctrl2_closed = calculate_bezier_control_points(first_dart['close_point'], leg_point,
                                                                 width=first_side_width, leg_side=side)

    ctx.move_to(*first_dart['start_point'])
    ctx.curve_to(*ctrl1, *ctrl2, *leg_point)

    ctx.move_to(*leg_point)
    ctx.curve_to(*ctrl2_closed, *ctrl1_closed, *first_dart['close_point'])

    curves.append([[first_dart['start_point'], ctrl1, ctrl2, leg_point],
                   [leg_point, ctrl2_closed, ctrl1_closed, first_dart['close_point']]])

    # Draw second dart
    leg_point = second_dart['right_leg'] if curve_data['sides']['second_side'] == right else second_dart['left_leg']
    side = curve_data['sides']['second_side']

    # Calculate and draw Bezier curve
    ctrl1, ctrl2 = calculate_bezier_control_points(second_dart['start_point'], leg_point,
                                                   width=second_side_width, leg_side=side)
    ctrl1_closed, ctrl2_closed = calculate_bezier_control_points(second_dart['close_point'], leg_point,
                                                                 width=second_side_width, leg_side=side)

    ctx.move_to(*second_dart['start_point'])
    ctx.curve_to(*ctrl1, *ctrl2, *leg_point)

    ctx.move_to(*leg_point)
    ctx.curve_to(*ctrl2_closed, *ctrl1_closed, *second_dart['close_point'])

    curves.append([[second_dart['start_point'], ctrl1, ctrl2, leg_point],
                   [leg_point, ctrl2_closed, ctrl1_closed, second_dart['close_point']]])

    return curves

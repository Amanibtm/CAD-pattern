import math
from typing import Tuple, Dict

from kernel.geometry import midpoint, distance_2points, angle
from kernel.geometry.lines import calculate_line_endpoint, calculate_perpendicular_points
from kernel.constants import right, left

Point = Tuple[float, float]


def calculate_bezier_control_points(
        startpoint: Point, endpoint: Point, width: float = None, leg_side: str = left,
        drop_p1: float = 0.3, drop_p2: float = 0.7,
        entry_p1: float = 0.5, entry_p2: float = 1.0
) -> Tuple[Point, Point]:
    """Pure math: Calculate control points for a curved dart leg"""

    x_start, y_start = startpoint
    x_end, y_end = endpoint

    if width is None:
        dx = abs(x_end - x_start)
        dy = abs(y_end - y_start)
        width = dx if dx <= dy else dy

    # Calculate line angle
    angle_rad = math.atan2(y_end - y_start, x_end - x_start)
    line_angle = math.degrees(angle_rad)

    # Calculate bisector point
    if leg_side == right:
        degree_bisector = line_angle + 90
        degree_side = line_angle - 90
    else:  # left
        degree_bisector = line_angle - 90
        degree_side = line_angle + 90

    # Calculate bisector endpoint
    x_bisectorend, y_bisectorend = calculate_line_endpoint((x_end, y_end), width, degree_bisector)

    # Calculate bisector angle and length
    bisector_angle_rad = math.atan2(y_bisectorend - y_start, x_bisectorend - x_start)
    bisector_angle = math.degrees(bisector_angle_rad)
    bisector_length = math.dist((x_start, y_start), (x_bisectorend, y_bisectorend))

    # Calculate control points
    # First control point
    vert_x1, vert_y1 = calculate_line_endpoint((x_start, y_start), bisector_length * drop_p1, bisector_angle)
    ctrl1 = calculate_line_endpoint((vert_x1, vert_y1), width * entry_p1, degree_side)

    # Second control point
    vert_x2, vert_y2 = calculate_line_endpoint((x_start, y_start), bisector_length * drop_p2, bisector_angle)
    ctrl2 = calculate_line_endpoint((vert_x2, vert_y2), width * entry_p2, degree_side)

    return ctrl1, ctrl2


def curst_darts_math(startpoint: Point, dart_width: float, bisector_angle: float, len_dart: float,
                     right_leg: bool = True, left_leg: bool = True, close_dart: bool = True) -> dict:
    """
    Calculate straight dart points mathematically.
    """
    # Calculate bisector point
    x_bisector, y_bisector = calculate_line_endpoint(startpoint, len_dart, bisector_angle)

    # Calculate leg points
    (x_right_leg, y_right_leg), (x_left_leg, y_left_leg) = calculate_perpendicular_points(
        (x_bisector, y_bisector), dart_width, bisector_angle)

    result = {
        'start_point': startpoint,
        'bisector_point': (x_bisector, y_bisector),
        'right_leg': (x_right_leg, y_right_leg) if right_leg else None,
        'left_leg': (x_left_leg, y_left_leg) if left_leg else None,
        'close_point': None
    }

    if close_dart:
        length = distance_2points(startpoint, (x_bisector, y_bisector))
        x_close, y_close = calculate_line_endpoint((x_bisector, y_bisector), length, bisector_angle)
        result['close_point'] = (x_close, y_close)

    return result


def clean_none_values(data_dict: Dict) -> Dict:
    """Remove keys with None values from dictionary."""
    return {key: value for key, value in data_dict.items() if value is not None}


def compound_wavy_curve_math(startpoint: Point, endpoint: Point, first_side: str = right, first_side_width: float = 1.5,
                             second_side_width: float = 1.5) -> Dict[str, any]:
    """
    Calculate compound wavy curve using darts.
    """
    # Determine sides
    second_side = left if first_side == right else right

    # Calculate key points
    middlepoint = midpoint(startpoint, endpoint)
    quarterpoint = midpoint(startpoint, middlepoint)

    quarter_dist = distance_2points(startpoint, quarterpoint)
    quarter_angle = angle(startpoint, quarterpoint)

    # Calculate darts
    first_semi_dart = curst_darts_math(startpoint, first_side_width, quarter_angle, quarter_dist,
                                       right_leg=(first_side == right),
                                       left_leg=(first_side == left),
                                       close_dart=True)

    second_semi_dart = curst_darts_math(middlepoint, second_side_width, quarter_angle, quarter_dist,
                                        right_leg=(second_side == right),
                                        left_leg=(second_side == left),
                                        close_dart=True)

    # Create continuous curve points + Remove None points
    first_cleaned_semi_dart = clean_none_values(first_semi_dart)
    second_cleaned_semi_dart = clean_none_values(second_semi_dart)

    return {
        'first_semi_dart': first_cleaned_semi_dart,
        'second_semi_dart': second_cleaned_semi_dart,
        'key_points': {
            'middlepoint': middlepoint,
            'quarterpoint': quarterpoint,
            'quarter_dist': quarter_dist,
            'quarter_angle': quarter_angle
        },
        'sides': {
            'first_side': first_side,
            'second_side': second_side
        }
    }


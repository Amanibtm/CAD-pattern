"""
Pure mathematical dart calculations with NO drawing dependencies.

This module contains:
- Geometry calculations for various dart types
- Point coordinate computations
- Mathematical transformations

All functions return data structures (tuples, dicts) without any drawing.
Use with any rendering backend (Cairo, matplotlib, SVG, etc.).

"""

import math
from typing import Tuple, List, Optional, Dict
from kernel.curves import point_at_distance_cubic
from kernel.geometry import (
    angle, distance_2points, triangle_apex,
    calculate_line_endpoint,
    point_on_line_dist as math_point_on_line_dist,
    calculate_perpendicular_points
)
from kernel.constants import right

Point = Tuple[float, float]
BezierCurve = Tuple[Point, Point, Point, Point]


def princess_dart_math(
        circle_center_point: Point,
        radius: float,
        bisector_angle: float,
        startpoint_distance_from_circle_center: float,
        dart_width: float,
        len_dart: Optional[float] = None,
        right_dart: bool = True,
        left_dart: bool = True
) -> dict:
    """
    Calculate princess dart points mathematically.
    Returns a dictionary of calculated points.
    """
    x_cc, y_cc = circle_center_point

    # Calculate start point
    x_start, y_start = calculate_line_endpoint((x_cc, y_cc), startpoint_distance_from_circle_center, bisector_angle)

    # Calculate bisector end point
    x_end_bisector, y_end_bisector = calculate_line_endpoint((x_cc, y_cc), radius, bisector_angle)

    # Calculate triangle geometry
    hypotenuse = radius
    adjacent = dart_width
    opposite = math.sqrt(hypotenuse ** 2 - adjacent ** 2)

    # Calculate right and left dart points
    (x_right_dart_len, y_right_dart_len), (x_left_dart_len, y_left_dart_len) = calculate_perpendicular_points(
        circle_center_point, dart_width, bisector_angle)

    x_right_dart, y_right_dart = calculate_line_endpoint((x_right_dart_len, y_right_dart_len), opposite, bisector_angle)
    x_left_dart, y_left_dart = calculate_line_endpoint((x_left_dart_len, y_left_dart_len), opposite, bisector_angle)

    # Calculate waist points if len_dart is provided
    result = {
        'start_point': (x_start, y_start),
        'bisector_end': (x_end_bisector, y_end_bisector),
        'right_dart': (x_right_dart, y_right_dart) if right_dart else None,
        'left_dart': (x_left_dart, y_left_dart) if left_dart else None,
        'right_dart_to_waist': None,
        'left_dart_to_waist': None,
        'waist_end': None
    }

    if len_dart:
        x_waist_end, y_waist_end = calculate_line_endpoint((x_start, y_start), len_dart, bisector_angle)
        result['waist_end'] = (x_waist_end, y_waist_end)

        if right_dart:
            (x_right_waist, y_right_waist), _ = calculate_perpendicular_points(
                (x_waist_end, y_waist_end), dart_width, bisector_angle)
            result['right_dart_to_waist'] = (x_right_waist, y_right_waist)

        if left_dart:
            _, (x_left_waist, y_left_waist) = calculate_perpendicular_points(
                (x_waist_end, y_waist_end), dart_width, bisector_angle)
            result['left_dart_to_waist'] = (x_left_waist, y_left_waist)

    return result


def curst_darts_math(
        startpoint: Point,
        dart_width: float,
        bisector_angle: float,
        len_dart: float,
        right_leg: bool = True,
        left_leg: bool = True,
        close_dart: bool = True
) -> dict:
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


def curst_darts_ready_points_math(
        startpoint: Point,
        bisector_point: Point,
        right_leg_point: Optional[Point] = None,
        left_leg_point: Optional[Point] = None,
        close_dart: bool = True
) -> Tuple[Optional[Point], float, Optional[float], Optional[float], Optional[float], Optional[float], Optional[float], Optional[float]]:
    """
    Calculate dart points when leg points are already known.
    Returns:

    (close_point, bisector_angle, x_right_leg, y_right_leg, x_left_leg, y_left_leg, right_leg_width, left_leg_width)
    """
    if right_leg_point is None and left_leg_point is None:
        raise ValueError("Dart requires at least one leg point!")

    bisector_angle = angle(startpoint, bisector_point)

    x_right_leg = y_right_leg = x_left_leg = y_left_leg = None
    right_leg_width = left_leg_width = None

    if right_leg_point:
        x_right_leg, y_right_leg = right_leg_point
        right_leg_width = distance_2points(bisector_point, right_leg_point)

    if left_leg_point:
        x_left_leg, y_left_leg = left_leg_point
        left_leg_width = distance_2points(bisector_point, left_leg_point)

    close_point = None
    if close_dart:
        length_from_startpoint = distance_2points(startpoint, bisector_point)
        close_point = calculate_line_endpoint(bisector_point, length_from_startpoint, bisector_angle)

    return close_point, bisector_angle, x_right_leg, y_right_leg, x_left_leg, y_left_leg, right_leg_width, left_leg_width


def curved_surface_dart_root_points_by_distance(
        surface_startpoint: Point,
        p1: Point,
        p2: Point,
        surface_endpoint: Point,
        distance_from_startpoint: float,
        dart_width: float,
        mono: bool = False,
        if_mono_which_side: str = right
) -> Tuple[Point, Point, Point] | Tuple[Point, Point]:
    """
    Calculate dart root points on a curved surface.
    """
    if distance_from_startpoint < 0:
        raise ValueError("Distance from start point should not be negative")

    distance_in_points = distance_from_startpoint
    dart_width_in_points = dart_width

    # Get bisector point
    bisector_point, _ = point_at_distance_cubic(surface_startpoint, p1, p2, surface_endpoint, distance_in_points)

    if not mono:
        # Symmetric dart
        right_leg, _ = point_at_distance_cubic(
            surface_startpoint, p1, p2, surface_endpoint, distance_in_points - (dart_width_in_points / 2))
        left_leg, _ = point_at_distance_cubic(
            surface_startpoint, p1, p2, surface_endpoint, distance_in_points + (dart_width_in_points / 2))
        return bisector_point, right_leg, left_leg
    else:
        # Mono dart
        if if_mono_which_side == right:
            right_leg, _ = point_at_distance_cubic(
                surface_startpoint, p1, p2, surface_endpoint, distance_in_points + dart_width_in_points)
            return bisector_point, right_leg
        else:
            left_leg, _ = point_at_distance_cubic(
                surface_startpoint, p1, p2, surface_endpoint, distance_in_points - dart_width_in_points)
            return bisector_point, left_leg


def straight_surface_dart_root_points_by_distance(
        surface_startpoint: Point,
        surface_endpoint: Point,
        distance_from_startpoint: float,
        dart_width: float,
        mono: bool = False,
        if_mono_which_side: str = right
) -> Tuple[Point, Point, Point] | Tuple[Point, Point]:
    """
    Calculate dart root points on a straight surface.
    """
    if distance_from_startpoint < 0:
        raise ValueError("Distance from start point should not be negative")

    # Get bisector point
    bisector_point = math_point_on_line_dist(
        surface_startpoint, surface_endpoint, distance_from_startpoint
    )

    if not mono:
        # Symmetric dart
        right_leg = math_point_on_line_dist(
            surface_startpoint, surface_endpoint, distance_from_startpoint - (dart_width / 2))
        left_leg = math_point_on_line_dist(
            surface_startpoint, surface_endpoint, distance_from_startpoint + (dart_width / 2))
        return bisector_point, right_leg, left_leg
    else:
        # Mono dart
        if if_mono_which_side == right:
            right_leg = math_point_on_line_dist(
                surface_startpoint, surface_endpoint, distance_from_startpoint + dart_width)
            return bisector_point, right_leg
        else:
            left_leg = math_point_on_line_dist(
                surface_startpoint, surface_endpoint, distance_from_startpoint - dart_width)
            return bisector_point, left_leg


def dart_root_math(
        firstpoint: Point,
        middlepoint: Point,
        secondpoint: Point,
        bisector_firstpoint: Point,
        height: Optional[float] = None
) -> Point:
    """
    Calculate dart root triangle summit mathematically.
    """
    A = firstpoint
    B = secondpoint
    M = middlepoint

    # Compute bisector angle
    bisector_angle = angle(bisector_firstpoint, M)

    if height is not None:
        # Use specified height
        return calculate_line_endpoint(M, height, bisector_angle)

    # Compute using triangle geometry
    AC = distance_2points(A, M) + 1
    BC = distance_2points(B, M) + 1

    # Get possible apex points
    C1, C2 = triangle_apex(A, B, AC, BC)

    # Choose the one closer to bisector angle
    angle_C1 = angle(M, C1)
    angle_C2 = angle(M, C2)

    error1 = abs(angle_C1 - bisector_angle)
    error2 = abs(angle_C2 - bisector_angle)

    return C1 if error1 < error2 else C2


def tree_dart_math(
        startpoint: Point,
        endpoint: Point,
        curves_number: int,
        distance: float,
        curves_side: str = right
) -> List[Point]:
    """
    Calculate tree dart points mathematically.
    """
    bisector_angle_deg = angle(startpoint, endpoint)
    all_curves_points = []

    for i in range(curves_number):
        dist = distance * (i + 1)
        right_point, left_point = calculate_perpendicular_points(endpoint, dist, bisector_angle_deg)

        if curves_side == right:
            curve_endpoint = right_point
        else:
            curve_endpoint = left_point

        all_curves_points.append(curve_endpoint)

    return all_curves_points


def slated_dart_points_math(
    startpoint: Point,
    endpoint: Optional[Point] = None,
    right_leg_point: Optional[Point] = None,
    left_leg_point: Optional[Point] = None
) -> Dict[str, Optional[Point]]:
    """
    Calculate slated dart points mathematically.
    Returns dictionary of points.
    """
    return {
        'start_point': startpoint,
        'endpoint': endpoint,
        'right_leg_point': right_leg_point,
        'left_leg_point': left_leg_point
    }

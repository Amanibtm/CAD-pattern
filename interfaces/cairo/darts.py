"""
Cairo-specific dart drawing implementations.

This module:
- Takes mathematical results from `core.py`
- Uses Cairo Context to render darts
- Handles Cairo-specific operations (paths, strokes, fills)

Dependencies: cairo, domain.darts.core, kernel.geometry;
"""
from typing import Optional, List
import cairo
from kernel.constants import right, left
from domain.darts.core import princess_dart_math, curst_darts_math, Point, curst_darts_ready_points_math
# Import drawing functions from your cairo interface
from .drawing import line, bezier_curve, sides_90


def princess_dart_draw(
        ctx: cairo.Context,
        circle_center_point: Point,
        radius: float,
        bisector_angle: float,
        startpoint_distance_from_circle_center: float,
        dart_width: float,
        len_dart: Optional[float] = None,
        right_dart: bool = True,
        left_dart: bool = True,
        draw_dart: bool = True,
        close_dart: bool = True
) -> dict:
    """
    Draw a princess dart using Cairo.
    """
    ctx.new_sub_path()

    # Calculate points
    points = princess_dart_math(
        circle_center_point, radius, bisector_angle,
        startpoint_distance_from_circle_center, dart_width,
        len_dart, right_dart, left_dart
    )

    # Draw dart if requested
    if draw_dart:
        if right_dart and points['right_dart']:
            line(ctx, points['start_point'], points['right_dart'])
        if left_dart and points['left_dart']:
            line(ctx, points['start_point'], points['left_dart'])

    # Draw waist connection if needed
    if close_dart and len_dart:
        if right_dart and points['right_dart_to_waist']:
            line(ctx, points['right_dart_to_waist'], points['right_dart'])
        if left_dart and points['left_dart_to_waist']:
            line(ctx, points['left_dart_to_waist'], points['left_dart'])

    return points


def curst_darts_draw(
        ctx: cairo.Context,
        startpoint: Point,
        dart_width: float,
        bisector_angle: float,
        len_dart: float,
        right_leg: bool = True,
        left_leg: bool = True,
        close_dart: bool = True,
        curvy: bool = False,
        drop_p1: float = 0.3,
        drop_p2: float = 0.7,
        entry_p1: float = 0.5,
        entry_p2: float = 1.0
) -> dict:
    """
    Draw straight or curvy darts using Cairo.
    """
    ctx.new_sub_path()
    curves = []

    # Calculate points
    points = curst_darts_math(
        startpoint, dart_width, bisector_angle, len_dart,
        right_leg, left_leg, close_dart
    )

    if not curvy:
        # Draw straight lines
        if right_leg and points['right_leg']:
            line(ctx, startpoint, points['right_leg'])
            if close_dart and points['close_point']:
                line(ctx, points['right_leg'], points['close_point'])

        if left_leg and points['left_leg']:
            line(ctx, startpoint, points['left_leg'])
            if close_dart and points['close_point']:
                line(ctx, points['left_leg'], points['close_point'])
    else:
        # Draw curvy bezier curves
        if right_leg and points['right_leg']:
            control1, control2 = bezier_curve(ctx, startpoint, points['right_leg'], dart_width,
                                              right, drop_p1, drop_p2, entry_p1, entry_p2)
            curves.append([startpoint, control1, control2, points['right_leg']])

            if close_dart and points['close_point']:
                control1_closed, control2_closed = bezier_curve(ctx, points['close_point'], points['right_leg'], dart_width,
                                                                left, drop_p1, drop_p2, entry_p1, entry_p2)
                curves.append([points['right_leg'], control2_closed, control1_closed, points['close_point']])

        if left_leg and points['left_leg']:
            control1, control2 = bezier_curve(ctx, startpoint, points['left_leg'], dart_width,
                                              left, drop_p1, drop_p2, entry_p1, entry_p2)
            curves.append([startpoint, control1, control2, points['left_leg']])

            if close_dart and points['close_point']:
                control1_closed, control2_closed = bezier_curve(ctx, points['close_point'], points['left_leg'], dart_width,
                                                                right, drop_p1, drop_p2, entry_p1, entry_p2)
                curves.append([points['left_leg'], control2_closed, control1_closed, points['close_point']])

    return {
        'points': points,
        'curves': curves if curvy else None
    }


def curst_darts_ready_points_draw(
        ctx: cairo.Context,
        startpoint: Point,
        bisector_point: Point,
        right_leg_point: Optional[Point] = None,
        left_leg_point: Optional[Point] = None,
        close_dart: bool = True,
        curvy: bool = False,
        drop_p1: float = 0.3,
        drop_p2: float = 0.7,
        entry_p1: float = 0.5,
        entry_p2: float = 1.0
) -> Point | List:
    """
    Draw darts when leg points are already known.
    Returns either the close point (if not curvy) or list of curves (if curvy).
    """
    curves = []

    ctx.new_sub_path()

    # Draw bisector
    line(ctx, startpoint, bisector_point)

    # Get the math calculations
    (
        close_point,
        bisector_angle,
        x_right_leg, y_right_leg,
        x_left_leg, y_left_leg,
        right_leg_width,
        left_leg_width
    ) = curst_darts_ready_points_math(startpoint, bisector_point, right_leg_point, left_leg_point, close_dart)

    if not curvy:
        # Draw straight lines
        if right_leg_point:
            line(ctx, startpoint, right_leg_point)
            if close_dart and close_point:
                line(ctx, right_leg_point, close_point)

        if left_leg_point:
            line(ctx, startpoint, left_leg_point)
            if close_dart and close_point:
                line(ctx, left_leg_point, close_point)

        # Return close point (matching original function)
        return close_point

    else:
        # Draw curvy bezier curves
        if right_leg_point:
            control_points1_right, control_points2_right = bezier_curve(
                ctx, startpoint, right_leg_point, right_leg_width,
                right, drop_p1, drop_p2, entry_p1, entry_p2
            )
            right_leg_curve = [startpoint, control_points1_right, control_points2_right, right_leg_point]
            curves.append(right_leg_curve)

            if close_dart and close_point:
                control_points1_closed_right, control_points2_closed_right = bezier_curve(
                    ctx, close_point, right_leg_point, right_leg_width,
                    left, drop_p1, drop_p2, entry_p1, entry_p2
                )
                right_closed_leg_curve = [
                    right_leg_point, control_points2_closed_right, control_points1_closed_right, close_point
                ]
                curves.append(right_closed_leg_curve)

        if left_leg_point:
            control_points1_left, control_points2_left = bezier_curve(
                ctx, startpoint, left_leg_point, left_leg_width,
                left, drop_p1, drop_p2, entry_p1, entry_p2
            )
            left_leg_curve = [startpoint, control_points1_left, control_points2_left, left_leg_point]
            curves.append(left_leg_curve)

            if close_dart and close_point:
                control_points1_closed_left, control_points2_closed_left = bezier_curve(
                    ctx, close_point, left_leg_point, left_leg_width,
                    right, drop_p1, drop_p2, entry_p1, entry_p2
                )
                left_closed_leg_curve = [
                    left_leg_point, control_points2_closed_left, control_points1_closed_left, close_point
                ]
                curves.append(left_closed_leg_curve)

        # Return list of curves (matching original function)
        return curves


def slated_dart_points_draw(
        ctx: cairo.Context,
        startpoint: Point,
        endpoint: Optional[Point] = None,
        right_leg_point: Optional[Point] = None,
        left_leg_point: Optional[Point] = None,
        legs_side: str = left,
        drop_p1: float = 0.3,
        drop_p2: float = 0.7,
        entry_p1: float = 0.5,
        entry_p2: float = 1.0
) -> None:
    """
    Draw slated dart points using Cairo.
    """
    if endpoint:
        bezier_curve(ctx, startpoint, endpoint, 2, legs_side, drop_p1, drop_p2, entry_p1, entry_p2)
    if right_leg_point:
        bezier_curve(ctx, startpoint, right_leg_point, 2, legs_side, drop_p1, drop_p2, entry_p1, entry_p2)
    if left_leg_point:
        bezier_curve(ctx, startpoint, left_leg_point, 2, legs_side, drop_p1, drop_p2, entry_p1, entry_p2)


def tree_dart_draw(
        ctx: cairo.Context,
        startpoint: Point,
        endpoint: Point,
        curves_number: int,
        distance: float,
        curves_side: str = right,
        legs_side: str = left,
        drop_p1: float = 0.3,
        drop_p2: float = 0.7,
        entry_p1: float = 0.5,
        entry_p2: float = 1.0
) -> List[Point]:
    """
    Draw tree dart using Cairo.
    Returns list of curve endpoints.
    """
    from kernel.geometry import angle

    bisector_angle_deg = angle(startpoint, endpoint)
    all_curves_points = []

    for i in range(curves_number):
        dist = distance * (i + 1)
        right_point, left_point = sides_90(ctx, endpoint, dist, bisector_angle_deg)

        if curves_side == right:
            curve_endpoint = right_point
        else:
            curve_endpoint = left_point

        all_curves_points.append(curve_endpoint)

        # Draw the bezier curve
        bezier_curve(
            ctx, startpoint, curve_endpoint, distance,
            legs_side, drop_p1, drop_p2, entry_p1, entry_p2
        )

    return all_curves_points


def dart_root_draw(
        ctx: cairo.Context,
        firstpoint: Point,
        middlepoint: Point,
        secondpoint: Point,
        bisector_firstpoint: Point,
        height: Optional[float] = None,
        draw: bool = False
) -> Point:
    """
    Draw dart root triangle using Cairo.
    """
    from domain.darts.core import dart_root_math

    # Calculate summit point
    summit = dart_root_math(
        firstpoint, middlepoint, secondpoint,
        bisector_firstpoint, height
    )

    # Draw if requested
    if draw:
        line(ctx, firstpoint, summit)
        line(ctx, secondpoint, summit)
        line(ctx, middlepoint, summit)

    return summit

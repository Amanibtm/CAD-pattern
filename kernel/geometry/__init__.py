"""
Pure geometry functions - no drawing, no side effects.
"""

from .angles import angle, angle_diff, direction_from_angle, direction
from .basic import distance_2points, point_on_line, point_on_line_dist, midpoint
from .division import divider
from .lines import calculate_line_endpoint, calculate_perpendicular_points
from .triangles import triangle_apex, perpendicular_to_bisector_toward_direction
from .units import cm_to_points, inch_to_points, points_to_cm, points_to_inch
from .vectors import move_point_by_direction

__all__ = [
    # From angles module
    'angle',
    'angle_diff',
    'direction_from_angle',
    'direction',

    # From basic module
    'distance_2points',
    'point_on_line',
    'point_on_line_dist',
    'midpoint',

    # From division module
    'divider',

    # From lines module
    'calculate_line_endpoint',
    'calculate_perpendicular_points',

    # From triangles module
    'triangle_apex',
    'perpendicular_to_bisector_toward_direction',

    # From units module
    'cm_to_points',
    'inch_to_points',
    'points_to_cm',
    'points_to_inch',

    # From vectors module
    'move_point_by_direction',
]

"""
Pure curve mathematics - Bezier-curves, splines, etc.
"""

from .bezier import (point_on_cubic_bezier, tangent_angle_degrees_cubic, tangent_vector_cubic,
                     tangent_unit_vector_cubic, _build_length_table, point_at_distance_cubic, split_cubic_bezier,
                     split_one_cubic_into_n, split_multiple_united_curves, multiple_curves_length,
                     curve_local_coordinate_representation, rebuild_curve_from_local, arc_length_simpson)

from .bezier_construction import calculate_bezier_control_points

__all__ = ['point_on_cubic_bezier', 'tangent_vector_cubic', 'tangent_unit_vector_cubic', 'tangent_angle_degrees_cubic',
           '_build_length_table', 'point_at_distance_cubic', 'split_cubic_bezier', 'split_one_cubic_into_n',
           'split_multiple_united_curves', 'multiple_curves_length', 'curve_local_coordinate_representation',
           'rebuild_curve_from_local', 'arc_length_simpson', 'calculate_bezier_control_points']

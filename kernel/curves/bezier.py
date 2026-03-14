import math
from typing import Tuple
from kernel.geometry.division import divider

Point = Tuple[float, float]


def point_on_cubic_bezier(P0: Point, P1: Point, P2: Point, P3: Point, t: float) -> Point:
    # B(t)=((1−t)^3 *P0)+(3(1−t)^2 *t*P1)+(3(1−t)t^2*P2)+(t^3 *P3)
    if not (0.0 <= t <= 1.0):
        raise ValueError("t must be between 0 and 1")
    u = 1.0 - t
    u3 = u * u * u
    t3 = t * t * t
    coeff0 = u3
    coeff1 = 3 * (u * u) * t
    coeff2 = 3 * u * (t * t)
    coeff3 = t3
    x = coeff0 * P0[0] + coeff1 * P1[0] + coeff2 * P2[0] + coeff3 * P3[0]
    y = coeff0 * P0[1] + coeff1 * P1[1] + coeff2 * P2[1] + coeff3 * P3[1]
    return x, y

# ----------------------------------------------------------------------------


def tangent_vector_cubic(P0: Point, P1: Point, P2: Point, P3: Point, t: float) -> Point:
    """Return derivative vector B'(t) for the cubic Bezier.
    B′(t)=3(1−t)^2 *(P1−P0)+6(1−t)*t(P2−P1)+3*t^2(P3−P2)"""
    if not (0.0 <= t <= 1.0):
        raise ValueError("t must be between 0 and 1")
    u = 1.0 - t
    a = 3 * (u * u)
    b = 6 * u * t
    c = 3 * (t * t)
    dx = a * (P1[0] - P0[0]) + b * (P2[0] - P1[0]) + c * (P3[0] - P2[0])
    dy = a * (P1[1] - P0[1]) + b * (P2[1] - P1[1]) + c * (P3[1] - P2[1])
    return dx, dy


def tangent_unit_vector_cubic(P0: Point, P1: Point, P2: Point, P3: Point, t: float) -> Point:
    dx, dy = tangent_vector_cubic(P0, P1, P2, P3, t)
    norm = math.hypot(dx, dy)
    if norm == 0:
        return 0.0, 0.0
    return dx / norm, dy / norm


def tangent_angle_degrees_cubic(P0: Point, P1: Point, P2: Point, P3: Point, t: float) -> float:
    dx, dy = tangent_vector_cubic(P0, P1, P2, P3, t)
    return math.degrees(math.atan2(dy, dx))

# ----------------------------------------------------------------------------


def _build_length_table(P0, P1, P2, P3, m=500):
    """
    Build arrays ts (len m+1) and cumulative lengths L where L[0]=0, L[-1]=total_length.
    m = number of segments (samples), larger m => better initial accuracy.
    """
    ts = [i / m for i in range(m+1)]
    pts = [point_on_cubic_bezier(P0, P1, P2, P3, t) for t in ts]
    L = [0.0]
    for i in range(1, len(pts)):
        seg = math.hypot(pts[i][0]-pts[i-1][0], pts[i][1]-pts[i-1][1])
        L.append(L[-1] + seg)
    return ts, L


def point_at_distance_cubic(P0:Point, P1:Point, P2:Point, P3:Point, distance: float,
                            m: int=500, tol: float=1e-3, max_iter: int=40) -> Tuple[Point, float]:
    """
    Return (x,y), t such that the point is at 'distance' along the curve from t=0.
    distance: same units as control points. If distance <=0 returns P0, if >= total returns P3.
    m: initial sample segments for building length table.
    tol: tolerance in units for arc length.
    """
    ts, L = _build_length_table(P0, P1, P2, P3, m=m)
    total = L[-1]
    if distance <= 0:
        return P0, 0.0
    if distance >= total:
        return P3, 1.0
    # find initial bracket index i where L[i] < distance <= L[i+1]
    import bisect
    i = bisect.bisect_left(L, distance) - 1
    if i < 0:
        i = 0
    t0, t1 = ts[i], ts[i+1]
    # bracket lengths
    L0, L1 = L[i], L[i+1]
    # initial linear interpolation for t
    if L1 - L0 != 0:
        t_guess = t0 + (distance - L0) * (t1 - t0) / (L1 - L0)
    else:
        t_guess = 0.5 * (t0 + t1)
    # refine with bisection using arc length function of t

    def arc_length_to_t(t):
        # approximate length from 0..t with Simpson using small n
        # choose n proportional to t*m but at least 4:
        n = max(6, int(m * t))
        return arc_length_simpson(P0, P1, P2, P3, t, n)
    # helper uses Simpson on [0,t]

    def _arc_len(t):
        return arc_length_to_t(t)
    # binary search refinement between t_low and t_high
    t_low, t_high = t0, t1
    for _ in range(max_iter):
        t_mid = 0.5 * (t_low + t_high)
        Lmid = _arc_len(t_mid)
        if abs(Lmid - distance) <= tol:
            t_final = t_mid
            break
        if Lmid < distance:
            t_low = t_mid
        else:
            t_high = t_mid
    else:
        t_final = 0.5 * (t_low + t_high)
    pt = point_on_cubic_bezier(P0, P1, P2, P3, t_final)
    return pt, t_final


def arc_length_simpson(P0, P1, P2, P3, t_max=1.0, n=200):
    """
    Simpson's rule is used to estimate the arc length of a curve
    by numerically approximating the definite integral in the arc length formula

    Simpson integration of speed(t) from 0..t_max. n must be even.
    We map s in [0,1] -> t = s * t_max and integrate accordingly.
    """
    if n % 2 == 1:
        n += 1
    h = t_max / n

    def speed(t):
        dx, dy = tangent_vector_cubic(P0, P1, P2, P3, t)
        return math.hypot(dx, dy)
    s = speed(0.0) + speed(t_max)
    for i in range(1, n):
        t = i * h
        coeff = 4 if i % 2 == 1 else 2
        s += coeff * speed(t)
    return (h / 3.0) * s

# the following is De Casteljeau funtion that take a sub-curve equals t from a curve and returns the sub-curve and the rest of the curve (4 points , 4 points)


def split_cubic_bezier(P0, P1, P2, P3, t):
    def lerp(a, b, t):
        return (
            a[0] + (b[0] - a[0]) * t,
            a[1] + (b[1] - a[1]) * t
        )

    # level 1
    P01 = lerp(P0, P1, t)
    P12 = lerp(P1, P2, t)
    P23 = lerp(P2, P3, t)

    # level 2
    P012 = lerp(P01, P12, t)
    P123 = lerp(P12, P23, t)

    # level 3 (split point)
    M = lerp(P012, P123, t)

    left = (P0,  P01,  P012, M)
    right = (M,  P123, P23,  P3)

    return left, right

# the following function cut one curve into equal sub-curves , sub-curve = n% of the whole or remaining curve


def split_one_cubic_into_n(P0, P1, P2, P3, n):
    curves = []
    remaining = (P0, P1, P2, P3)

    for i in range(n - 1):
        t = 1.0 / (n - i)
        left, remaining = split_cubic_bezier(*remaining, t)
        curves.append(left)

    curves.append(remaining)
    return curves


def split_multiple_united_curves(curves: list, divisions: list):
    sub_curves = {}
    curve = None
    remaining_curve = []

    length_each_curve, sum_all_curves = multiple_curves_length(curves)
    sum_all_divisions = sum(divisions)

    if len(curves) == 0:
        raise ValueError("curves list is empty")

    if len(divisions) == 0:
        raise ValueError("divisions list is empty")

    if sum_all_curves < sum_all_divisions:
        raise ValueError("The curve is smaller than the sum of divisions you want to devide it to")

    curves_divisions = divider(length_each_curve, divisions)

    rest = curves[len(curves_divisions):]

    for N_curve in range(len(curves_divisions)):
        curve = curves[N_curve]

        for division in curves_divisions[N_curve]:
            for num_sub_curve, length in sorted(division.items()):
                if not num_sub_curve in sub_curves:
                    sub_curves[num_sub_curve] = []

                endpoint, t_length = point_at_distance_cubic(*curve, length)
                new_sub_curve, curve = split_cubic_bezier(curve[0], curve[1], curve[2], curve[3], t_length)

                sub_curves[num_sub_curve].append(new_sub_curve)

    for r in rest:
        remaining_curve.append(r)
    remaining_curve.append(list(curve))

    return sub_curves, remaining_curve


# the following function compute the sum length of a united group of curves ( related to each other )


def multiple_curves_length(curves: list):
    curves_lengths = []
    total_length = 0
    for curve in curves:
        curve_length = arc_length_simpson(*curve)
        total_length += curve_length
        curves_lengths.append(curve_length)
    return curves_lengths, total_length


def curve_local_coordinate_representation(P0, P1, P2, P3):
    # Step 1: chord  (Distance formula : d = sqrt(X2-X1)² +(Y2-Y1)²)
    Cx = P3[0] - P0[0]
    Cy = P3[1] - P0[1]
    L = math.hypot(Cx, Cy)
    if L == 0:
        raise ValueError("Degenerate curve: start and end coincide")

    # Step 2: local axes
    Ux, Uy = Cx / L, Cy / L          # chord direction
    Vx, Vy = -Uy, Ux                # perpendicular

    # Step 3: control vectors
    D1x = P1[0] - P0[0]
    D1y = P1[1] - P0[1]

    D2x = P2[0] - P3[0]
    D2y = P2[1] - P3[1]

    # Step 4: project to local frame (normalized)
    ctrl1 = (
        (D1x * Ux + D1y * Uy) / L,
        (D1x * Vx + D1y * Vy) / L
    )

    ctrl2 = (
        (D2x * Ux + D2y * Uy) / L,
        (D2x * Vx + D2y * Vy) / L
    )

    return {
        "ctrl_start": ctrl1,
        "ctrl_end": ctrl2
    }


def rebuild_curve_from_local(P0, P3, ctrl1, ctrl2):
    Cx = P3[0] - P0[0]
    Cy = P3[1] - P0[1]
    L = math.hypot(Cx, Cy)

    Ux, Uy = Cx / L, Cy / L
    Vx, Vy = -Uy, Ux

    x1, y1 = ctrl1
    x2, y2 = ctrl2

    P1 = (
        P0[0] + L * (x1 * Ux + y1 * Vx),
        P0[1] + L * (x1 * Uy + y1 * Vy)
    )

    P2 = (
        P3[0] + L * (x2 * Ux + y2 * Vx),
        P3[1] + L * (x2 * Uy + y2 * Vy)
    )

    return P0, P1, P2, P3

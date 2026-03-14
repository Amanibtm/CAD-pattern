import json
import math


def load_model(path="json_directory/model.json"):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "points": {},
            "elements": {},
            "constraints": {},
            "operations": {}
        }


def save_model(model, path="json_directory/model.json"):
    with open(path, "w") as f:
        json.dump(model, f, indent=4)


def add_point_logic(model, x, y):
    existing = point_exists(model, x, y)
    if existing:
        return existing

    pid = new_element_id(model, "points", "P")
    model["points"][pid] = {"x": x, "y": y}
    return pid


def add_point(x, y, path="json_directory/model.json"):
    model = load_model(path)
    ret = add_point_logic(model, x, y)
    save_model(model, path)
    return ret


def add_line(start_point, end_point, path="json_directory/model.json"):
    model = load_model(path)
    p0 = add_point_logic(model, start_point[0], start_point[1])
    p1 = add_point_logic(model, end_point[0], end_point[1])
    existing = line_exists(model, p0, p1)
    if existing:
        return existing

    element_id = new_element_id(model, "elements", "L")
    model["elements"][element_id] = {
        "type": "line",
        "start": p0,
        "end": p1
    }
    save_model(model, path)
    return element_id


def add_cubic_bezier(p0, p1, p2, p3, path="json_directory/model.json"):
    model = load_model(path)
    p0 = add_point_logic(model, p0[0], p0[1])
    p1 = add_point_logic(model, p1[0], p1[1])
    p2 = add_point_logic(model, p2[0], p2[1])
    p3 = add_point_logic(model, p3[0], p3[1])

    existing = curve_exists(model, p0, p1, p2, p3)
    if existing:
        return existing

    element_id = new_element_id(model, "elements", "CB")
    model["elements"][element_id] = {
        "type": "cubic_bezier",
        "P0": p0,
        "P1": p1,
        "P2": p2,
        "P3": p3,
    }
    save_model(model, path)
    return element_id


def add_length_constraint(element_id, length, path="json_directory/model.json"):
    model = load_model(path)
    constraint_id = new_element_id(model, "constraints", "C")
    model["constraints"][constraint_id] = {
        "type": "length",
        "element": element_id,
        "value": length
    }
    save_model(model, path)

    '''Later you will need to decide:

    is this total length?

    or projection length?

    or distance between endpoints?'''


def add_fixed_point_constraint(point_id, path="json_directory/model.json"):
    model = load_model(path)
    constraint_id = new_element_id(model, "constraints", "C")
    model["constraints"][constraint_id] = {
        "type": "fixed_point",
        "point": point_id
    }
    save_model(model, path)
    return constraint_id


def add_coincident_constraint(point_ids, path="json_directory/model.json"):
    # points that are the same, occupy the same location, or occur at the same time. "تطابق"
    model = load_model(path)
    constraint_id = new_element_id(model, "constraints", "C")
    model["constraints"][constraint_id] = {
        "type": "coincident",
        "points": point_ids
    }
    save_model(model, path)
    return constraint_id


def add_curve_local_shape_constraint(element_id, ctrl1, ctrl2, path="json_directory/model.json"):
    model = load_model(path)
    constraint_id = new_element_id(model, "constraints", "C")
    model["constraints"][constraint_id] = {
        "type": "curve_local_shape",
        "element": element_id,
        "data": {
            "ctrl1": list(ctrl1),
            "ctrl2": list(ctrl2)
        }
    }
    save_model(model, path)
    return constraint_id


def add_operation(op_type, data, path="json_directory/model.json"):
    model = load_model(path)
    op_id = new_element_id(model, "operations", "O")
    model["operations"][op_id] = {
        "type": op_type,
        **data
    }
    save_model(model, path)
    return op_id


def point_exists(model, x, y, eps=1e-3):
    for pid, p in model["points"].items():
        if math.hypot(p["x"] - x, p["y"] - y) < eps:
            return pid
    return None


def line_exists(model, p0, p1):
    for eid, e in model["elements"].items():
        if e["type"] == "line":
            if {e["start"], e["end"]} == {p0, p1}:
                return eid
    return None


def curve_exists(model, p0, p1, p2, p3):
    for eid, e in model["elements"].items():
        if e["type"] == "cubic_bezier":
            if e["P0"] == p0 and e["P1"] == p1 and e["P2"] == p2 and e["P3"] == p3:
                return eid
    return None


def new_element_id(model, container="elements", prefix="E"):
    i = 1
    while f"{prefix}{i}" in model[container]:
        i += 1
    return f"{prefix}{i}"


"""
GEOMETRIC MODEL – FOUNDATION LAYER
=================================

Purpose
-------
This file defines the *declarative geometric model* of the system.
It is NOT a solver, NOT a renderer, and NOT a geometry mutator.

Core principles
---------------
1. Nothing moves directly.
   - Geometry is never edited in-place.
   - All changes are expressed via constraints and operations.
   - Geometry is rebuilt later by a solver.

2. Identity is internal.
   - IDs for points, elements, constraints, and operations
     are generated internally.
   - User input never provides IDs.

3. Topology over coordinates.
   - Elements (lines, curves) reference point IDs.
   - Points store coordinates.
   - Shared points represent connections.

4. Separation of responsibilities.
   - Points       → geometry storage
   - Elements     → topology (what connects to what)
   - Constraints  → rules (length, fixed, coincident, shape)
   - Operations   → user intent / history (dart, split, move)

5. add_*_logic vs add_*.
   - *_logic functions mutate an in-memory model only.
   - add_* functions handle load → logic → save.
   - Disk IO is never mixed with logic.

6. Constraints are descriptive, not procedural.
   - No solving happens here.
   - No iteration, no loops, no enforcement.
   - This layer only records facts and intentions.

7. Cubic Bézier convention.
   - P0: start point
   - P1: first control
   - P2: second control
   - P3: end point
   - Matches math literature and CAD standards.

This file is intentionally stable.
---------------------------------
Do NOT add:
- solver logic
- geometry mutation
- rebuild logic
- dependency resolution

Those belong to higher layers.

If something feels hard to do here,
it probably belongs elsewhere.
"""

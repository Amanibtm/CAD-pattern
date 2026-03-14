def cm_to_points(number=1.0):
    return round((number*72)/2.54, 2)


def inch_to_points(number=1.0):
    return round(number*72, 2)


def points_to_cm(number=1.0):
    return round((number*2.54)/72, 2)


def points_to_inch(number=1.0):
    return round(number/72, 2)



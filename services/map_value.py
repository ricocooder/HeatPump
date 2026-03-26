"""
Linear range mapping utility.

Used to convert raw ADC readings (0-1023) to physical units (A or V).
"""


def map_value(value: float, in_min: float, in_max: float,
              out_min: float, out_max: float) -> float:
    """
    Map *value* from one numeric range to another using linear interpolation.

    Formula: out = (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    Args:
        value:   Input value to map.
        in_min:  Lower bound of the input range.
        in_max:  Upper bound of the input range.
        out_min: Lower bound of the output range.
        out_max: Upper bound of the output range.

    Returns:
        float: Linearly interpolated value in the output range.
               Returns out_min if in_max == in_min (avoids division by zero).
    """
    if in_max == in_min:
        return out_min
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

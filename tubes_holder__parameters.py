import logging
import math as m
from importlib import reload

from typeguard import typechecked

log = logging.getLogger(__name__)

# ============
#  Tolerances
# ============


@typechecked
class Tol:
    """
    Tolerances constants for the model.
    All dimensions are in mm if not specified.
    """

    # General tolerance
    tol = 0.1


# ============
#  Dimensions
# ============


@typechecked
class TubeHolder:
    """
    Dimensions of the tube holder.
    All dimensions are in mm if not specified.
    """

    height = 50.0
    tube_height = 100.0
    tube_cap_diameter = 19.0
    tube_diameter = 15.0
    tube_hole_diameter = tube_diameter + 1.0
    tube_hole_radius = tube_hole_diameter / 2
    nb_holes = 7
    width = 45
    length = tube_hole_diameter * (2 * nb_holes + 1)
    support_thickness = 5.0

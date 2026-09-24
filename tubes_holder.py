# From cq-editor run:
# _p = '/home/manu/manuLinux/code/sources.yguel/3D_modeling/cadquery/tubes_holder/tubes_holder.py'
# exec(compile(open(_p).read(), _p, "exec"))

import inspect
import math as m
import os
import sys
from importlib import reload


def _script_path():
    if "__file__" in globals():
        return os.path.abspath(__file__)
    filename = inspect.currentframe().f_code.co_filename
    return os.path.abspath(filename)


current_path = os.path.dirname(_script_path())
sys.path.append(current_path)

import cq_utils

reload(cq_utils)
import numpy as np
import scipy.spatial.transform as stf

import tubes_holder__parameters
from cq_utils import *

reload(tubes_holder__parameters)
from tubes_holder__parameters import *

# Warning view_trough, is not the same piece built for an amovible front cover, the inner cylinder that is used to hollow the object is just extended to cut trough the font face.
view_through = False
export_stl_step = True
SEE_HALF = False
export_tol = 0.001


# ==============================
#  Computed geometric dimensions
# ==============================


####################################
####################################
# ACTUAL CODE
####################################


def tube_hole(h: float, tr: tuple = (0, 0, 0)):
    """
    Create a tube hole.
    """
    hole_radius = TubeHolder.tube_hole_radius
    hole = cq.Workplane("XY").circle(hole_radius).extrude(2 * h).translate(tr)
    return hole


def holder():
    """
    Create the main holder.
    """
    width = TubeHolder.width
    length = TubeHolder.length
    height = TubeHolder.height
    wall_thickness = TubeHolder.wall_thickness
    base = cq.Workplane("XY").box(
        width, length, wall_thickness, centered=(True, True, False)
    )
    top = base.translate((0, 0, height - wall_thickness))
    middle = base.translate((0, 0, 10 - wall_thickness / 2.0))
    leg_base = cq.Workplane("XY").box(
        width, wall_thickness, height, centered=(True, True, False)
    )
    left_leg = leg_base.translate((0, -length / 2 + wall_thickness / 2, 0))
    right_leg = leg_base.translate((0, length / 2 - wall_thickness / 2, 0))
    holder = top.union(middle).union(left_leg).union(right_leg)

    # Fillets
    # =======
    fillet_size = wall_thickness / 4.0
    # Add fillets to the edges of the top most face
    holder = holder.edges(">Z").fillet(fillet_size)
    # Add fillets at the junction of the top and middle sections
    ## Left
    l_top_left = (
        width / 2,
        -length / 2 + 2 * wall_thickness,
        height - wall_thickness / 2,
    )
    l_bot_right = (-width / 2, -length / 2 + wall_thickness / 2, wall_thickness / 2)
    left_selector = cq.selectors.BoxSelector(
        l_top_left, l_bot_right, boundingbox=False
    )  # Only center point is ok for edges for bbox inclusion test
    holder = (
        holder.edges(left_selector).edges("#Z").fillet(fillet_size)
    )  # keep only edges orthogonal to Z

    ## Right
    r_top_left = (
        width / 2,
        length / 2 - 2 * wall_thickness,
        height - wall_thickness / 2,
    )
    r_bot_right = (-width / 2, length / 2 - wall_thickness / 2, wall_thickness / 2)
    right_selector = cq.selectors.BoxSelector(
        r_top_left, r_bot_right, boundingbox=False
    )  # Only center point is ok for edges for bbox inclusion test
    holder = (
        holder.edges(right_selector).edges("#Z").fillet(fillet_size)
    )  # keep only edges orthogonal to Z
    return holder


def tube_holder():
    """
    Create the complete tube holder with all tube holes.
    """
    length = TubeHolder.length
    tube_height = TubeHolder.tube_height
    nb_holes = TubeHolder.nb_holes
    hole_diam = TubeHolder.tube_hole_diameter
    base = holder()
    hole = tube_hole(tube_height, (0, 0, 0))
    for i in range(nb_holes):
        tr = (0, hole_diam * (2 * i + 1.5) - length / 2, 0)
        base = base.cut(hole.translate(tr))
    return base


str_size = (
    str(TubeHolder.tube_hole_diameter)
    + "x"
    + str(TubeHolder.height)
    + "__nb"
    + str(TubeHolder.nb_holes)
)
full_model_info = [
    {
        "name": "tube_holder_" + str_size,
        "gen": tube_holder,
        "color": "yellow",
        "export": True,
        "display": True,
    }
]


if export_stl_step:
    import os

    from cadquery import exporters

    ex_path = os.path.join(current_path, "exports", "models")

    sol_pfx = "diamHole_x_h__nholes_" + str_size + "_"

    tube_holder_base_file_name = sol_pfx + "tube_holder"

    file_names = [tube_holder_base_file_name]

    gen_funcs = [tube_holder]

    models = []
    for i in range(0, len(file_names)):
        d = {"file_name": file_names[i], "gen_f": gen_funcs[i]}
        models.append(d)

    for item in models:
        f_name = item["file_name"]
        gen_f = item["gen_f"]

        # STL
        stl_full_file_name = os.path.join(ex_path, f_name + ".stl")
        exporters.export(
            gen_f(),
            stl_full_file_name,
            exportType=exporters.ExportTypes.STL,
            tolerance=export_tol,
        )

        # STEP
        step_full_file_name = os.path.join(ex_path, f_name + ".step")
        exporters.export(
            gen_f(),
            step_full_file_name,
            exportType=exporters.ExportTypes.STEP,
            tolerance=export_tol,
        )


# show_object(res)
proto_base = False
if proto_base:
    for mod in full_model_info:
        if "base_" != mod["name"][0 : len("base_")]:
            mod["display"] = False

if SEE_HALF:
    cut_side = 1000
    cut_cube = (
        cq.Workplane("XY")
        .box(cut_side, cut_side, cut_side, centered=True)
        .translate((0, cut_side / 2, 0))
    )


for mod in full_model_info:
    if mod["display"]:
        if SEE_HALF:
            show_object(
                mod["gen"]().cut(cut_cube), mod["name"], options={"color": mod["color"]}
            )
        else:
            show_object(mod["gen"](), mod["name"], options={"color": mod["color"]})


"""
show_object(place_3x_pg9_connector_holes().translate((0, 0, - HexaJoint.height)), "connector_holes_" +
            str_size, options={"color": "red"})

show_object(pg9_connector_hole(), "connector_hole_" +
            str_size, options={"color": "red"})

show_object(clipped_hollow_sphere(50, 50 - 4, 0),
            "clipped_hollow_sphere_" + str_size, options={"color": "yellow"})

show_object(plate_for_cut, "plate_for_cut_" +
            str_size, options={"color": "red"})

cut_for_screws = bottomPlate_fixing_screw_holes_to_base()
show_object(cut_for_screws, "cut_for_screws_" +
            str_size, options={"color": "red"})

show_object(pod_hat, "pod_hat_" + str_size, options={"color": "cyan"})
s_holes = all_screw_holes(
    2 * Base.top_hexagon_height).translate((0, 0, -Base.top_hexagon_height))
show_object(s_holes, "s_holes_" + str_size, options={"color": "red"})
cyl_corner_rad = ShellSection.CylinderCorner.radius
corner_pos_init = (
    ShellSection.Outer.vertex_2_vertex_radius - cyl_corner_rad, 0, 0)
show_object(corner(ShellNav.height).translate(corner_pos_init),
            "corner_" + str_size, options={"color": "red"})
"""
# show_object(corner(10), "corner")
# show_object(rails_orig00(ShellNav.height, 1.6, 3, 2), "rails")
# show_object(rails(ShellNav.height, 1.6, 3, 2)[
#            0].translate((0, 0, ShellNav.height)), "rails2", options={"color": "red"})

if SEE_HALF:
    # show_object(half_base_emptied(), "Main open")
    pass


print("=============")
print(" Cotes utiles")
print("=============")

print(f"tube_diameter: {TubeHolder.tube_diameter:.1f} mm.")
print(f"tube_hole_diameter: {TubeHolder.tube_hole_diameter:.1f} mm.")
print(f"nb_holes: {TubeHolder.nb_holes}")
print(f"width: {TubeHolder.width:.1f} mm.")
print(f"length: {TubeHolder.length:.1f} mm.")
print(f"height: {TubeHolder.height:.1f} mm.")

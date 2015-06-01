# !/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

import numpy as np
from vispy.geometry.generation import create_box
from vispy.scene.visuals import Node, Line

from colour import RGB_to_XYZ, xy_to_XYZ

from colour_analysis.constants import DEFAULT_PLOTTING_ILLUMINANT
from colour_analysis.utilities import (
    CHROMATICITY_DIAGRAM_TRANSFORMATIONS,
    XYZ_to_reference_colourspace,
    get_RGB_colourspace)
from colour_analysis.visuals import Box


def RGB_identity_cube(width_segments=16,
                      height_segments=16,
                      depth_segments=16,
                      planes=None,
                      uniform_colour=None,
                      uniform_opacity=1.0,
                      vertex_colours=True,
                      wireframe=False,
                      *args,
                      **kwargs):
    vertices, _faces, _outline = create_box(width_segments=width_segments,
                                            height_segments=height_segments,
                                            depth_segments=depth_segments,
                                            planes=planes)

    vertex_colours = vertices['color'] if vertex_colours else None

    RGB_box = Box(width_segments=width_segments,
                  height_segments=height_segments,
                  depth_segments=depth_segments,
                  planes=planes,
                  uniform_colour=uniform_colour,
                  uniform_opacity=uniform_opacity,
                  vertex_colours=vertex_colours,
                  wireframe=wireframe,
                  wireframe_offset=(1, 1),
                  *args,
                  **kwargs)

    vertices = RGB_box.mesh_data.get_vertices()
    vertices += 0.5
    RGB_box.mesh_data.set_vertices(vertices)

    return RGB_box


def RGB_colourspace_volume_visual(colourspace='Rec. 709',
                                  reference_colourspace='CIE xyY',
                                  segments=16,
                                  uniform_colour=None,
                                  uniform_opacity=0.5,
                                  wireframe=True,
                                  wireframe_colour=None,
                                  wireframe_opacity=1.0,
                                  parent=None):
    node = Node(parent)

    colourspace = get_RGB_colourspace(colourspace)

    RGB_cube_f = RGB_identity_cube(
        width_segments=segments,
        height_segments=segments,
        depth_segments=segments,
        uniform_colour=uniform_colour,
        uniform_opacity=uniform_opacity,
        vertex_colours=not uniform_colour,
        parent=node)

    vertices = RGB_cube_f.mesh_data.get_vertices()
    XYZ = RGB_to_XYZ(
        vertices,
        colourspace.whitepoint,
        colourspace.whitepoint,
        colourspace.RGB_to_XYZ_matrix)
    value = XYZ_to_reference_colourspace(XYZ,
                                         colourspace.whitepoint,
                                         reference_colourspace)
    value[np.isnan(value)] = 0

    RGB_cube_f.mesh_data.set_vertices(value)

    if wireframe:
        RGB_cube_w = RGB_identity_cube(
            width_segments=segments,
            height_segments=segments,
            depth_segments=segments,
            uniform_colour=wireframe_colour,
            uniform_opacity=wireframe_opacity,
            vertex_colours=not wireframe_colour,
            wireframe=True,
            parent=node)
        RGB_cube_w.mesh_data.set_vertices(value)

    return node


def RGB_colourspace_triangle_visual(colourspace='Rec. 709',
                                    diagram='CIE 1931',
                                    uniform_colour=None,
                                    uniform_opacity=1.0,
                                    width=4.0,
                                    parent=None):
    if uniform_colour is None:
        uniform_colour = (0.8, 0.8, 0.8)

    colourspace = get_RGB_colourspace(colourspace)

    illuminant = DEFAULT_PLOTTING_ILLUMINANT

    XYZ_to_ij = CHROMATICITY_DIAGRAM_TRANSFORMATIONS[diagram]['XYZ_to_ij']

    ij = XYZ_to_ij(xy_to_XYZ(colourspace.primaries), illuminant)
    # TODO: Remove following hack dealing with 'agg' method issues.
    ij = np.vstack((ij[-1, ...], ij, ij[0, ...]))

    ij[np.isnan(ij)] = 0

    RGB = np.hstack((uniform_colour, uniform_opacity)),

    line = Line(ij,
                RGB,
                width=width,
                method='agg',
                parent=parent)

    return line
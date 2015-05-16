# !/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

import numpy as np
from vispy.color.color_array import ColorArray
from vispy.gloo import set_state
from vispy.scene import Node
from vispy.scene.visuals import (
    Image,
    Line,
    Markers,
    XYZAxis,
    create_visual_node)
from vispy.visuals.mesh import MeshVisual

from colour_analysis.geometry import plane, box

from colour import RGB_to_XYZ, XYZ_to_sRGB

from colour_analysis.common import (
    XYZ_to_reference_colourspace,
    get_cmfs,
    get_RGB_colourspace)
from colour_analysis.constants import DEFAULT_PLOTTING_ILLUMINANT


class PrimitiveVisual(MeshVisual):
    def __init__(self,
                 vertices,
                 faces,
                 uniform_colour=(0.5, 0.5, 1.0),
                 uniform_opacity=1.0,
                 vertex_colours=None,
                 wireframe=False,
                 wireframe_offset=None):

        self.__wireframe = wireframe
        self.__wireframe_offset = wireframe_offset
        mode = 'lines' if self.__wireframe else 'triangles'

        positions = vertices['position']

        uniform_colour = ColorArray(uniform_colour, alpha=uniform_opacity).rgba
        if vertex_colours is not None:
            vertex_colours[..., 3] = uniform_opacity

        MeshVisual.__init__(
            self,
            positions,
            faces,
            vertex_colours,
            None,
            uniform_colour,
            mode=mode)

    def draw(self, transforms):
        MeshVisual.draw(self, transforms)
        if self.__wireframe and self.__wireframe_offset:
            set_state(polygon_offset=self.__wireframe_offset,
                      polygon_offset_fill=True)


class PlaneVisual(PrimitiveVisual):
    def __init__(self,
                 width=1,
                 height=1,
                 width_segments=1,
                 height_segments=1,
                 direction='+z',
                 uniform_colour=(0.5, 0.5, 1.0),
                 uniform_opacity=1.0,
                 vertex_colours=None,
                 wireframe=False,
                 wireframe_offset=None):
        vertices, faces, outline = plane(width, height,
                                         width_segments, height_segments,
                                         direction)

        PrimitiveVisual.__init__(
            self,
            vertices,
            outline if wireframe else faces,
            uniform_colour,
            uniform_opacity,
            vertex_colours,
            wireframe,
            wireframe_offset)


Plane = create_visual_node(PlaneVisual)


class BoxVisual(PrimitiveVisual):
    def __init__(self,
                 width=1,
                 height=1,
                 depth=1,
                 width_segments=1,
                 height_segments=1,
                 depth_segments=1,
                 planes=None,
                 uniform_colour=(0.5, 0.5, 1.0),
                 uniform_opacity=1.0,
                 vertex_colours=None,
                 wireframe=False,
                 wireframe_offset=None):
        vertices, faces, outline = box(width, height, depth,
                                       width_segments,
                                       height_segments,
                                       depth_segments,
                                       planes)

        PrimitiveVisual.__init__(
            self,
            vertices,
            outline if wireframe else faces,
            uniform_colour,
            uniform_opacity,
            vertex_colours,
            wireframe,
            wireframe_offset)


Box = create_visual_node(BoxVisual)


class PointsVisual(Markers):
    def __init__(self,
                 points=None,
                 size=4.0,
                 edge_size=0.5,
                 face_color=None,
                 edge_color=None,
                 parent=None):
        Markers.__init__(self)

        self.set_data(points,
                      size=size,
                      edge_width=edge_size,
                      face_color=face_color,
                      edge_color=edge_color)
        self.set_symbol('disc')

        if parent is not None:
            parent.add(self)


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
    vertices, _faces, _outline = box(width_segments=width_segments,
                                     height_segments=height_segments,
                                     depth_segments=depth_segments,
                                     planes=planes)

    vertex_colours = vertices['colour'] if vertex_colours else None

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


def RGB_colourspace_gamut_visual(colourspace='Rec. 709',
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


def RGB_scatter_visual(RGB,
                       colourspace='Rec. 709',
                       reference_colourspace='CIE xyY',
                       size=4.0,
                       edge_size=0.5,
                       uniform_colour=None,
                       uniform_opacity=1.0,
                       uniform_edge_colour=None,
                       uniform_edge_opacity=1.0,
                       maximum_points=10 ** 5,
                       parent=None):
    colourspace = get_RGB_colourspace(colourspace)

    RGB = np.asarray(RGB).reshape((-1, 3))

    if RGB.shape[0] > maximum_points:
        RGB = RGB[np.random.choice(RGB.shape[0], maximum_points)]

    XYZ = RGB_to_XYZ(
        RGB,
        colourspace.whitepoint,
        colourspace.whitepoint,
        colourspace.RGB_to_XYZ_matrix)

    points = XYZ_to_reference_colourspace(XYZ,
                                          colourspace.whitepoint,
                                          reference_colourspace)

    RGB = np.clip(RGB, 0, 1)

    if uniform_colour is None:
        RGB = np.hstack((RGB, np.full((RGB.shape[0], 1), uniform_opacity)))
    else:
        RGB = ColorArray(uniform_colour, alpha=uniform_opacity).rgba

    if uniform_edge_colour is None:
        RGB_e = RGB
    else:
        RGB_e = ColorArray(uniform_edge_colour,
                           alpha=uniform_edge_opacity).rgba

    markers = PointsVisual(points=points,
                           size=size,
                           edge_size=edge_size,
                           face_color=RGB,
                           edge_color=RGB_e,
                           parent=parent)

    return markers


def spectral_locus_visual(reference_colourspace='CIE xyY',
                          cmfs='CIE 1931 2 Degree Standard Observer',
                          uniform_colour=None,
                          uniform_opacity=1.0,
                          width=2.0,
                          parent=None):
    cmfs = get_cmfs(cmfs)
    XYZ = cmfs.values

    illuminant = DEFAULT_PLOTTING_ILLUMINANT

    points = XYZ_to_reference_colourspace(XYZ,
                                          illuminant,
                                          reference_colourspace)
    points = np.vstack((points, points[0, ...]))
    points[np.isnan(points)] = 0

    if uniform_colour is None:
        RGB = XYZ_to_sRGB(points)
        RGB = np.hstack((RGB, np.full((RGB.shape[0], 1), uniform_opacity)))
    else:
        RGB = ColorArray(uniform_colour, alpha=uniform_opacity).rgba

    line = Line(points, np.clip(RGB, 0, 1), width=width, parent=parent)

    return line


def image_visual(image,
                 parent=None):
    image = np.clip(image, 0, 1)

    return Image(image, parent=parent)


def axis_visual(parent=None):
    return XYZAxis(parent=parent)

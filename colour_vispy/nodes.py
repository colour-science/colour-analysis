# !/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

import numpy as np
from vispy import scene
from vispy.color.color_array import ColorArray

from colour import RGB_to_XYZ, XYZ_to_sRGB

from colour_vispy.common import (
    DEFAULT_PLOTTING_ILLUMINANT,
    XYZ_to_reference_colourspace,
    get_cmfs,
    get_RGB_colourspace)
from colour_vispy.geometry import box
from colour_vispy.visuals import Box


def RGB_identity_cube(width_segments=16,
                      height_segments=16,
                      depth_segments=16,
                      planes=None,
                      uniform_colour=(0.5, 0.5, 1.0),
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


def RGB_colourspace_gamut_node(colourspace='Rec. 709',
                               reference_colourspace='CIE xyY',
                               segments=16,
                               uniform_colour=None,
                               uniform_opacity=0.5,
                               wireframe=True,
                               wireframe_colour=None,
                               wireframe_opacity=1.0,
                               parent=None):
    node = scene.Node(parent)

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


def spectral_locus_node(reference_colourspace='CIE xyY',
                        cmfs='CIE 1931 2 Degree Standard Observer',
                        uniform_colour=None,
                        uniform_opacity=1.0,
                        width=2.0,
                        parent=None):
    node = scene.Node(parent)

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

    scene.visuals.Line(points,
                       np.clip(RGB, 0, 1),
                       width=width,
                       parent=node)

    return node


if __name__ == '__main__':
    from vispy import visuals

    reference_colourspace = 'CIE xyY'

    canvas = scene.SceneCanvas(keys='interactive',
                               size=(800, 600),
                               show=True)

    view = canvas.central_widget.add_view()
    camera = scene.cameras.TurntableCamera(fov=45,
                                           parent=view.scene,
                                           up='+z')
    view.camera = camera

    rec_709 = RGB_colourspace_gamut_node(
        reference_colourspace=reference_colourspace,
        parent=view.scene)

    red_color4 = RGB_colourspace_gamut_node(
        'REDcolor4',
        reference_colourspace=reference_colourspace,
        wireframe=False,
        parent=view.scene)

    transform = visuals.transforms.AffineTransform()
    transform.translate((1, 0, 0))
    red_color4.transform = transform

    aces_cg = RGB_colourspace_gamut_node(
        'ACEScg',
        reference_colourspace=reference_colourspace,
        uniform_colour=(1.0, 1.0, 1.0),
        uniform_opacity=1.0,
        wireframe_colour='k',
        wireframe_opacity=0.5,
        parent=view.scene)

    spectral_locus = spectral_locus_node(
        reference_colourspace=reference_colourspace,
        parent=view.scene)

    transform = visuals.transforms.AffineTransform()
    transform.translate((2, 0, 0))
    aces_cg.transform = transform

    axis = scene.visuals.XYZAxis(parent=view.scene)

    canvas.app.run()

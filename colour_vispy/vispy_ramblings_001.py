# !/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

import sys

import numpy as np
from vispy import scene

from colour_vispy.geometry import box, plane
from colour_vispy.visuals import Box, Plane

if __name__ == '__main__' and sys.flags.interactive == 0:
    canvas = scene.SceneCanvas(keys='interactive',
                               size=(800, 600),
                               show=True,
                               bgcolor=(0.5, 0.5, 0.5))

    view = canvas.central_widget.add_view()
    view.camera = scene.cameras.TurntableCamera(fov=45, parent=view.scene,
                                                up='+y')

    direction = '+z'
    sides = ('-x', '-y', '-z')
    # sides = ('+x', '-x', '+y', '-y', '+z', '-z')
    w, h, d = 1, 2, 3
    w_s, h_s, d_s = 16, 8, 4

    vertices, filled, outline = plane(width=w / 2,
                                      height=h / 2,
                                      width_segments=w_s,
                                      height_segments=h_s,
                                      direction=direction)
    RGB_f = np.copy(vertices['color'])
    RGB_f[..., 3] *= 0
    RGB_e = vertices['color']

    quad = Plane(direction=direction,
                 width=w / 2,
                 height=h / 2,
                 width_segments=w_s,
                 height_segments=h_s,
                 vertex_colors=RGB_f,
                 edge_color=RGB_e,
                 parent=view.scene)

    vertices, filled, outline = box(width=w,
                                    height=h,
                                    depth=h,
                                    width_segments=w_s,
                                    height_segments=h_s,
                                    depth_segments=h_s,
                                    sides=sides)
    RGB_f = np.copy(vertices['color'])
    RGB_f[..., 3] *= 0
    RGB_e = vertices['color']

    box1 = Box(width=w,
               height=h,
               depth=h,
               width_segments=w_s,
               height_segments=h_s,
               sides=sides,
               depth_segments=h_s,
               vertex_colors=RGB_f,
               edge_color=RGB_e,
               parent=view.scene)

    box2 = Box(width=0.5,
               height=0.5,
               depth=0.5,
               width_segments=8,
               height_segments=8,
               depth_segments=8,
               edge_color='k',
               parent=view.scene)

    vertices = box2.mesh_data.get_vertices()
    vertices[..., 0] += 1
    box2.mesh_data.set_vertices(vertices)

    axis = scene.visuals.XYZAxis(parent=view.scene)

    canvas.app.run()

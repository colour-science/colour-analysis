# !/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

import numpy as np

from colour_analysis.geometries import plane_geometry


def box_geometry(width=1,
                 height=1,
                 depth=1,
                 width_segments=1,
                 height_segments=1,
                 depth_segments=1,
                 planes=None):
    planes = (('+x', '-x', '+y', '-y', '+z', '-z')
              if planes is None else
              [d.lower() for d in planes])

    w_s, h_s, d_s = width_segments, height_segments, depth_segments

    planes_m = []
    if '-z' in planes:
        planes_m.append(plane_geometry(width, depth, w_s, d_s, '-z'))
        planes_m[-1][0]['position'][..., 2] -= height / 2
    if '+z' in planes:
        planes_m.append(plane_geometry(width, depth, w_s, d_s, '+z'))
        planes_m[-1][0]['position'][..., 2] += height / 2

    if '-y' in planes:
        planes_m.append(plane_geometry(height, width, h_s, w_s, '-y'))
        planes_m[-1][0]['position'][..., 1] -= depth / 2
    if '+y' in planes:
        planes_m.append(plane_geometry(height, width, h_s, w_s, '+y'))
        planes_m[-1][0]['position'][..., 1] += depth / 2

    if '-x' in planes:
        planes_m.append(plane_geometry(depth, height, d_s, h_s, '-x'))
        planes_m[-1][0]['position'][..., 0] -= width / 2
    if '+x' in planes:
        planes_m.append(plane_geometry(depth, height, d_s, h_s, '+x'))
        planes_m[-1][0]['position'][..., 0] += width / 2

    positions = np.zeros((0, 3))
    uvs = np.zeros((0, 2))
    normals = np.zeros((0, 3))

    faces = np.zeros((0, 3), dtype=np.uint32)
    outline = np.zeros((0, 2), dtype=np.uint32)

    offset = 0
    for vertices_p, faces_p, outline_p in planes_m:
        positions = np.vstack((positions, vertices_p['position']))
        uvs = np.vstack((uvs, vertices_p['uv']))
        normals = np.vstack((normals, vertices_p['normal']))

        faces = np.vstack((faces, faces_p + offset))
        outline = np.vstack((outline, outline_p + offset))
        offset += vertices_p['position'].shape[0]

    vertices = np.zeros(positions.shape[0],
                        [('position', np.float32, 3),
                         ('uv', np.float32, 2),
                         ('normal', np.float32, 3),
                         ('colour', np.float32, 4)])

    colours = np.ravel(positions)
    colours = np.hstack((np.reshape(np.interp(colours,
                                              (np.min(colours),
                                               np.max(colours)),
                                              (0, 1)),
                                    positions.shape),
                         np.ones((positions.shape[0], 1))))

    vertices['position'] = positions
    vertices['normal'] = normals
    vertices['colour'] = colours
    vertices['uv'] = uvs

    return vertices, faces, outline

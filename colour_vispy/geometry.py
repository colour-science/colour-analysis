# !/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

import numpy as np


def plane(width=1,
          height=1,
          width_segments=1,
          height_segments=1,
          direction='+z'):
    x_grid = width_segments
    y_grid = height_segments

    x_grid1 = x_grid + 1
    y_grid1 = y_grid + 1

    # Positions, normals and uvs.
    positions = np.zeros(x_grid1 * y_grid1 * 3)
    normals = np.zeros(x_grid1 * y_grid1 * 3)
    uvs = np.zeros(x_grid1 * y_grid1 * 2)

    offset = offset1 = 0
    for i_y in range(y_grid1):
        y = i_y * height / y_grid - height / 2
        for i_x in range(x_grid1):
            x = i_x * width / x_grid - width / 2

            positions[offset] = x
            positions[offset + 1] = - y

            normals[offset + 2] = 1

            uvs[offset1] = i_x / x_grid
            uvs[offset1 + 1] = 1 - (i_y / y_grid)

            offset += 3
            offset1 += 2

    # Faces and outline.
    faces = np.zeros(x_grid * y_grid * 6, dtype=np.uint32)
    outline = np.zeros(x_grid * y_grid * 8, dtype=np.uint32)

    offset = offset1 = 0
    for i_y in range(y_grid):
        for i_x in range(x_grid):
            a = i_x + x_grid1 * i_y
            b = i_x + x_grid1 * (i_y + 1)
            c = (i_x + 1) + x_grid1 * (i_y + 1)
            d = (i_x + 1) + x_grid1 * i_y

            faces[offset] = a
            faces[offset + 1] = b
            faces[offset + 2] = d

            faces[offset + 3] = b
            faces[offset + 4] = c
            faces[offset + 5] = d

            outline[offset1] = a
            outline[offset1 + 1] = b

            outline[offset1 + 2] = b
            outline[offset1 + 3] = c

            outline[offset1 + 4] = c
            outline[offset1 + 5] = d

            outline[offset1 + 6] = d
            outline[offset1 + 7] = a

            offset += 6
            offset1 += 8

    positions = np.reshape(positions, (-1, 3))
    normals = np.reshape(normals, (-1, 3))
    faces = np.reshape(faces, (-1, 3))
    outline = np.reshape(outline, (-1, 2))

    direction = direction.lower()
    if direction in ('-x', '+x'):
        shift, neutral_axis = 1, 0
    elif direction in ('-y', '+y'):
        shift, neutral_axis = -1, 1
    elif direction in ('-z', '+z'):
        shift, neutral_axis = 0, 2

    sign = -1 if '-' in direction else 1

    positions = np.roll(positions, shift, -1)
    normals = np.roll(normals, shift, -1) * sign
    colours = np.ravel(positions)
    colours = np.hstack((np.reshape(np.interp(colours,
                                              (np.min(colours),
                                               np.max(colours)),
                                              (0, 1)),
                                    positions.shape),
                         np.ones((positions.shape[0], 1))))
    colours[..., neutral_axis] = 0
    uvs = np.reshape(uvs, (-1, 2))

    vertices = np.zeros(positions.shape[0],
                        [('position', np.float32, 3),
                         ('normal', np.float32, 3),
                         ('uv', np.float32, 2),
                         ('colour', np.float32, 4)])

    vertices['position'] = positions
    vertices['normal'] = normals
    vertices['colour'] = colours
    vertices['uv'] = uvs

    return vertices, faces, outline


def box(width=1,
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
        planes_m.append(plane(width, depth, w_s, d_s, '-z'))
        planes_m[-1][0]['position'][..., 2] -= height / 2
    if '+z' in planes:
        planes_m.append(plane(width, depth, w_s, d_s, '+z'))
        planes_m[-1][0]['position'][..., 2] += height / 2

    if '-y' in planes:
        planes_m.append(plane(height, width, h_s, w_s, '-y'))
        planes_m[-1][0]['position'][..., 1] -= depth / 2
    if '+y' in planes:
        planes_m.append(plane(height, width, h_s, w_s, '+y'))
        planes_m[-1][0]['position'][..., 1] += depth / 2

    if '-x' in planes:
        planes_m.append(plane(depth, height, d_s, h_s, '-x'))
        planes_m[-1][0]['position'][..., 0] -= width / 2
    if '+x' in planes:
        planes_m.append(plane(depth, height, d_s, h_s, '+x'))
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

# !/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

from vispy.scene.visuals import create_visual_node
from vispy.visuals.mesh import MeshVisual
from vispy.gloo import set_state
from vispy.color.color_array import ColorArray

from colour_vispy.geometry import plane, box


class PlaneVisual(MeshVisual):
    def __init__(self,
                 width=1,
                 height=1,
                 width_segments=1,
                 height_segments=1,
                 direction='+z',
                 vertex_colors=None,
                 face_colors=None,
                 color=(0.5, 0.5, 1, 1),
                 edge_color=None):
        vertices, filled_indices, outline_indices = plane(
            width, height, width_segments, height_segments, direction)

        MeshVisual.__init__(self, vertices['position'], filled_indices,
                            vertex_colors, face_colors, color)
        if edge_color is not None:
            edge_color = ColorArray(edge_color).rgba
            if edge_color.shape[0] == 1:
                self._outline = MeshVisual(vertices['position'],
                                           outline_indices,
                                           color=edge_color, mode='lines')
            else:
                self._outline = MeshVisual(vertices['position'],
                                           outline_indices,
                                           vertex_colors=edge_color,
                                           mode='lines')
        else:
            self._outline = None

    def draw(self, transforms):
        MeshVisual.draw(self, transforms)
        if self._outline:
            set_state(polygon_offset=(1, 1), polygon_offset_fill=True)
            self._outline.draw(transforms)


class BoxVisual(MeshVisual):
    def __init__(self,
                 width=1,
                 height=1,
                 depth=1,
                 width_segments=1,
                 height_segments=1,
                 depth_segments=1,
                 sides=None,
                 vertex_colors=None,
                 face_colors=None,
                 color=(0.5, 0.5, 1, 1),
                 edge_color=None):
        vertices, filled_indices, outline_indices = box(
            width, height, depth,
            width_segments, height_segments, depth_segments, sides)

        MeshVisual.__init__(self, vertices['position'], filled_indices,
                            vertex_colors, face_colors, color)
        if edge_color is not None:
            edge_color = ColorArray(edge_color).rgba
            if edge_color.shape[0] == 1:
                self._outline = MeshVisual(vertices['position'],
                                           outline_indices,
                                           color=edge_color, mode='lines')
            else:
                self._outline = MeshVisual(vertices['position'],
                                           outline_indices,
                                           vertex_colors=edge_color,
                                           mode='lines')
        else:
            self._outline = None

    def draw(self, transforms):
        MeshVisual.draw(self, transforms)
        if self._outline:
            set_state(polygon_offset=(1, 1), polygon_offset_fill=True)
            self._outline.draw(transforms)


Plane = create_visual_node(PlaneVisual)
Box = create_visual_node(BoxVisual)
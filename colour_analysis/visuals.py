# !/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

from vispy.color.color_array import ColorArray
from vispy.gloo import set_state
from vispy.scene.visuals import create_visual_node
from vispy.visuals.mesh import MeshVisual

from colour_analysis.geometry import plane, box


class GenericMeshVisual(MeshVisual):
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


class PlaneVisual(GenericMeshVisual):
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

        GenericMeshVisual.__init__(
            self,
            vertices,
            outline if wireframe else faces,
            uniform_colour,
            uniform_opacity,
            vertex_colours,
            wireframe,
            wireframe_offset)


class BoxVisual(GenericMeshVisual):
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

        GenericMeshVisual.__init__(
            self,
            vertices,
            outline if wireframe else faces,
            uniform_colour,
            uniform_opacity,
            vertex_colours,
            wireframe,
            wireframe_offset)


Plane = create_visual_node(PlaneVisual)
Box = create_visual_node(BoxVisual)

# !/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

from vispy.scene.visuals import create_visual_node

from colour_analysis.geometries import box_geometry
from colour_analysis.visuals import PrimitiveVisual


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
        vertices, faces, outline = box_geometry(width, height, depth,
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


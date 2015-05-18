# !/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

from vispy.scene.visuals import create_visual_node

from colour_analysis.geometries import plane_geometry
from colour_analysis.visuals import PrimitiveVisual


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
        vertices, faces, outline = plane_geometry(width, height,
                                                  width_segments,
                                                  height_segments,
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

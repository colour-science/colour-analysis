# !/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

import numpy as np

from vispy.color.color_array import ColorArray
from vispy.gloo import set_state
from vispy.scene.visuals import create_visual_node
from vispy.visuals.mesh import MeshVisual


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

        uniform_colour = ColorArray(uniform_colour, alpha=uniform_opacity).rgba
        if vertex_colours is not None:
            if vertex_colours.shape[-1] == 3:
                vertex_colours = np.hstack(
                    (vertex_colours,
                     np.full((vertex_colours.shape[0], 1), uniform_opacity)))
            else:
                vertex_colours[..., 3] = uniform_opacity

        MeshVisual.__init__(
            self,
            vertices,
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


Primitive = create_visual_node(PrimitiveVisual)

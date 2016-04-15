# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Primitive Visual
================

Defines the *Primitive Visual*:

-   :class:`PrimitiveVisual`
"""

from __future__ import division, unicode_literals

import numpy as np

from vispy.color.color_array import ColorArray
from vispy.gloo import set_state
from vispy.scene.visuals import create_visual_node
from vispy.visuals.mesh import MeshVisual

__author__ = 'Colour Developers'
__copyright__ = 'Copyright (C) 2013-2016 - Colour Developers'
__license__ = 'New BSD License - http://opensource.org/licenses/BSD-3-Clause'
__maintainer__ = 'Colour Developers'
__email__ = 'colour-science@googlegroups.com'
__status__ = 'Production'

__all__ = ['PrimitiveVisual',
           'Primitive']


class PrimitiveVisual(MeshVisual):
    def __init__(self,
                 vertices,
                 faces,
                 uniform_colour=(0.5, 0.5, 1.0),
                 uniform_opacity=1.0,
                 vertex_colours=None,
                 wireframe=False,
                 wireframe_offset=None):
        """
        Creates a primitive visual based on
        :class:`vispy.visuals.mesh.MeshVisual` class.

        Parameters
        ----------
        vertices : array_like
            Vertices data.
        faces : array_like
            Faces data.
        uniform_colour : array_like, optional
            Uniform mesh colour.
        uniform_opacity : numeric, optional
            Uniform mesh opacity.
        vertex_colours : array_like, optional
            Per vertex varying colour.
        wireframe : bool, optional
            Use wireframe display.
        wireframe_offset : array_like, optional
            Wireframe offset.

        Notes
        -----
        -   `vertex_colours` argument takes precedence over `uniform_colour` if
            provided.
        -   `uniform_opacity` argument will be stacked to `vertex_colours`
            argument if the latter last dimension is equal to 3.
        """

        self._wireframe = wireframe
        self._wireframe_offset = wireframe_offset
        mode = 'lines' if self._wireframe else 'triangles'

        uniform_colour = ColorArray(uniform_colour, alpha=uniform_opacity).rgba
        if vertex_colours is not None:
            if vertex_colours.shape[-1] == 3:
                vertex_colours = np.hstack(
                    (vertex_colours,
                     np.full((vertex_colours.shape[0], 1),
                             uniform_opacity,
                             np.float_)))
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

    def draw(self):
        MeshVisual.draw(self)
        if self._wireframe and self._wireframe_offset:
            set_state(polygon_offset=self._wireframe_offset,
                      polygon_offset_fill=True)


Primitive = create_visual_node(PrimitiveVisual)

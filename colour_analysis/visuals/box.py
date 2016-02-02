# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Box Visual
==========

Defines the *Box Visual*:

-   :class:`BoxVisual`
"""

from __future__ import division, unicode_literals

from vispy.geometry.generation import create_box
from vispy.scene.visuals import create_visual_node

from colour_analysis.visuals import PrimitiveVisual

__author__ = 'Colour Developers'
__copyright__ = 'Copyright (C) 2013-2016 - Colour Developers'
__license__ = 'New BSD License - http://opensource.org/licenses/BSD-3-Clause'
__maintainer__ = 'Colour Developers'
__email__ = 'colour-science@googlegroups.com'
__status__ = 'Production'

__all__ = ['BoxVisual',
           'Box']


class BoxVisual(PrimitiveVisual):
    """
    Creates a box like :class:`colour_analysis.visuals.PrimitiveVisual` class
    instance.

    Parameters
    ----------
    width : numeric, optional
        Box width.
    height : numeric, optional
        Box height.
    depth : numeric, optional
        Box depth.
    width_segments : int, optional
        Box segments count along the width.
    height_segments : int, optional
        Box segments count along the height.
    depth_segments : int, optional
        Box segments count along the depth.
    planes: array_like, optional
        Any combination of ``{'-x', '+x', '-y', '+y', '-z', '+z'}``

        Included planes in the box construction.
    uniform_colour : array_like, optional
        Uniform mesh colour.
    uniform_opacity : numeric, optional
        Uniform mesh opacity.
    vertex_colour : array_like, optional
        Per vertex varying colour.
    wireframe : bool, optional
        Use wireframe display.
    wireframe_offset : array_like, optional
        Wireframe offset.

    Notes
    -----
    -   `vertex_colours` argument takes precedence over `uniform_colour` if
        provided.
    -   `uniform_opacity` argument will be stacked to `vertex_colours` argument
        if the latter last dimension is equal to 3.
    """

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
        vertices, faces, outline = create_box(width, height, depth,
                                              width_segments,
                                              height_segments,
                                              depth_segments,
                                              planes)

        PrimitiveVisual.__init__(
            self,
            vertices['position'],
            outline if wireframe else faces,
            uniform_colour,
            uniform_opacity,
            vertex_colours,
            wireframe,
            wireframe_offset)


Box = create_visual_node(BoxVisual)

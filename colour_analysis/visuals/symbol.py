# !/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

from vispy.scene.visuals import Markers


class Symbol(Markers):
    def __init__(self,
                 symbol='disc',
                 positions=None,
                 size=4.0,
                 edge_size=0.5,
                 face_colour=None,
                 edge_colour=None,
                 scaling=False,
                 parent=None):
        """
        Convenient symbol visual based on :class:`vispy.scene.visuals.Markers`
        class instance.

        Parameters
        ----------
        symbol : unicode, optional
            Symbol type to draw.
        positions : array_like, optional
            Positions of symbols.
        size : numeric, optional
            Symbol size.
        edge_size : numeric, optional
            Symbol edge size.
        face_colour : array_like, optional
            Uniform symbol colour.
        edge_colour : array_like, optional
            Uniform symbol edge colour.
        scaling : bool, optional
            Marker will scale when zooming.
        parent : Node, optional
            Parent of the symbol visual in the `SceneGraph`.
        """

        Markers.__init__(self)

        self.set_data(positions,
                      size=size,
                      edge_width=edge_size,
                      face_color=face_colour,
                      edge_color=edge_colour,
                      scaling=scaling)
        self.symbol = symbol

        if parent is not None:
            parent.add(self)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

from vispy.scene.widgets import Console


class ConsoleView(Console):
    def __init__(self, canvas=None, *args, **kwargs):
        Console.__init__(self, *args, **kwargs)

        self.__canvas = canvas

    @property
    def canvas(self):
        """
        Property for **self.canvas** attribute.

        Returns
        -------
        SceneCanvas
        """

        return self.__canvas

    @canvas.setter
    def canvas(self, value):
        """
        Setter for **self.canvas** attribute.

        Parameters
        ----------
        value : SceneCanvas
            Attribute value.
        """

        raise AttributeError('"{0}" attribute is read only!'.format('canvas'))

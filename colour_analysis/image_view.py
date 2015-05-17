#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

import numpy as np

from vispy.scene.cameras import PanZoomCamera
from vispy.scene.widgets.viewbox import ViewBox

from colour import RGB_COLOURSPACES
from colour_analysis.visuals import image_visual


class ImageView(ViewBox):
    def __init__(self, image=None, oecf=None, **kwargs):
        ViewBox.__init__(self, **kwargs)

        self.__image = None
        self.image = image
        self.__oecf = None
        self.oecf = oecf

        self.__image_visual = None

        self.initialise_visuals()
        self.initialise_camera()

    @property
    def image(self):
        """
        Property for **self.__image** private attribute.

        Returns
        -------
        array_like
            self.__image.
        """

        return self.__image

    @image.setter
    def image(self, value):
        """
        Setter for **self.__image** private attribute.

        Parameters
        ----------
        value : array_like
            Attribute value.
        """

        if value is not None:
            assert type(value) in (tuple, list, np.ndarray, np.matrix), (
                ('"{0}" attribute: "{1}" type is not "tuple", "list", '
                 '"ndarray" or "matrix"!').format('image', value))
        self.__image = value

    @property
    def oecf(self):
        """
        Property for **self.__oecf** private attribute.

        Returns
        -------
        unicode
            self.__oecf.
        """

        return self.__oecf

    @oecf.setter
    def oecf(self, value):
        """
        Setter for **self.__oecf** private attribute.

        Parameters
        ----------
        value : unicode
            Attribute value.
        """

        if value is not None:
            assert type(value) in (str, unicode), (
                ('"{0}" attribute: "{1}" type is not '
                 '"str" or "unicode"!').format('oecf', value))
            assert value in RGB_COLOURSPACES, (
                '"{0}" OECF is not associated with any factory '
                'RGB colourspaces: "{1}".').format(value, ', '.join(
                sorted(RGB_COLOURSPACES.keys())))
        self.__oecf = value

    def __create_image(self):
        colourspace = RGB_COLOURSPACES[self.__oecf]

        return colourspace.transfer_function(self.__image)

    def __attach_visuals(self):
        self.__image_visual = image_visual(
            self.__create_image(),
            parent=self.scene)

    def __detach_visuals(self):
        self.__image_visual.remove_parent(self.scene)

    def __attach_camera(self):
        self.camera = PanZoomCamera(aspect=1)
        self.camera.flip = (False, True, False)

    def __detach_camera(self):
        pass

    def initialise_visuals(self):
        self.__attach_visuals()

        return True

    def initialise_camera(self):
        self.__attach_camera()

        return True

    def fit_image_visual_image_action(self):
        # TODO: Implement definition.

        print('fit_image_visual_image')

        return True
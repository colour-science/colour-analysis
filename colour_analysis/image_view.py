#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

import numpy as np

from vispy.scene.cameras import PanZoomCamera
from vispy.scene.widgets.viewbox import ViewBox

from colour import RGB_COLOURSPACES, RGB_to_RGB

from colour_analysis.visuals import image_visual


class ImageView(ViewBox):
    def __init__(self,
                 image=None,
                 oecf='Rec. 709',
                 input_colourspace='Rec. 709',
                 correlate_colourspace='ACEScg',
                 **kwargs):
        ViewBox.__init__(self, **kwargs)

        self.__image = None
        self.image = image
        self.__oecf = None
        self.oecf = oecf
        self.__input_colourspace = None
        self.input_colourspace = input_colourspace
        self.__correlate_colourspace = None
        self.correlate_colourspace = correlate_colourspace

        self.__image_visual = None

        self.__display_input_colourspace_out_of_gamut = False
        self.__display_correlate_colourspace_out_of_gamut = False
        self.__display_hdr_colours = False

        self.__initialise_visuals()
        self.__initialise_camera()

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

    @property
    def input_colourspace(self):
        """
        Property for **self.__input_colourspace** private attribute.

        Returns
        -------
        unicode
            self.__input_colourspace.
        """

        return self.__input_colourspace

    @input_colourspace.setter
    def input_colourspace(self, value):
        """
        Setter for **self.__input_colourspace** private attribute.

        Parameters
        ----------
        value : unicode
            Attribute value.
        """

        if value is not None:
            assert type(value) in (str, unicode), (
                ('"{0}" attribute: "{1}" type is not '
                 '"str" or "unicode"!').format('input_colourspace', value))
            assert value in RGB_COLOURSPACES, (
                '"{0}" colourspace not found in factory RGB colourspaces: '
                '"{1}".').format(
                value, ', '.join(sorted(RGB_COLOURSPACES.keys())))
        self.__input_colourspace = value

    @property
    def correlate_colourspace(self):
        """
        Property for **self.__correlate_colourspace** private attribute.

        Returns
        -------
        unicode
            self.__correlate_colourspace.
        """

        return self.__correlate_colourspace

    @correlate_colourspace.setter
    def correlate_colourspace(self, value):
        """
        Setter for **self.__correlate_colourspace** private attribute.

        Parameters
        ----------
        value : unicode
            Attribute value.
        """

        if value is not None:
            assert type(value) in (str, unicode), (
                ('"{0}" attribute: "{1}" type is not '
                 '"str" or "unicode"!').format('correlate_colourspace', value))
            assert value in RGB_COLOURSPACES, (
                '"{0}" colourspace not found in factory RGB colourspaces: '
                '"{1}".').format(value, ', '.join(
                sorted(RGB_COLOURSPACES.keys())))
        self.__correlate_colourspace = value

    def __create_image(self):
        colourspace = RGB_COLOURSPACES[self.__oecf]
        image = np.copy(self.__image)

        if self.__display_correlate_colourspace_out_of_gamut:
            image = RGB_to_RGB(image,
                               RGB_COLOURSPACES[self.__input_colourspace],
                               RGB_COLOURSPACES[self.__correlate_colourspace])

            colourspace = RGB_COLOURSPACES[self.__oecf]

        if (self.__display_input_colourspace_out_of_gamut or
                self.__display_correlate_colourspace_out_of_gamut):
            image[image > 0] = 0
            image[image < 0] = 1

        if self.__display_hdr_colours:
            image[image <= 1] = 0

        oecf = colourspace.transfer_function

        return oecf(image)

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

    def __initialise_visuals(self):
        self.__attach_visuals()

        return True

    def __initialise_camera(self):
        self.__attach_camera()

        return True

    def toggle_input_colourspace_out_of_gamut_colours_display_action(self):
        self.__display_input_colourspace_out_of_gamut = (
            not self.__display_input_colourspace_out_of_gamut)

        if self.__display_input_colourspace_out_of_gamut:
            self.__display_correlate_colourspace_out_of_gamut = False
            self.__display_hdr_colours = False

        self.__detach_visuals()

        self.__attach_visuals()

        return True

    def toggle_correlate_colourspace_out_of_gamut_colours_display_action(self):
        self.__display_correlate_colourspace_out_of_gamut = (
            not self.__display_correlate_colourspace_out_of_gamut)

        if self.__display_correlate_colourspace_out_of_gamut:
            self.__display_input_colourspace_out_of_gamut = False
            self.__display_hdr_colours = False

        self.__detach_visuals()

        self.__attach_visuals()

        return True

    def toggle_hdr_colours_display_action(self):
        self.__display_hdr_colours = (
            not self.__display_hdr_colours)

        if self.__display_hdr_colours:
            self.__display_input_colourspace_out_of_gamut = False
            self.__display_correlate_colourspace_out_of_gamut = False

        self.__detach_visuals()

        self.__attach_visuals()

        return True

    def fit_image_visual_image_action(self):
        # TODO: Implement definition.

        print('fit_image_visual_image')

        return True

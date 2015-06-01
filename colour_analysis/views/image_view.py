#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

import numpy as np

from vispy.scene.cameras import PanZoomCamera
from vispy.scene.visuals import Text
from vispy.scene.widgets.viewbox import ViewBox

from colour import (
    RGB_COLOURSPACES,
    RGB_to_RGB,
    RGB_to_XYZ,
    is_within_pointer_gamut,
    tstack)

from colour_analysis.visuals import image_visual


class ImageView(ViewBox):
    def __init__(self,
                 canvas=None,
                 image=None,
                 oecf='Rec. 709',
                 input_colourspace='Rec. 709',
                 correlate_colourspace='ACEScg',
                 **kwargs):
        ViewBox.__init__(self, **kwargs)

        self.__canvas = canvas

        self.__image = None
        self.image = image
        self.__oecf = None
        self.oecf = oecf
        self.__input_colourspace = None
        self.input_colourspace = input_colourspace
        self.__correlate_colourspace = None
        self.correlate_colourspace = correlate_colourspace

        self.__title_overlay_visual = None

        self.__image_visual = None

        self.__clamp_blacks = False
        self.__clamp_whites = False
        self.__image_overlay = True

        self.__display_input_colourspace_out_of_gamut = False
        self.__display_correlate_colourspace_out_of_gamut = False
        self.__display_out_of_pointer_gamut = False
        self.__display_hdr_colours = False

        self.__create_visuals()
        self.__attach_visuals()
        self.__create_camera()

        self.__create_title_overlay_visual()
        self.__canvas.events.resize.connect(self.__canvas_resize_event)

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
        image = np.copy(self.__image)

        has_overlay = False
        if self.__clamp_blacks:
            image = np.clip(image, 0, np.inf)
            has_overlay = True

        if self.__clamp_whites:
            image = np.clip(image, -np.inf, 1)
            has_overlay = True

        if self.__display_correlate_colourspace_out_of_gamut:
            image = RGB_to_RGB(image,
                               RGB_COLOURSPACES[self.__input_colourspace],
                               RGB_COLOURSPACES[self.__correlate_colourspace])
            has_overlay = True

        if (self.__display_input_colourspace_out_of_gamut or
                self.__display_correlate_colourspace_out_of_gamut):
            image[image >= 0] = 0
            image[image < 0] = 1
            has_overlay = True

        if self.__display_out_of_pointer_gamut:
            colourspace = RGB_COLOURSPACES[self.__input_colourspace]
            image = is_within_pointer_gamut(
                RGB_to_XYZ(image,
                           colourspace.whitepoint,
                           colourspace.whitepoint,
                           colourspace.RGB_to_XYZ_matrix)).astype(int)

            # TODO: Investigate why stacking implies that image need to be
            # inverted.
            image = 1 - tstack((image, image, image))
            has_overlay = True

        if self.__display_hdr_colours:
            image[image <= 1] = 0
            # has_overlay = True

        if self.__image_overlay and has_overlay:
            image = self.__image + image

        oecf = RGB_COLOURSPACES[self.__oecf].transfer_function

        return oecf(image)

    def __create_visuals(self):
        self.__image_visual = image_visual(self.__create_image())

    def __create_camera(self):
        self.camera = PanZoomCamera(aspect=1)
        self.camera.flip = (False, True, False)

    def __attach_visuals(self):
        self.__image_visual.add_parent(self.scene)

    def __detach_visuals(self):
        self.__image_visual.remove_parent(self.scene)

    def __create_title_overlay_visual(self):
        self.__title_overlay_visual = Text(str(),
                                           anchor_x='center',
                                           anchor_y='bottom',
                                           font_size=10,
                                           color=(0.8, 0.8, 0.8),
                                           parent=self)

        self.__title_overlay_visual_position()
        self.__title_overlay_visual_text()

    def __title_overlay_visual_position(self):
        self.__title_overlay_visual.pos = self.size[0] / 2, 32

    def __title_overlay_visual_text(self):
        self.__title_overlay_visual.text = str()

        if self.__display_input_colourspace_out_of_gamut:
            self.__title_overlay_visual.text = (
                '{0} - Out of Gamut Colours Display'.format(
                    self.__input_colourspace))

        if self.__display_correlate_colourspace_out_of_gamut:
            self.__title_overlay_visual.text = (
                '{0} - Out of Gamut Colours Display'.format(
                    self.__correlate_colourspace))

        if self.__display_out_of_pointer_gamut:
            self.__title_overlay_visual.text = ('Out of Pointer\'s Gamut '
                                                'Colours Display')

        if self.__display_hdr_colours:
            self.__title_overlay_visual.text = 'HDR Colours Display'

    def __canvas_resize_event(self, event=None):
        self.__title_overlay_visual_position()

    def cycle_correlate_colourspace_action(self):
        self.__detach_visuals()
        self.__create_visuals()
        self.__attach_visuals()
        self.__title_overlay_visual_text()

        return True

    def toggle_blacks_clamp_action(self):
        self.__clamp_blacks = not self.__clamp_blacks
        self.__detach_visuals()
        self.__create_visuals()
        self.__attach_visuals()
        self.__title_overlay_visual_text()

        return True

    def toggle_whites_clamp_action(self):
        self.__clamp_whites = not self.__clamp_whites
        self.__detach_visuals()
        self.__create_visuals()
        self.__attach_visuals()
        self.__title_overlay_visual_text()

        return True

    def toggle_input_colourspace_out_of_gamut_colours_display_action(self):
        self.__detach_visuals()
        self.__display_input_colourspace_out_of_gamut = (
            not self.__display_input_colourspace_out_of_gamut)
        if self.__display_input_colourspace_out_of_gamut:
            self.__display_correlate_colourspace_out_of_gamut = False
            self.__display_hdr_colours = False
        self.__create_visuals()
        self.__attach_visuals()
        self.__title_overlay_visual_text()

        return True

    def toggle_correlate_colourspace_out_of_gamut_colours_display_action(self):
        self.__detach_visuals()
        self.__display_correlate_colourspace_out_of_gamut = (
            not self.__display_correlate_colourspace_out_of_gamut)
        if self.__display_correlate_colourspace_out_of_gamut:
            self.__display_input_colourspace_out_of_gamut = False
            self.__display_out_of_pointer_gamut = False
            self.__display_hdr_colours = False
        self.__create_visuals()
        self.__attach_visuals()
        self.__title_overlay_visual_text()

        return True

    def toggle_out_of_pointer_gamut_colours_display_action(self):
        self.__detach_visuals()
        self.__display_out_of_pointer_gamut = (
            not self.__display_out_of_pointer_gamut)
        if self.__display_out_of_pointer_gamut:
            self.__display_input_colourspace_out_of_gamut = False
            self.__display_correlate_colourspace_out_of_gamut = False
            self.__display_hdr_colours = False
        self.__create_visuals()
        self.__attach_visuals()
        self.__title_overlay_visual_text()

        return True

    def toggle_hdr_colours_display_action(self):
        self.__detach_visuals()
        self.__display_hdr_colours = (
            not self.__display_hdr_colours)
        if self.__display_hdr_colours:
            self.__display_input_colourspace_out_of_gamut = False
            self.__display_correlate_colourspace_out_of_gamut = False
            self.__display_out_of_pointer_gamut = False
        self.__create_visuals()
        self.__attach_visuals()
        self.__title_overlay_visual_text()

        return True

    def toggle_image_overlay_display_action(self):
        self.__image_overlay = not self.__image_overlay
        self.__detach_visuals()
        self.__create_visuals()
        self.__attach_visuals()
        self.__title_overlay_visual_text()

    def fit_image_visual_image_action(self):
        # TODO: Implement definition.

        print('fit_image_visual_image')

        return True

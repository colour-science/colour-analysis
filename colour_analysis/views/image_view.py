# -*- coding: utf-8 -*-
"""
Image View
==========

Defines the *Image View* related objects:

-   :class:`ImageView`
"""

from __future__ import division, unicode_literals

import numpy as np

from vispy.scene.cameras import PanZoomCamera
from vispy.scene.widgets import Label, ViewBox, Widget

from colour import (RGB_COLOURSPACES, RGB_to_RGB, RGB_to_XYZ,
                    is_within_pointer_gamut)
from colour.utilities import is_string, tstack

from colour_analysis.constants import DEFAULT_ENCODING_CCTF
from colour_analysis.visuals import image_visual

__author__ = 'Colour Developers'
__copyright__ = 'Copyright (C) 2013-2019 - Colour Developers'
__license__ = 'New BSD License - http://opensource.org/licenses/BSD-3-Clause'
__maintainer__ = 'Colour Developers'
__email__ = 'colour-science@googlegroups.com'
__status__ = 'Production'

__all__ = ['ImageView']


class ImageView(ViewBox):
    """
    Defines the *Diagram View*.

    Parameters
    ----------
    scene_canvas : SceneCanvas, optional
        Current `vispy.scene.SceneCanvas` instance.
    image : array_like, optional
        Image to use in the view interactions.
    input_colourspace : unicode, optional
        **{'ITU-R BT.709', 'ACES2065-1', 'ACEScc', 'ACEScg', 'ACESproxy',
        'ALEXA Wide Gamut', 'Adobe RGB (1998)', 'Adobe Wide Gamut RGB',
        'Apple RGB', 'Best RGB', 'Beta RGB', 'CIE RGB', 'Cinema Gamut',
        'ColorMatch RGB', 'DCI-P3', 'DCI-P3+', 'DRAGONcolor', 'DRAGONcolor2',
        'Don RGB 4', 'ECI RGB v2', 'ERIMM RGB', 'Ekta Space PS 5', 'Max RGB',
        'NTSC', 'Pal/Secam', 'ProPhoto RGB', 'REDcolor', 'REDcolor2',
        'REDcolor3', 'REDcolor4', 'RIMM RGB', 'ROMM RGB', 'ITU-R BT.2020',
        'Russell RGB', 'S-Gamut', 'S-Gamut3', 'S-Gamut3.Cine', 'SMPTE-C RGB',
        'V-Gamut', 'Xtreme RGB', 'sRGB'}**,
        :class:`colour.RGB_Colourspace` class instance name defining the
        `image` argument colourspace.
    correlate_colourspace : unicode, optional
        See `input_colourspace` argument for possible values, default value is
        *ACEScg*.

        :class:`colour.RGB_Colourspace` class instance name defining the
        comparison / correlate colourspace.

    Other Parameters
    ----------------
    \\**kwargs : dict, optional
        Keywords arguments passed to
        :class:`vispy.scene.widgets.viewbox.Viewbox` class constructor.

    Attributes
    ----------
    scene_canvas
    image
    input_colourspace
    correlate_colourspace

    Methods
    -------
    toggle_input_colourspace_out_of_gamut_colours_display_action
    toggle_correlate_colourspace_out_of_gamut_colours_display_action
    toggle_out_of_pointer_gamut_colours_display_action
    toggle_hdr_colours_display_action
    toggle_image_overlay_display_action
    fit_image_visual_image_action
    """

    def __init__(self,
                 scene_canvas=None,
                 image=None,
                 input_colourspace='ITU-R BT.709',
                 correlate_colourspace='ACEScg',
                 **kwargs):
        self._initialised = False

        ViewBox.__init__(self, **kwargs)

        self.unfreeze()

        self._scene_canvas = scene_canvas

        self._image = None
        self.image = image
        self._input_colourspace = None
        self.input_colourspace = input_colourspace
        self._correlate_colourspace = None
        self.correlate_colourspace = correlate_colourspace

        self._grid = None

        self._label = None

        self._image_visual = None

        self._image_overlay = True

        self._display_input_colourspace_out_of_gamut = False
        self._display_correlate_colourspace_out_of_gamut = False
        self._display_out_of_pointer_gamut = False
        self._display_hdr_colours = False

        self._create_visuals()
        self._attach_visuals()
        self._create_camera()

        self._create_label()

        self._initialised = True

    @property
    def scene_canvas(self):
        """
        Property for **self.scene_canvas** attribute.

        Returns
        -------
        SceneCanvas
        """

        return self._scene_canvas

    @property
    def image(self):
        """
        Property for **self._image** private attribute.

        Returns
        -------
        array_like
            self._image.
        """

        return self._image

    @image.setter
    def image(self, value):
        """
        Setter for **self._image** private attribute.

        Parameters
        ----------
        value : array_like
            Attribute value.
        """

        if value is not None:
            assert isinstance(value, (tuple, list, np.ndarray, np.matrix)), ((
                '"{0}" attribute: "{1}" is not a "tuple", "list", "ndarray" '
                'or "matrix" instance!').format('image', value))

        self._image = value

        if self._initialised:
            self._detach_visuals()
            self._create_visuals()
            self._attach_visuals()
            self._label_text()

    @property
    def input_colourspace(self):
        """
        Property for **self._input_colourspace** private attribute.

        Returns
        -------
        unicode
            self._input_colourspace.
        """

        return self._input_colourspace

    @input_colourspace.setter
    def input_colourspace(self, value):
        """
        Setter for **self._input_colourspace** private attribute.

        Parameters
        ----------
        value : unicode
            Attribute value.
        """

        if value is not None:
            assert is_string(value), (('"{0}" attribute: "{1}" is not a '
                                       '"string" like object!').format(
                                           'input_colourspace', value))
            assert value in RGB_COLOURSPACES, (
                '"{0}" colourspace not found in factory RGB colourspaces: '
                '"{1}".').format(value, ', '.join(
                    sorted(RGB_COLOURSPACES.keys())))

        self._input_colourspace = value

        if self._initialised:
            self._detach_visuals()
            self._create_visuals()
            self._attach_visuals()
            self._label_text()

    @property
    def correlate_colourspace(self):
        """
        Property for **self._correlate_colourspace** private attribute.

        Returns
        -------
        unicode
            self._correlate_colourspace.
        """

        return self._correlate_colourspace

    @correlate_colourspace.setter
    def correlate_colourspace(self, value):
        """
        Setter for **self._correlate_colourspace** private attribute.

        Parameters
        ----------
        value : unicode
            Attribute value.
        """

        if value is not None:
            assert is_string(value), (('"{0}" attribute: "{1}" is not a '
                                       '"string" like object!').format(
                                           'correlate_colourspace', value))
            assert value in RGB_COLOURSPACES, (
                '"{0}" colourspace not found in factory RGB colourspaces: '
                '"{1}".').format(value, ', '.join(
                    sorted(RGB_COLOURSPACES.keys())))

        self._correlate_colourspace = value

        if self._initialised:
            self._detach_visuals()
            self._create_visuals()
            self._attach_visuals()
            self._label_text()

    def _create_image(self):
        """
        Creates the image used by the *Image View* according to
        :attr:`GamutView._display_input_colourspace_out_of_gamut`,
        :attr:`GamutView._display_correlate_colourspace_out_of_gamut`,
        :attr:`GamutView._display_out_of_pointer_gamut` and
        :attr:`GamutView._display_hdr_colours` attributes values.

        Returns
        -------
        ndarray
            Image
        """

        image = np.copy(self._image)

        has_overlay = False
        if (self._display_input_colourspace_out_of_gamut
                or self._display_correlate_colourspace_out_of_gamut):
            image[image >= 0] = 0
            image[image < 0] = 1
            has_overlay = True

        if self._display_correlate_colourspace_out_of_gamut:
            image = RGB_to_RGB(image,
                               RGB_COLOURSPACES[self._input_colourspace],
                               RGB_COLOURSPACES[self._correlate_colourspace])
            has_overlay = True

        if self._display_out_of_pointer_gamut:
            colourspace = RGB_COLOURSPACES[self._input_colourspace]
            image = is_within_pointer_gamut(
                RGB_to_XYZ(image, colourspace.whitepoint,
                           colourspace.whitepoint,
                           colourspace.RGB_to_XYZ_matrix)).astype(int)

            # TODO: Investigate why stacking implies that image needs to be
            # inverted.
            image = 1 - tstack([image, image, image])
            has_overlay = True

        if self._display_hdr_colours:
            image[image <= 1] = 0
            # has_overlay = True

        if self._image_overlay and has_overlay:
            image = self._image + image

        oecf = RGB_COLOURSPACES[DEFAULT_ENCODING_CCTF].encoding_cctf

        return oecf(image)

    def _create_visuals(self):
        """
        Creates the *Image View* visuals.
        """

        self._image_visual = image_visual(self._create_image())

    def _create_camera(self):
        """
        Creates the *Image View* camera.
        """

        self.camera = PanZoomCamera(aspect=1)
        self.camera.flip = (False, True, False)
        self.camera._set_range(False)

    def _attach_visuals(self):
        """
        Attaches / parents the visuals to the *Image View* scene.
        """

        self._image_visual.parent = self.scene

    def _detach_visuals(self):
        """
        Detaches / un-parents the visuals from the *Image View* scene.
        """

        self._image_visual.parent = None

    def _create_label(self):
        """
        Creates the label.
        """

        self._label = Label(str(), color=(0.8, 0.8, 0.8))
        self._label.stretch = (1, 0.1)
        self._grid = self.add_grid(margin=16)
        self._grid.add_widget(self._label, row=0, col=0)
        self._grid.add_widget(Widget(), row=1, col=0)

        self._label_text()

    def _label_text(self):
        """
        Sets the label text.
        """

        self._label.text = str()

        if self._display_input_colourspace_out_of_gamut:
            self._label.text = ('{0} - Out of Gamut Colours Display'.format(
                self._input_colourspace))

        if self._display_correlate_colourspace_out_of_gamut:
            self._label.text = ('{0} - Out of Gamut Colours Display'.format(
                self._correlate_colourspace))

        if self._display_out_of_pointer_gamut:
            self._label.text = ('Out of Pointer\'s Gamut ' 'Colours Display')

        if self._display_hdr_colours:
            self._label.text = 'HDR Colours Display'

    def toggle_input_colourspace_out_of_gamut_colours_display_action(self):
        """
        Defines the slot triggered by the
        *toggle_input_colourspace_out_of_gamut_colours_display* action.

        Returns
        -------
        bool
            Definition success.
        """

        self._detach_visuals()
        self._display_input_colourspace_out_of_gamut = (
            not self._display_input_colourspace_out_of_gamut)
        if self._display_input_colourspace_out_of_gamut:
            self._display_correlate_colourspace_out_of_gamut = False
            self._display_hdr_colours = False
        self._create_visuals()
        self._attach_visuals()
        self._label_text()

        return True

    def toggle_correlate_colourspace_out_of_gamut_colours_display_action(self):
        """
        Defines the slot triggered by the
        *toggle_correlate_colourspace_out_of_gamut_colours_display* action.

        Returns
        -------
        bool
            Definition success.
        """

        self._detach_visuals()
        self._display_correlate_colourspace_out_of_gamut = (
            not self._display_correlate_colourspace_out_of_gamut)
        if self._display_correlate_colourspace_out_of_gamut:
            self._display_input_colourspace_out_of_gamut = False
            self._display_out_of_pointer_gamut = False
            self._display_hdr_colours = False
        self._create_visuals()
        self._attach_visuals()
        self._label_text()

        return True

    def toggle_out_of_pointer_gamut_colours_display_action(self):
        """
        Defines the slot triggered by the
        *toggle_out_of_pointer_gamut_colours_display* action.

        Returns
        -------
        bool
            Definition success.
        """

        self._detach_visuals()
        self._display_out_of_pointer_gamut = (
            not self._display_out_of_pointer_gamut)
        if self._display_out_of_pointer_gamut:
            self._display_input_colourspace_out_of_gamut = False
            self._display_correlate_colourspace_out_of_gamut = False
            self._display_hdr_colours = False
        self._create_visuals()
        self._attach_visuals()
        self._label_text()

        return True

    def toggle_hdr_colours_display_action(self):
        """
        Defines the slot triggered by the *toggle_hdr_colours_display* action.

        Returns
        -------
        bool
            Definition success.
        """

        self._detach_visuals()
        self._display_hdr_colours = (not self._display_hdr_colours)
        if self._display_hdr_colours:
            self._display_input_colourspace_out_of_gamut = False
            self._display_correlate_colourspace_out_of_gamut = False
            self._display_out_of_pointer_gamut = False
        self._create_visuals()
        self._attach_visuals()
        self._label_text()

        return True

    def toggle_image_overlay_display_action(self):
        """
        Defines the slot triggered by the *toggle_image_overlay_display*
        action.

        Returns
        -------
        bool
            Definition success.
        """

        self._image_overlay = not self._image_overlay
        self._detach_visuals()
        self._create_visuals()
        self._attach_visuals()
        self._label_text()

    def fit_image_visual_image_action(self):
        """
        Defines the slot triggered by the *fit_image_visual_image* action.

        Returns
        -------
        bool
            Definition success.
        """

        # TODO: Implement definition.

        print('fit_image_visual_image')

        return True

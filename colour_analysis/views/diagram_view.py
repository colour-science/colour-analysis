#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Diagram View
============

Defines the *Diagram View* related objects:

-   :class:`DiagramView`
"""

from __future__ import division, unicode_literals

import numpy as np
from collections import OrderedDict

from vispy.scene.cameras import PanZoomCamera
from vispy.scene.visuals import GridLines, Text
from vispy.scene.widgets.viewbox import ViewBox

from colour import RGB_COLOURSPACES

from colour_analysis.constants import (
    CHROMATICITY_DIAGRAMS,
    CHROMATICITY_DIAGRAM_TO_REFERENCE_COLOURSPACE)
from colour_analysis.utilities import Cycle
from colour_analysis.visuals import (
    CIE_1931_chromaticity_diagram,
    CIE_1960_UCS_chromaticity_diagram,
    CIE_1976_UCS_chromaticity_diagram,
    RGB_colourspace_triangle_visual,
    RGB_scatter_visual,
    axis_visual,
    pointer_gamut_boundaries_visual,
    pointer_gamut_visual,
    spectral_locus_visual)

__author__ = 'Colour Developers'
__copyright__ = 'Copyright (C) 2013 - 2015 - Colour Developers'
__license__ = 'New BSD License - http://opensource.org/licenses/BSD-3-Clause'
__maintainer__ = 'Colour Developers'
__email__ = 'colour-science@googlegroups.com'
__status__ = 'Production'

__all__ = ['DiagramView']


class DiagramView(ViewBox):
    """
    Defines the *Diagram View*.

    Parameters
    ----------
    canvas : SceneCanvas, optional
        Current `vispy.scene.SceneCanvas` instance.
    image : array_like, optional
        Image to use in the view interactions.
    oecf : unicode, optional
        {'Rec. 709', 'ACES2065-1', 'ACEScc', 'ACEScg', 'ACESproxy',
        'ALEXA Wide Gamut RGB', 'Adobe RGB 1998', 'Adobe Wide Gamut RGB',
        'Apple RGB', 'Best RGB', 'Beta RGB', 'CIE RGB', 'Cinema Gamut',
        'ColorMatch RGB', 'DCI-P3', 'DCI-P3+', 'DRAGONcolor', 'DRAGONcolor2',
        'Don RGB 4', 'ECI RGB v2', 'Ekta Space PS 5', 'Max RGB', 'NTSC RGB',
        'Pal/Secam RGB', 'ProPhoto RGB', 'REDcolor', 'REDcolor2', 'REDcolor3',
        'REDcolor4', 'Rec. 2020', 'Russell RGB', 'S-Gamut', 'S-Gamut3',
        'S-Gamut3.Cine', 'SMPTE-C RGB', 'V-Gamut', 'Xtreme RGB', 'aces',
        'adobe1998', 'prophoto', 'sRGB'}

        :class:`colour.RGB_Colourspace` class instance name defining the image
        opto-electronic conversion function.
    input_colourspace : unicode, optional
        See `oecf` argument for possible values.

        :class:`colour.RGB_Colourspace` class instance name defining the
        `image` argument colourspace.
    correlate_colourspace : unicode, optional
        See `oecf` argument for possible values, default value is *ACEScg*.

        :class:`colour.RGB_Colourspace` class instance name defining the
        comparison / correlate colourspace.
    diagram : unicode, optional
        {'CIE 1931', 'CIE 1960 UCS', 'CIE 1976 UCS'}

        Chromaticity diagram to draw.
    \*\*kwargs : \*\*, optional
        Keywords arguments passed to
        :class:`vispy.scene.widgets.viewbox.Viewbox` class constructor.

    Attributes
    ----------
    canvas
    image
    oecf
    input_colourspace
    correlate_colourspace
    diagram

    Methods
    -------
    toggle_spectral_locus_visual_visibility_action
    toggle_input_colourspace_visual_visibility_action
    toggle_correlate_colourspace_visual_visibility_action
    toggle_RGB_scatter_visual_visibility_action
    toggle_pointer_gamut_visual_visibility_action
    toggle_grid_visual_visibility_action
    toggle_axis_visual_visibility_action
    cycle_chromaticity_diagram_action
    toggle_blacks_clamp_action
    toggle_whites_clamp_action
    """

    def __init__(self,
                 canvas=None,
                 image=None,
                 oecf='Rec. 709',
                 input_colourspace='Rec. 709',
                 correlate_colourspace='ACEScg',
                 diagram='CIE 1931',
                 **kwargs):
        self.__initialised = False

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
        self.__diagram = None
        self.diagram = diagram

        self.__diagrams_cycle = Cycle(CHROMATICITY_DIAGRAMS)

        self.__title_overlay_visual = None

        self.__chromaticity_diagram = None
        self.__spectral_locus_visual = None
        self.__RGB_scatter_visual = None
        self.__input_colourspace_visual = None
        self.__correlate_colourspace_visual = None
        self.__pointer_gamut_visual = None
        self.__pointer_gamut_boundaries_visual = None
        self.__grid_visual = None
        self.__axis_visual = None

        self.__clamp_blacks = False
        self.__clamp_whites = False

        self.__create_visuals()
        self.__attach_visuals()
        self.__create_camera()

        self.__create_title_overlay_visual()
        self.__canvas.events.resize.connect(self.__canvas_resize_event)

        self.__initialised = True

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

        if self.__initialised:
            self.__detach_visuals()
            self.__create_input_colourspace_visual()
            self.__attach_visuals()
            self.__title_overlay_visual_text()

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

        if self.__initialised:
            self.__detach_visuals()
            self.__create_correlate_colourspace_visual()
            self.__attach_visuals()
            self.__title_overlay_visual_text()

    @property
    def diagram(self):
        """
        Property for **self.__diagram** private attribute.

        Returns
        -------
        unicode
            self.__diagram.
        """

        return self.__diagram

    @diagram.setter
    def diagram(self, value):
        """
        Setter for **self.__diagram** private attribute.

        Parameters
        ----------
        value : unicode
            Attribute value.
        """

        if value is not None:
            assert type(value) in (str, unicode), (
                ('"{0}" attribute: "{1}" type is not '
                 '"str" or "unicode"!').format('diagram', value))
            assert value in CHROMATICITY_DIAGRAMS, (
                '"{0}" diagram not found in factory chromaticity diagrams: '
                '"{1}".').format(value, ', '.join(
                sorted(CHROMATICITY_DIAGRAMS.keys())))

        if self.__initialised:
            self.__store_visuals_visibility()
            self.__detach_visuals()

        self.__diagram = value

        if self.__initialised:
            self.__create_visuals()
            self.__attach_visuals()
            self.__restore_visuals_visibility()
            self.__title_overlay_visual_text()

    def __create_image(self):
        """
        Creates the image used by the *Diagram View* according to
        :attr:`DiagramView.__clamp_blacks` or
        :attr:`DiagramView.__clamp_whites` attributes values.

        Returns
        -------
        ndarray
            Image
        """

        image = self.__image

        if self.__clamp_blacks:
            image = np.clip(image, 0, np.inf)

        if self.__clamp_whites:
            image = np.clip(image, -np.inf, 1)

        return image

    def __create_chromaticity_diagram_visual(self, diagram='CIE 1931'):
        """
        Creates the given chromaticity diagram visual.

        Parameters
        ----------
        diagram : unicode
            {'CIE 1931', 'CIE 1960 UCS', 'CIE 1976 UCS'}

            Chromaticity diagram to draw.
        """

        diagrams = {'CIE 1931': CIE_1931_chromaticity_diagram,
                    'CIE 1960 UCS': CIE_1960_UCS_chromaticity_diagram,
                    'CIE 1976 UCS': CIE_1976_UCS_chromaticity_diagram}

        self.__chromaticity_diagram = diagrams[diagram]()

    def __create_spectral_locus_visual(self):
        """
        Creates the spectral locus visual according to
        :attr:`DiagramView.diagram` attribute value.
        """

        self.__spectral_locus_visual = spectral_locus_visual(
            reference_colourspace=(
                CHROMATICITY_DIAGRAM_TO_REFERENCE_COLOURSPACE[self.__diagram]),
            uniform_colour=(0.0, 0.0, 0.0),
            width=2.0,
            method='agg')

    def __create_RGB_scatter_visual(self, RGB):
        """
        Creates the *RGB* scatter visual for given *RGB* array according to
        :attr:`DiagramView.diagram` attribute value.

        Parameters
        ----------
        RGB : array_like
            *RGB* array to draw.
        """

        self.__RGB_scatter_visual = RGB_scatter_visual(
            RGB,
            reference_colourspace=(
                CHROMATICITY_DIAGRAM_TO_REFERENCE_COLOURSPACE[self.__diagram]),
            uniform_colour=(0.0, 0.0, 0.0))

    def __create_pointer_gamut_visual(self):
        """
        Creates the *Pointer's Gamut* visual according to
        :attr:`DiagramView.diagram` attribute value.
        """

        self.__pointer_gamut_visual = pointer_gamut_visual(
            reference_colourspace=(
                CHROMATICITY_DIAGRAM_TO_REFERENCE_COLOURSPACE[self.__diagram]),
            uniform_opacity=0.4)

    def __create_pointer_gamut_boundaries_visual(self):
        """
        Creates the *Pointer's Gamut* boundaries visual according to
        :attr:`DiagramView.diagram` attribute value.
        """

        self.__pointer_gamut_boundaries_visual = (
            pointer_gamut_boundaries_visual(reference_colourspace=(
                CHROMATICITY_DIAGRAM_TO_REFERENCE_COLOURSPACE[
                    self.__diagram])))

    def __create_input_colourspace_visual(self):
        """
        Creates the input colourspace visual according to
        :attr:`DiagramView.input_colourspace` attribute value.
        """

        self.__input_colourspace_visual = RGB_colourspace_triangle_visual(
            self.__input_colourspace,
            self.__diagram,
            uniform_colour=(0.8, 0.0, 0.8))

    def __create_correlate_colourspace_visual(self):
        """
        Creates the correlate colourspace visual according to
        :attr:`DiagramView.correlate_colourspace` attribute value.
        """

        self.__correlate_colourspace_visual = RGB_colourspace_triangle_visual(
            self.__correlate_colourspace,
            self.__diagram,
            uniform_colour=(0.0, 0.8, 0.8))

    def __create_grid_visual(self):
        """
        Creates the grid visual.
        """

        self.__grid_visual = GridLines()

    def __create_axis_visual(self):
        """
        Creates the axis visual.
        """

        self.__axis_visual = axis_visual()

    def __create_visuals(self):
        """
        Creates the *Diagram View* visuals.
        """

        self.__create_chromaticity_diagram_visual(self.__diagram)
        self.__create_spectral_locus_visual()
        self.__create_RGB_scatter_visual(self.__create_image())
        self.__create_pointer_gamut_visual()
        self.__create_pointer_gamut_boundaries_visual()
        self.__create_input_colourspace_visual()
        self.__create_correlate_colourspace_visual()
        self.__create_grid_visual()
        self.__create_axis_visual()

    def __create_camera(self):
        """
        Creates the *Diagram View* camera.
        """

        self.camera = PanZoomCamera(rect=(-0.1, -0.1, 1.1, 1.1),
                                    aspect=1)

    def __attach_visuals(self):
        """
        Attaches / parents the visuals to the *Diagram View* scene.
        """

        self.__chromaticity_diagram.add_parent(self.scene)
        self.__spectral_locus_visual.add_parent(self.scene)
        self.__RGB_scatter_visual.add_parent(self.scene)
        self.__pointer_gamut_visual.add_parent(self.scene)
        self.__pointer_gamut_boundaries_visual.add_parent(self.scene)
        self.__input_colourspace_visual.add_parent(self.scene)
        self.__correlate_colourspace_visual.add_parent(self.scene)
        self.__grid_visual.add_parent(self.scene)
        self.__axis_visual.add_parent(self.scene)

    def __detach_visuals(self):
        """
        Detaches / un-parents the visuals from the *Diagram View* scene.
        """

        self.__chromaticity_diagram.remove_parent(self.scene)
        self.__spectral_locus_visual.remove_parent(self.scene)
        self.__RGB_scatter_visual.remove_parent(self.scene)
        self.__pointer_gamut_visual.remove_parent(self.scene)
        self.__pointer_gamut_boundaries_visual.remove_parent(self.scene)
        self.__input_colourspace_visual.remove_parent(self.scene)
        self.__correlate_colourspace_visual.remove_parent(self.scene)
        self.__grid_visual.remove_parent(self.scene)
        self.__axis_visual.remove_parent(self.scene)

    def __store_visuals_visibility(self):
        """
        Stores visuals visibility in :attr:`DiagramView.__visuals_visibility`
        attribute.
        """

        visible = OrderedDict()
        visible['chromaticity_diagram_visual'] = (
            self.__chromaticity_diagram.visible)
        visible['spectral_locus_visual'] = (
            self.__spectral_locus_visual.visible)
        visible['RGB_scatter_visual'] = (
            self.__RGB_scatter_visual.visible)
        visible['pointer_gamut_visual'] = (
            self.__pointer_gamut_visual.visible)
        visible['pointer_gamut_boundaries_visual'] = (
            self.__pointer_gamut_boundaries_visual.visible)
        visible['input_colourspace_visual'] = (
            self.__input_colourspace_visual.visible)
        visible['correlate_colourspace_visual'] = (
            self.__correlate_colourspace_visual.visible)
        visible['grid_visual'] = (
            self.__grid_visual.visible)
        visible['axis_visual'] = (
            self.__axis_visual.visible)

        self.__visuals_visibility = visible

    def __restore_visuals_visibility(self):
        """
        Restores visuals visibility from
        :attr:`DiagramView.__visuals_visibility` attribute.
        """

        visible = self.__visuals_visibility

        self.__chromaticity_diagram.visible = (
            visible['chromaticity_diagram_visual'])
        self.__spectral_locus_visual.visible = (
            visible['spectral_locus_visual'])
        self.__RGB_scatter_visual.visible = (
            visible['RGB_scatter_visual'])
        self.__pointer_gamut_visual.visible = (
            visible['pointer_gamut_visual'])
        self.__pointer_gamut_boundaries_visual.visible = (
            visible['pointer_gamut_boundaries_visual'])
        self.__input_colourspace_visual.visible = (
            visible['input_colourspace_visual'])
        self.__correlate_colourspace_visual.visible = (
            visible['correlate_colourspace_visual'])
        self.__grid_visual.visible = (
            visible['grid_visual'])
        self.__axis_visual.visible = (
            visible['axis_visual'])

    def __create_title_overlay_visual(self):
        """
        Creates the title overlay visual.
        """

        self.__title_overlay_visual = Text(str(),
                                           anchor_x='center',
                                           anchor_y='bottom',
                                           font_size=10,
                                           color=(0.8, 0.8, 0.8),
                                           parent=self)

        self.__title_overlay_visual_position()
        self.__title_overlay_visual_text()

    def __title_overlay_visual_position(self):
        """
        Sets the title overlay visual position.
        """

        self.__title_overlay_visual.pos = self.size[0] / 2, 32

    def __title_overlay_visual_text(self):
        """
        Sets the title overlay visual text.
        """

        title = ''

        if self.__input_colourspace_visual.visible:
            title += self.__input_colourspace
            title += ' - '
        if self.__correlate_colourspace_visual.visible:
            title += self.__correlate_colourspace
            title += ' - '

        title += '{0} Chromaticity Diagram'.format(self.__diagram)

        if self.__clamp_blacks:
            title += ' - '
            title += 'Blacks Clamped'

        if self.__clamp_whites:
            title += ' - '
            title += 'Whites Clamped'

        self.__title_overlay_visual.text = title

    def __canvas_resize_event(self, event=None):
        """
        Slot for current :class:`vispy.scene.SceneCanvas` instance resize
        event.

        Parameters
        ----------
        event : Object
            Event.
        """

        self.__title_overlay_visual_position()

    def toggle_spectral_locus_visual_visibility_action(self):
        """
        Defines the slot triggered by the
        *toggle_spectral_locus_visual_visibility* action.

        Returns
        -------
        bool
            Definition success.
        """

        self.__spectral_locus_visual.visible = (
            not self.__spectral_locus_visual.visible)

        return True

    def toggle_input_colourspace_visual_visibility_action(self):
        """
        Defines the slot triggered by the
        *toggle_input_colourspace_visual_visibility* action.

        Returns
        -------
        bool
            Definition success.
        """

        self.__input_colourspace_visual.visible = (
            not self.__input_colourspace_visual.visible)
        self.__title_overlay_visual_text()

        return True

    def toggle_correlate_colourspace_visual_visibility_action(self):
        """
        Defines the slot triggered by the
        *toggle_correlate_colourspace_visual_visibility* action.

        Returns
        -------
        bool
            Definition success.
        """

        self.__correlate_colourspace_visual.visible = (
            not self.__correlate_colourspace_visual.visible)
        self.__title_overlay_visual_text()

        return True

    def toggle_RGB_scatter_visual_visibility_action(self):
        """
        Defines the slot triggered by the
        *toggle_RGB_scatter_visual_visibility* action.

        Returns
        -------
        bool
            Definition success.
        """

        self.__RGB_scatter_visual.visible = (
            not self.__RGB_scatter_visual.visible)

        return True

    def toggle_pointer_gamut_visual_visibility_action(self):
        """
        Defines the slot triggered by the
        *toggle_pointer_gamut_visual_visibility* action.

        Returns
        -------
        bool
            Definition success.
        """

        self.__pointer_gamut_visual.visible = (
            not self.__pointer_gamut_visual.visible)
        self.__pointer_gamut_boundaries_visual.visible = (
            not self.__pointer_gamut_boundaries_visual.visible)

        return True

    def toggle_grid_visual_visibility_action(self):
        """
        Defines the slot triggered by the *toggle_grid_visual_visibility*
        action.

        Returns
        -------
        bool
            Definition success.
        """

        self.__grid_visual.visible = not self.__grid_visual.visible

        return True

    def toggle_axis_visual_visibility_action(self):
        """
        Defines the slot triggered by the *toggle_axis_visual_visibility*
        action.

        Returns
        -------
        bool
            Definition success.
        """

        self.__axis_visual.visible = (
            not self.__axis_visual.visible)

        return True

    def cycle_chromaticity_diagram_action(self):
        """
        Defines the slot triggered by the *cycle_chromaticity_diagram* action.

        Returns
        -------
        bool
            Definition success.
        """

        self.diagram = self.__diagrams_cycle.next_item()

        return True

    def toggle_blacks_clamp_action(self):
        """
        Defines the slot triggered by the *toggle_blacks_clamp* action.

        Returns
        -------
        bool
            Definition success.
        """

        self.__clamp_blacks = not self.__clamp_blacks
        self.__store_visuals_visibility()
        self.__detach_visuals()
        self.__create_RGB_scatter_visual(self.__create_image())
        self.__attach_visuals()
        self.__restore_visuals_visibility()
        self.__title_overlay_visual_text()

        return True

    def toggle_whites_clamp_action(self):
        """
        Defines the slot triggered by the *toggle_whites_clamp* action.

        Returns
        -------
        bool
            Definition success.
        """

        self.__clamp_whites = not self.__clamp_whites
        self.__store_visuals_visibility()
        self.__detach_visuals()
        self.__create_RGB_scatter_visual(self.__create_image())
        self.__attach_visuals()
        self.__restore_visuals_visibility()
        self.__title_overlay_visual_text()

        return True

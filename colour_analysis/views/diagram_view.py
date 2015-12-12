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
from vispy.scene.visuals import GridLines
from vispy.scene.widgets import Label, ViewBox, Widget

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
    scene_canvas : SceneCanvas, optional
        Current `vispy.scene.SceneCanvas` instance.
    image : array_like, optional
        Image to use in the view interactions.
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
    \**kwargs : dict, optional
        Keywords arguments passed to
        :class:`vispy.scene.widgets.viewbox.Viewbox` class constructor.

    Attributes
    ----------
    scene_canvas
    image
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
    """

    def __init__(self,
                 scene_canvas=None,
                 image=None,
                 input_colourspace='Rec. 709',
                 correlate_colourspace='ACEScg',
                 diagram='CIE 1931',
                 **kwargs):
        self.__initialised = False

        ViewBox.__init__(self, **kwargs)

        self.unfreeze()

        self.__scene_canvas = scene_canvas

        self.__image = None
        self.image = image
        self.__input_colourspace = None
        self.input_colourspace = input_colourspace
        self.__correlate_colourspace = None
        self.correlate_colourspace = correlate_colourspace
        self.__diagram = None
        self.diagram = diagram

        self.__diagrams_cycle = Cycle(CHROMATICITY_DIAGRAMS)

        self.__grid = None

        self.__label = None

        self.__chromaticity_diagram_visual = None
        self.__spectral_locus_visual = None
        self.__RGB_scatter_visual = None
        self.__input_colourspace_visual = None
        self.__correlate_colourspace_visual = None
        self.__pointer_gamut_visual = None
        self.__pointer_gamut_boundaries_visual = None
        self.__grid_visual = None
        self.__axis_visual = None

        self.__visuals = ('chromaticity_diagram_visual',
                          'spectral_locus_visual',
                          'RGB_scatter_visual',
                          'input_colourspace_visual',
                          'correlate_colourspace_visual',
                          'pointer_gamut_visual',
                          'pointer_gamut_boundaries_visual',
                          'grid_visual',
                          'axis_visual')

        self.__visuals_visibility = None

        self.__create_visuals()
        self.__attach_visuals()
        self.__create_camera()

        self.__create_label()

        self.__initialised = True

    @property
    def scene_canvas(self):
        """
        Property for **self.scene_canvas** attribute.

        Returns
        -------
        SceneCanvas
        """

        return self.__scene_canvas

    @scene_canvas.setter
    def scene_canvas(self, value):
        """
        Setter for **self.scene_canvas** attribute.

        Parameters
        ----------
        value : SceneCanvas
            Attribute value.
        """

        raise AttributeError('"{0}" attribute is read only!'.format(
            'scene_canvas'))

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
            assert isinstance(value, (tuple, list, np.ndarray, np.matrix)), (
                ('"{0}" attribute: "{1}" is not a "tuple", "list", "ndarray" '
                 'or "matrix" instance!').format('image', value))

        self.__image = value

        if self.__initialised:
            self.__store_visuals_visibility()
            self.__detach_visuals()
            self.__create_RGB_scatter_visual(self.__image)
            self.__attach_visuals()
            self.__restore_visuals_visibility()
            self.__label_text()

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
            assert isinstance(value, basestring), (  # noqa
                ('"{0}" attribute: "{1}" is not a '
                 '"basestring" instance!').format('input_colourspace', value))
            assert value in RGB_COLOURSPACES, (
                '"{0}" colourspace not found in factory RGB colourspaces: '
                '"{1}".').format(
                value, ', '.join(sorted(RGB_COLOURSPACES.keys())))

        self.__input_colourspace = value

        if self.__initialised:
            self.__detach_visuals()
            self.__create_input_colourspace_visual()
            self.__attach_visuals()
            self.__label_text()

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
            assert isinstance(value, basestring), (  # noqa
                ('"{0}" attribute: "{1}" is not a '
                 '"basestring" instance!').format(
                    'correlate_colourspace', value))
            assert value in RGB_COLOURSPACES, (
                '"{0}" colourspace not found in factory RGB colourspaces: '
                '"{1}".').format(value, ', '.join(
                sorted(RGB_COLOURSPACES.keys())))
        self.__correlate_colourspace = value

        if self.__initialised:
            self.__detach_visuals()
            self.__create_correlate_colourspace_visual()
            self.__attach_visuals()
            self.__label_text()

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
            assert isinstance(value, basestring), (  # noqa
                ('"{0}" attribute: "{1}" is not a '
                 '"basestring" instance!').format('input_colourspace', value))
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
            self.__label_text()

    def __create_chromaticity_diagram_visual(self, diagram=None):
        """
        Creates the given chromaticity diagram visual.

        Parameters
        ----------
        diagram : unicode, optional
            {'CIE 1931', 'CIE 1960 UCS', 'CIE 1976 UCS'}

            Chromaticity diagram to draw.
        """

        diagram = self.__diagram if diagram is None else diagram

        diagrams = {'CIE 1931': CIE_1931_chromaticity_diagram,
                    'CIE 1960 UCS': CIE_1960_UCS_chromaticity_diagram,
                    'CIE 1976 UCS': CIE_1976_UCS_chromaticity_diagram}

        self.__chromaticity_diagram_visual = diagrams[diagram]()

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

    def __create_RGB_scatter_visual(self, RGB=None):
        """
        Creates the *RGB* scatter visual for given *RGB* array according to
        :attr:`DiagramView.diagram` attribute value.

        Parameters
        ----------
        RGB : array_like, optional
            *RGB* array to draw.
        """

        RGB = self.__image if RGB is None else RGB

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

        for visual in self.__visuals:
            visual = '_DiagramView__create_{0}'.format(visual)
            getattr(self, visual)()

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

        for visual in self.__visuals:
            visual = '_DiagramView__{0}'.format(visual)
            getattr(self, visual).parent = self.scene

    def __detach_visuals(self):
        """
        Detaches / un-parents the visuals from the *Diagram View* scene.
        """

        for visual in self.__visuals:
            visual = '_DiagramView__{0}'.format(visual)
            getattr(self, visual).parent = None

    def __store_visuals_visibility(self):
        """
        Stores visuals visibility in :attr:`DiagramView.__visuals_visibility`
        attribute.
        """

        visibility = OrderedDict()
        for visual in self.__visuals:
            visibility[visual] = (
                getattr(self, '_DiagramView__{0}'.format(visual)).visible)

        self.__visuals_visibility = visibility

    def __restore_visuals_visibility(self):
        """
        Restores visuals visibility from
        :attr:`DiagramView.__visuals_visibility` attribute.
        """

        visibility = self.__visuals_visibility
        for visual in self.__visuals:
            getattr(self, '_DiagramView__{0}'.format(visual)).visible = (
                visibility[visual])

    def __create_label(self):
        """
        Creates the label.
        """

        self.__label = Label(str(), color=(0.8, 0.8, 0.8))
        self.__label.stretch = (1, 0.1)
        self.__grid = self.add_grid(margin=16)
        self.__grid.add_widget(self.__label, row=0, col=0)
        self.__grid.add_widget(Widget(), row=1, col=0)

        self.__label_text()

    def __label_text(self):
        """
        Sets the label text.
        """

        title = ''

        if self.__input_colourspace_visual.visible:
            title += self.__input_colourspace
            title += ' - '
        if self.__correlate_colourspace_visual.visible:
            title += self.__correlate_colourspace
            title += ' - '

        title += '{0} Chromaticity Diagram'.format(self.__diagram)

        if self.scene_canvas.clamp_blacks:
            title += ' - '
            title += 'Blacks Clamped'

        if self.scene_canvas.clamp_whites:
            title += ' - '
            title += 'Whites Clamped'

        self.__label.text = title

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
        self.__label_text()

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
        self.__label_text()

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

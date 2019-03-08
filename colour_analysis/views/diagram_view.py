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
from colour.utilities import is_string

from colour_analysis.constants import (
    CHROMATICITY_DIAGRAMS, CHROMATICITY_DIAGRAM_TO_REFERENCE_COLOURSPACE)
from colour_analysis.utilities import Cycle
from colour_analysis.visuals import (
    CIE_1931_chromaticity_diagram, CIE_1960_UCS_chromaticity_diagram,
    CIE_1976_UCS_chromaticity_diagram, RGB_colourspace_triangle_visual,
    RGB_scatter_visual, axis_visual, pointer_gamut_boundaries_visual,
    pointer_gamut_visual, spectral_locus_visual)

__author__ = 'Colour Developers'
__copyright__ = 'Copyright (C) 2013-2019 - Colour Developers'
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
        **{'CIE 1931', 'CIE 1960 UCS', 'CIE 1976 UCS'}**,
        Chromaticity diagram to draw.

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
                 input_colourspace='ITU-R BT.709',
                 correlate_colourspace='ACEScg',
                 diagram='CIE 1931',
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
        self._diagram = None
        self.diagram = diagram

        self._diagrams_cycle = Cycle(CHROMATICITY_DIAGRAMS)

        self._grid = None

        self._label = None

        self._chromaticity_diagram_visual = None
        self._spectral_locus_visual = None
        self._RGB_scatter_visual = None
        self._input_colourspace_visual = None
        self._correlate_colourspace_visual = None
        self._pointer_gamut_visual = None
        self._pointer_gamut_boundaries_visual = None
        self._grid_visual = None
        self._axis_visual = None

        self._visuals = ('chromaticity_diagram_visual',
                         'spectral_locus_visual', 'RGB_scatter_visual',
                         'input_colourspace_visual',
                         'correlate_colourspace_visual',
                         'pointer_gamut_visual',
                         'pointer_gamut_boundaries_visual', 'grid_visual',
                         'axis_visual')

        self._visuals_visibility = None

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
            self._store_visuals_visibility()
            self._detach_visuals()
            self._create_RGB_scatter_visual(self._image)
            self._attach_visuals()
            self._restore_visuals_visibility()
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
            self._create_input_colourspace_visual()
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
            self._create_correlate_colourspace_visual()
            self._attach_visuals()
            self._label_text()

    @property
    def diagram(self):
        """
        Property for **self._diagram** private attribute.

        Returns
        -------
        unicode
            self._diagram.
        """

        return self._diagram

    @diagram.setter
    def diagram(self, value):
        """
        Setter for **self._diagram** private attribute.

        Parameters
        ----------
        value : unicode
            Attribute value.
        """

        if value is not None:
            assert is_string(value), (('"{0}" attribute: "{1}" is not a '
                                       '"string" like object!').format(
                                           'input_colourspace', value))
            assert value in CHROMATICITY_DIAGRAMS, (
                '"{0}" diagram not found in factory chromaticity diagrams: '
                '"{1}".').format(value, ', '.join(
                    sorted(CHROMATICITY_DIAGRAMS.keys())))

        if self._initialised:
            self._store_visuals_visibility()
            self._detach_visuals()

        self._diagram = value

        if self._initialised:
            self._create_visuals()
            self._attach_visuals()
            self._restore_visuals_visibility()
            self._label_text()

    def _create_chromaticity_diagram_visual(self, diagram=None):
        """
        Creates the given chromaticity diagram visual.

        Parameters
        ----------
        diagram : unicode, optional
            **{'CIE 1931', 'CIE 1960 UCS', 'CIE 1976 UCS'}**,
            Chromaticity diagram to draw.
        """

        diagram = self._diagram if diagram is None else diagram

        diagrams = {
            'CIE 1931': CIE_1931_chromaticity_diagram,
            'CIE 1960 UCS': CIE_1960_UCS_chromaticity_diagram,
            'CIE 1976 UCS': CIE_1976_UCS_chromaticity_diagram
        }

        self._chromaticity_diagram_visual = diagrams[diagram]()

    def _create_spectral_locus_visual(self):
        """
        Creates the spectral locus visual according to
        :attr:`DiagramView.diagram` attribute value.
        """

        self._spectral_locus_visual = spectral_locus_visual(
            reference_colourspace=(
                CHROMATICITY_DIAGRAM_TO_REFERENCE_COLOURSPACE[self._diagram]),
            uniform_colour=(0.0, 0.0, 0.0),
            width=2.0,
            method='agg')

    def _create_RGB_scatter_visual(self, RGB=None):
        """
        Creates the *RGB* scatter visual for given *RGB* array according to
        :attr:`DiagramView.diagram` attribute value.

        Parameters
        ----------
        RGB : array_like, optional
            *RGB* array to draw.
        """

        RGB = self._image if RGB is None else RGB

        self._RGB_scatter_visual = RGB_scatter_visual(
            RGB,
            reference_colourspace=(
                CHROMATICITY_DIAGRAM_TO_REFERENCE_COLOURSPACE[self._diagram]),
            uniform_colour=(0.0, 0.0, 0.0))

    def _create_pointer_gamut_visual(self):
        """
        Creates the *Pointer's Gamut* visual according to
        :attr:`DiagramView.diagram` attribute value.
        """

        self._pointer_gamut_visual = pointer_gamut_visual(
            reference_colourspace=(
                CHROMATICITY_DIAGRAM_TO_REFERENCE_COLOURSPACE[self._diagram]),
            uniform_opacity=0.4)

    def _create_pointer_gamut_boundaries_visual(self):
        """
        Creates the *Pointer's Gamut* boundaries visual according to
        :attr:`DiagramView.diagram` attribute value.
        """

        self._pointer_gamut_boundaries_visual = (
            pointer_gamut_boundaries_visual(
                reference_colourspace=(
                    CHROMATICITY_DIAGRAM_TO_REFERENCE_COLOURSPACE[
                        self._diagram])))

    def _create_input_colourspace_visual(self):
        """
        Creates the input colourspace visual according to
        :attr:`DiagramView.input_colourspace` attribute value.
        """

        self._input_colourspace_visual = RGB_colourspace_triangle_visual(
            self._input_colourspace,
            self._diagram,
            uniform_colour=(0.8, 0.0, 0.8))

    def _create_correlate_colourspace_visual(self):
        """
        Creates the correlate colourspace visual according to
        :attr:`DiagramView.correlate_colourspace` attribute value.
        """

        self._correlate_colourspace_visual = RGB_colourspace_triangle_visual(
            self._correlate_colourspace,
            self._diagram,
            uniform_colour=(0.0, 0.8, 0.8))

    def _create_grid_visual(self):
        """
        Creates the grid visual.
        """

        self._grid_visual = GridLines()

    def _create_axis_visual(self):
        """
        Creates the axis visual.
        """

        self._axis_visual = axis_visual()

    def _create_visuals(self):
        """
        Creates the *Diagram View* visuals.
        """

        for visual in self._visuals:
            visual = '_create_{0}'.format(visual)
            getattr(self, visual)()

    def _create_camera(self):
        """
        Creates the *Diagram View* camera.
        """

        self.camera = PanZoomCamera(rect=(-0.1, -0.1, 1.1, 1.1), aspect=1)

    def _attach_visuals(self):
        """
        Attaches / parents the visuals to the *Diagram View* scene.
        """

        for visual in self._visuals:
            visual = '_{0}'.format(visual)
            getattr(self, visual).parent = self.scene

    def _detach_visuals(self):
        """
        Detaches / un-parents the visuals from the *Diagram View* scene.
        """

        for visual in self._visuals:
            visual = '_{0}'.format(visual)
            getattr(self, visual).parent = None

    def _store_visuals_visibility(self):
        """
        Stores visuals visibility in :attr:`DiagramView._visuals_visibility`
        attribute.
        """

        visibility = OrderedDict()
        for visual in self._visuals:
            visibility[visual] = getattr(self, '_{0}'.format(visual)).visible

        self._visuals_visibility = visibility

    def _restore_visuals_visibility(self):
        """
        Restores visuals visibility from
        :attr:`DiagramView._visuals_visibility` attribute.
        """

        visibility = self._visuals_visibility
        for visual in self._visuals:
            getattr(self, '_{0}'.format(visual)).visible = (visibility[visual])

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

        title = ''

        if self._input_colourspace_visual.visible:
            title += self._input_colourspace
            title += ' - '
        if self._correlate_colourspace_visual.visible:
            title += self._correlate_colourspace
            title += ' - '

        title += '{0} Chromaticity Diagram'.format(self._diagram)

        if self.scene_canvas.clamp_blacks:
            title += ' - '
            title += 'Blacks Clamped'

        if self.scene_canvas.clamp_whites:
            title += ' - '
            title += 'Whites Clamped'

        self._label.text = title

    def toggle_spectral_locus_visual_visibility_action(self):
        """
        Defines the slot triggered by the
        *toggle_spectral_locus_visual_visibility* action.

        Returns
        -------
        bool
            Definition success.
        """

        self._spectral_locus_visual.visible = (
            not self._spectral_locus_visual.visible)

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

        self._input_colourspace_visual.visible = (
            not self._input_colourspace_visual.visible)
        self._label_text()

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

        self._correlate_colourspace_visual.visible = (
            not self._correlate_colourspace_visual.visible)
        self._label_text()

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

        self._RGB_scatter_visual.visible = (
            not self._RGB_scatter_visual.visible)

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

        self._pointer_gamut_visual.visible = (
            not self._pointer_gamut_visual.visible)
        self._pointer_gamut_boundaries_visual.visible = (
            not self._pointer_gamut_boundaries_visual.visible)

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

        self._grid_visual.visible = not self._grid_visual.visible

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

        self._axis_visual.visible = (not self._axis_visual.visible)

        return True

    def cycle_chromaticity_diagram_action(self):
        """
        Defines the slot triggered by the *cycle_chromaticity_diagram* action.

        Returns
        -------
        bool
            Definition success.
        """

        self.diagram = self._diagrams_cycle.next_item()

        return True

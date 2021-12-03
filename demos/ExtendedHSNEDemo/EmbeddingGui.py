# -*- coding: utf-8 -*-
"""Embedding Gui Classes.

This module implements a number of classes for the display of a
tSNE or other embedding. It supports a number of selection methods
and will return selection events correcpoiding to transient, permanent
and new analysis selections

Classes:
    SelectionEvent
    EmbeddingGui
    EmbeddingViewer

"""
import io
import enum
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.style as mplstyle
from matplotlib.widgets import RectangleSelector, LassoSelector, EllipseSelector, PolygonSelector
from matplotlib.path import Path
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.backend_bases import MouseEvent, KeyEvent
from matplotlib.figure import Figure
from matplotlib import colors
from PyQt5 import QtWidgets, QtCore

from cursors import DrawingCursors, DrawingShape, DrawingMode
from matplotlib.backend_bases import TimerBase
from typing import Dict, Any, List, Tuple, Callable, Union


def calculate_ellipse_path(x1, y1, x2, y2) -> Path:
    """This is how matplotlib draws the ellipse - thanks for the code"""

    xmin, xmax = sorted([x1, x2])
    ymin, ymax = sorted([y1, y2])
    center = [x1 + (x2 - x1) / 2.0, y1 + (y2 - y1) / 2.0]
    a = (xmax - xmin) / 2.0
    b = (ymax - ymin) / 2.0
    rad = np.deg2rad(np.arange(31) * 12)
    x = a * np.cos(rad) + center[0]
    y = b * np.sin(rad) + center[1]
    verts = np.stack((np.transpose(x), np.transpose(y)), 1)
    print(f"Shape verts {verts.shape}")
    return Path(verts)


class SelectionEvent(enum.Enum):
    """The possible selection types from the EmbeddingGui"""

    TRANSIENT = 1  # For example mouse over - just views nearest points
    PERMANENT = 2  # Area selected


class EmbeddingGui(FigureCanvas):
    """This is the matplotlib based GUI for a single analysis
    It assumes the analysis is simple image data (this could be abstracted)"""

    def __init__(self, width=5, height=5) -> None:
        DrawingCursors.init_cursors()
        self.fig = Figure(figsize=(width, height))
        self.ax: plt.Axes = self.fig.add_subplot(111)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        mplstyle.use("fast")
        super(EmbeddingGui, self).__init__(self.fig)
        self.fig.tight_layout(pad=0)
        self.fig.canvas.setFocusPolicy(QtCore.Qt.ClickFocus)  # type: ignore
        self.fig.canvas.setFocus()
        self.draw_state = (DrawingMode.NoDraw, DrawingShape.NoShape)
        self.selection_mask = np.full((0, 0), False)
        self.in_selection = False
        self.facecolors: List[Tuple[float, float, float, float]] = [(0, 0, 0, 0)]
        self.scatter: plt.Axes = None
        self.active_selector = None
        self.setWhatsThis(
            """
    Select keys:
    ============
    A - select all
    D - remove selection
    I - invert selection

    Shaped selector keys:
    =====================
    E - ellipse
    L - lasso
    P - polygon
    R - rectangle
    Space - remove selector

    Selector modifier keys
    ======================
    <Shift> + <selector key> - add selection
    <Ctrl> + <selector key> - subtract selection
            """
        )
        self.selectors: Dict[DrawingShape, Any] = {}
        self.embedding: np.ndarray
        plt.show(block=False)

    def get_canvas_timer(self, interval: int) -> TimerBase:
        """Get a timer for this canvas widget,
        can be used to drive the embedding process"""
        return self.fig.canvas.new_timer(interval)

    def init_plot(
        self,
        embedding: np.ndarray,
        weights: np.ndarray,
        on_selection: Callable[[List[int], bool], None],
        on_close: Callable[[], None],
        disable_select: bool,
        top_level: bool = False,
        labels: Union[np.ndarray, None] = None,
        color_norm: Union[colors.Normalize, None] = None,
    ) -> None:
        """Set the initial embedding and point weights
        to create and display the plot at iteration step=0"""
        # pylint: disable=attribute-defined-outside-init
        self.top_level = top_level
        self.labels = labels
        self.color_norm = color_norm
        self.disable_select = disable_select
        self.selection_mask = np.full(weights.shape, False)

        # Plot and image definition
        # self.rect = None
        self.extent = 2.8
        self.cleanup = True
        self.rectangle_selector = None
        self.lasso_selector = None

        # Callbacks
        self.fig.canvas.mpl_connect("motion_notify_event", self.on_over)
        self.fig.canvas.mpl_connect("key_press_event", self.on_keypress)
        self.fig.canvas.mpl_connect("button_press_event", self.on_start_select)
        self.fig.canvas.mpl_connect("close_event", self.handle_close)

        # Brush support values
        self.in_selection = False
        self.in_paint = False
        self.dim_xy = (None, None)  # displacement
        self.rorg_xy = (None, None)  # The bottom left corner

        print("Show plot")
        plt.show(block=False)  # Need no block for cooperation with tkinter

        self.embedding = embedding
        self.on_selection = on_selection
        self.on_close = on_close
        # pylint: enable=attribute-defined-outside-init
        x = embedding[:, 0]
        y = embedding[:, 1]
        if self.labels is None:
            self.scatter = self.ax.scatter(x, y, s=weights * 8, c="b", alpha=0.4, picker=10)
        else:
            self.scatter = self.ax.scatter(
                x,
                y,
                s=weights * 8,
                c=self.labels,
                # TODO make color map user selectable pylint: disable=fixme
                cmap=plt.cm.rainbow_r,  # # pylint: disable=no-member
                norm=self.color_norm,
                alpha=0.4,
                picker=10,
            )

        self.update_scatter_plot_limits(embedding)

        # Drawing selectors
        rectangle_selector = RectangleSelector(
            self.ax,
            self.on_end_rectangle_select,
            drawtype="box",
            useblit=True,
            button=[1, 3],
            rectprops=dict(facecolor=(1, 0, 0, 0.1), edgecolor=(1, 0, 0, 0.5), fill=False),
            minspanx=5,
            minspany=5,
            spancoords="pixels",
        )
        lasso_selector = LassoSelector(
            self.ax, onselect=self.on_end_lasso_select, lineprops=dict(color=(1, 0, 0, 0.5))
        )
        ellipse_selector = EllipseSelector(
            self.ax,
            onselect=self.on_end_ellipse_select,
            drawtype="line",
            lineprops=dict(color=(1, 0, 0, 0.5)),
        )
        polygon_selector = PolygonSelector(
            self.ax, onselect=self.on_end_lasso_select, lineprops=dict(color=(1, 0, 0, 0.5))
        )

        self.selectors = {
            DrawingShape.Lasso: lasso_selector,
            DrawingShape.Ellipse: ellipse_selector,
            DrawingShape.Rectangle: rectangle_selector,
            DrawingShape.Polygon: polygon_selector,
        }
        # pylint: disable=attribute-defined-outside-init
        self.set_selector()
        # force rendering of facecolors
        self.fig.canvas.draw()
        self.facecolors = self.scatter.get_facecolors()

    def quit(self) -> None:
        """Close the plot and cleanup model"""
        plt.close(self.fig)

    def handle_close(self, evt) -> None:  # pylint: disable=unused-argument
        """Cleanup at the canvas close event"""
        self.fig.canvas.stop_event_loop()
        self.on_close()

    def update_scatter_plot_limits(self, embedding: np.ndarray) -> None:
        """Resize the plot te respect the extent of the updated embedding"""
        minp = np.amin(embedding, axis=0)
        maxp = np.amax(embedding, axis=0)

        extent_x = (maxp[0] - minp[0]) if (maxp[0] - minp[0]) > 0 else 0.1
        extent_y = (maxp[1] - minp[1]) if (maxp[1] - minp[1]) > 0 else 0.1
        self.ax.set(
            xlim=(minp[0] - 0.1 * extent_x, maxp[0] + 0.1 * extent_x),
            ylim=(minp[1] - 0.1 * extent_y, maxp[1] + 0.1 * extent_y),
        )

    def force_refresh(self) -> None:
        """Force complete canvas redraw"""
        if not self.facecolors is None and not self.scatter is None:
            self.scatter.set_facecolors(self.facecolors)
        fig_size = self.fig.get_size_inches()
        self.fig.set_size_inches(fig_size)
        self.fig.canvas.draw()
        if self.active_selector:
            self.active_selector.update()

    def update_plot(self, embedding: np.ndarray) -> None:
        """Set new coordinated for the embedding and redraw everything"""
        self.embedding = embedding
        self.scatter.set_offsets(embedding)
        self.update_scatter_plot_limits(embedding)
        self.force_refresh()

    def set_face_colors(self, colors: np.ndarray) -> None:
        """Colors is a numpy array of #XXXXXX
        format string colors"""
        self.facecolors = list(colors)
        self.force_refresh()

    def on_over(self, event: MouseEvent) -> None:
        """Handle a transient selection"""
        self.fig.canvas.setFocus()
        if not self.in_selection:
            # Emit a transient selection
            cont, index = self.scatter.contains(event)
            perm_set = set(np.nonzero(self.selection_mask)[0])
            if cont:
                # self.on_selection(list(index['ind']), SelectionEvent.TRANSIENT)
                self.on_selection(list(set(index["ind"]) | perm_set), SelectionEvent.TRANSIENT)  # type: ignore
            else:
                # self.on_selection([], SelectionEvent.TRANSIENT)
                self.on_selection(list(perm_set), SelectionEvent.TRANSIENT)  # type: ignore

    def refresh_selection(self) -> None:
        """Adjust the edge colors to reflect the selection
        and trigger the callbask"""
        xys = self.scatter.get_offsets()
        # expand the single color case to give colors for all points
        # Set default edge colors same as face
        ec = self.scatter.get_facecolors()
        if ec.shape[0] == 1:
            ec = np.tile(ec, (xys.shape[0], 1))
        lw = np.full((ec.shape[0]), 1)
        # Set selected edge colors to dark grey and 2 thickness
        ec[self.selection_mask] = (0.05, 0.05, 0.05, 1)
        lw[self.selection_mask] = 2
        self.scatter.set_edgecolors(ec)
        self.scatter.set_linewidths(lw)
        self.fig.canvas.draw_idle()
        # Emit a permanent selection
        # return the current selection indexes
        self.on_selection(list(np.nonzero(self.selection_mask)[0]), SelectionEvent.PERMANENT)  # type: ignore

    def on_keypress(self, event: KeyEvent) -> None:
        """Handle the keyboard shortcuts"""
        if event.key in ["q", "Q", "escape"]:
            self.quit()
        update = False
        if event.key in ["i", "I"]:
            self.selection_mask = ~self.selection_mask
            update = True
        if event.key in ["a", "A"]:
            self.selection_mask.fill(True)
            update = True
        if event.key in ["d", "D"]:
            self.selection_mask.fill(False)
            update = True
        if update:
            self.refresh_selection()
            return

        self.draw_state = DrawingCursors.get_drawstate(event.key)
        self.setCursor(DrawingCursors.cursors[self.draw_state])
        self.set_selector(self.draw_state[1])

    def in_zoom_or_pan(self) -> bool:
        """Return true if the matplotlib zoom/pan function is active"""
        return bool(self.fig.canvas.toolbar.mode)

    def set_selector(self, enable=None) -> None:
        """Set the currently visible path selection widget"""
        self.active_selector = None
        for key, selector in self.selectors.items():
            # Need to also set the visibility for the polygon selector
            if key == enable:
                selector.set_active(True)
                selector.set_visible(True)
                self.active_selector = selector
            else:
                selector.set_active(False)
                selector.set_visible(False)

    def on_start_select(self, event: KeyEvent) -> None:
        """Check that the user has started a selection and record that"""
        print(f"Event key {event.key}")

        if self.disable_select:
            return
        if not event.inaxes == self.scatter.axes:
            return

        if self.draw_state == (DrawingMode.NoDraw, DrawingShape.NoShape):
            return
        self.in_selection = True

    def on_end_rectangle_select(self, pressed: MouseEvent, released: MouseEvent):
        """Use the rectangle path to make a
        selection based on the selecton state"""
        x1, y1 = pressed.xdata, pressed.ydata
        x2, y2 = released.xdata, released.ydata
        path = Path(np.array(([x1, y1], [x2, y1], [x2, y2], [x1, y2], [x1, y1])))
        self.select_path(path)

    def on_end_ellipse_select(self, pressed: MouseEvent, released: MouseEvent):
        """Use the ellipse path to make a
        selection based on the selecton state"""
        path = calculate_ellipse_path(pressed.xdata, pressed.ydata, released.xdata, released.ydata)
        self.select_path(path)

    def on_end_lasso_select(self, verts: List[float]):
        """Use the lasso or polygon path to make a
        selection based on the selecton state"""
        path = Path(verts)
        self.select_path(path)

    def select_path(self, path: Path):
        """make a selection from a matplotlib.path.Path"""
        self.in_selection = False
        xys = self.scatter.get_offsets()
        # length N bool array
        selection_mask = path.contains_points(xys)
        # print(f"selection shape {selection_mask.shape}")
        # print(f"current selection shape {self.selection_mask.shape}")
        # print(f"shape xys {xys.shape}")
        if self.draw_state[0] == DrawingMode.New:
            self.selection_mask = selection_mask
        if self.draw_state[0] == DrawingMode.Add:
            self.selection_mask = self.selection_mask | selection_mask
        if self.draw_state[0] == DrawingMode.Sub:
            self.selection_mask = self.selection_mask & ~selection_mask
        self.refresh_selection()

    def set_selection(self, indexes: np.ndarray):
        """Set a non-interactive selection.
        This could be a saved selection or one driven
        by meta data"""
        self.selection_mask.fill(False)
        self.selection_mask[indexes] = True
        self.refresh_selection()

    def get_figure_as_buffer(self):
        """Return the scatter plot as an image in a buffer"""
        self.force_refresh()
        buf = io.BytesIO()
        extent = self.scatter.get_tightbbox(self.fig.canvas.get_renderer()).transformed(
            self.fig.dpi_scale_trans.inverted()
        )

        self.fig.savefig(buf, bbox_inches=extent)
        self.force_refresh()
        return buf


class EmbeddingViewer(QtWidgets.QWidget):
    """Display an embedding gui for interaction and selection.
    In addition show the number of landmarks selected and give the
    user the chance to start a new analysis"""

    def __init__(self, parent=None):
        super(QtWidgets.QWidget, self).__init__(parent)
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.plot_widget = EmbeddingGui()
        self.main_layout.addWidget(self.plot_widget)
        self.control_layout = QtWidgets.QHBoxLayout(self)
        self.landmarks_label = QtWidgets.QLabel("Landmarks selected: 0")
        self.control_layout.addWidget(self.landmarks_label)
        self.new_analysis_button = QtWidgets.QPushButton("New Analysis")
        self.new_analysis_button.clicked.connect(self.on_new_analysis)
        self.control_layout.addWidget(self.new_analysis_button)
        self.main_layout.addLayout(self.control_layout)
        self.main_layout.setStretch(0, 1)
        self.setLayout(self.main_layout)
        self.selection_list = []
        self.on_selection_callback = None

    def init_plot(
        self,
        embedding,
        weights,
        on_selection,
        on_close,
        disable_select=False,
        top_level=False,
        labels=None,
        color_norm=None,
    ):
        """Initialize the scatter plot with the embedding provided

        Args:
            embedding ([type]): [description]
            weights ([type]): [description]
            on_selection ([type]): [description]
            on_close ([type]): [description]
            disable_select (bool, optional): [description]. Defaults to False.
            top_level (bool, optional): [description]. Defaults to False.
            labels ([type], optional): [description]. Defaults to None.
            color_norm ([type], optional): [description]. Defaults to None.
        """
        self.plot_widget.init_plot(
            embedding,
            weights,
            self.on_selection,
            on_close,
            disable_select,
            top_level,
            labels,
            color_norm,
        )
        self.on_selection_callback = on_selection

    def set_face_colors(self, color_array: np.ndarray) -> None:
        """Set the point glyph colors

        Args:
            color_array (np.ndarray): a numpy array of #XXXXXX colors
        """
        self.plot_widget.set_face_colors(color_array)

    def set_selection(self, index_array: np.ndarray) -> None:
        """Set a selection from an outside source

        Args:
            index_array (nd.array): The index_array is a numpy array of indexes
        """
        self.plot_widget.set_selection(index_array)

    @QtCore.pyqtSlot()
    def on_selection(self, indexes: np.ndarray, selection_event: SelectionEvent):
        """Handle a user selection operation in the plot
        Save the indexes and feed them back to the controller

        Args:
            indexes (np.ndarray): selection indexes
            selection_event (SelectionEvent.Enum): A permanent or transient (mouse over) selection
        """
        # print(f"indexes: {indexes.shape} selection size: {len(list(indexes))} perm: {permanent}")
        if selection_event is SelectionEvent.PERMANENT:
            self.selection_list = indexes
            self.landmarks_label.setText(f"Landmarks selected: {len(self.selection_list)}")
            self.on_selection_callback(self.selection_list, False)
        else:
            # mouse over - dont change the selection list
            if len(indexes) == 0:
                # restore the previous selection
                if len(self.selection_list) > 0:
                    self.on_selection_callback(self.selection_list, False)
            else:
                self.on_selection_callback(indexes, False)

    @QtCore.pyqtSlot()
    def on_new_analysis(self):
        """Start a new analysis bases on the selected indexes in this embedding."""
        if len(self.selection_list) > 0:
            self.on_selection_callback(self.selection_list, True)
        else:
            QtWidgets.QMessageBox.warning(
                self, "Warning", "Select some landscape points first to create a new analysis."
            )

    def set_dynamic_indexes(self, indexes):
        """A hook that could be employed to handle operations dependent on
        transient selections. Currently unused."""
        pass  # pylint: disable=unnecessary-pass

    def get_canvas_timer(self, interval: int):
        """Return a timer that can be used with the plot canvas

        interval is in milliseconds"""
        return self.plot_widget.get_canvas_timer(interval)

    def update_plot(self, embedding: np.ndarray):
        """Used in the embedding iteration phase when the xys are
        being calculated"""
        self.plot_widget.update_plot(embedding)

    def force_refresh(self):
        """Redraw the plot widget"""
        self.plot_widget.force_refresh()

    def get_figure_as_buffer(self):
        """Return the scatter plot as an image in a buffer"""
        return self.plot_widget.get_figure_as_buffer()

    def set_static_mask(self, mask):
        """Accept 1D num py array of 0 or 1.0 mask values"""
        # self.image_widget.set_selection_alpha(mask)

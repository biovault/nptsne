# -*- coding: utf-8 -*-
"""Control of Analysis Embedding.

This module implements a dialog and controller.
The dialog displays and embedding viewer and an image vewer.
The controller ensures that image viewer reflects
the selection state of the embedding selection.
The behavior of the image viewers is different for the 3 supported
demo types.

Classes:
    AnalysisController

"""
import time
import numpy as np
import nptsne
from matplotlib import colors
from matplotlib.backend_bases import TimerBase
from PyQt5 import QtWidgets  # pylint: disable=no-name-in-module
from EmbeddingGui import EmbeddingViewer
from CompositeImageViewer import CompositeImageViewer
from HyperspectralImageViewer import HyperspectralImageViewer
from MetaDataViewer import MetaDataViewer
from typing import List, Callable, Tuple, Union, TypeVar
from ConfigClasses import DemoType
from io import BytesIO
from typing import Union


class AnalysisController(QtWidgets.QDialog):
    """The containing dialog and controller for the embedding
    and the image viewer that together make up an analysis
    (i.e. a user selection at an hSNE scale). It also
    iterates over the embedding once the analysis is created
    and this is dynamically displayed in the embedding gui."""

    ListIds = TypeVar

    def __init__(
        self,
        demo_type: DemoType,
        make_new_analysis: Callable[[nptsne.hsne_analysis.Analysis, List[int]], None],
        remove_analysis: Callable[[int], List[int]],
        analysis_stopped: Callable[[nptsne.hsne_analysis.Analysis, BytesIO], None],
    ) -> None:
        super(QtWidgets.QDialog, self).__init__()
        self.embedding_viewer = EmbeddingViewer(self)
        self.data_gui: QtWidgets.QWidget
        self.demo_type = demo_type
        if demo_type == DemoType.LABELLED_DEMO:
            self.data_gui = CompositeImageViewer()
        elif demo_type == DemoType.HYPERSPECTRAL_DEMO:
            self.data_gui = HyperspectralImageViewer()
        elif demo_type == DemoType.POINT_DEMO:
            self.data_gui = MetaDataViewer()

        # Callbacks to the ModelController
        self.make_new_analysis = make_new_analysis
        self.remove_analysis = remove_analysis
        self.analysis_stopped = analysis_stopped
        self.meta_path: Union[str, None] = None

        self.__init_ui()

        # HSNE Analysis and data
        self.analysis: nptsne.hsne_analysis.Analysis = None  # hsne analysis
        self.data: np.ndarray  # the original data
        self.image_dimensions: Tuple[
            int, int
        ]  # the dimensions if the data rows represent an image
        self.iterations: int  # number of embedding iterations to perform for the layout

        # Embedding iteration control
        self.iters_per_frame = 1  # frames contain multiple iterations (for rendering speed)
        self.num_frames = 0  # number of render frames
        self._stop_iter = False  # stop iterating flage
        self._iter_count = 0  # current iteration
        self.timer_count = 0  # total number or iterations
        self.timer: TimerBase = None  # iteration timer

    def __init_ui(self) -> None:
        # Define the layout
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.widget_layout = QtWidgets.QHBoxLayout(self)
        self.widget_layout.addWidget(self.embedding_viewer, 1)
        data_gui_stretch = 0
        if self.demo_type == DemoType.HYPERSPECTRAL_DEMO:
            data_gui_stretch = 1
        if self.data_gui:
            self.widget_layout.addWidget(self.data_gui, data_gui_stretch)
        self.status = QtWidgets.QStatusBar()

        self.main_layout.addLayout(self.widget_layout)
        self.main_layout.addWidget(self.status)

        self.setLayout(self.main_layout)
        self.show()

    def set_metapath(self, meta_path: str):
        """The path to the optional meta data csv file"""
        self.meta_path = meta_path

    def start_embedding(
        self,
        data: np.ndarray,
        analysis: nptsne.hsne_analysis.Analysis,
        iterations: int,
        image_dimensions: Tuple[int, int],
        top_level: bool = False,
        labels: Union[np.ndarray, None] = None,
        color_norm: Union[colors.Normalize, None] = None,
    ) -> None:
        """Start the embedding  iteration loop with the
        supplied data and hsne analysis"""
        self.setWindowTitle(str(analysis))
        self.analysis = analysis
        self.data = data
        self.image_dimensions = image_dimensions
        self.iterations = iterations

        # Animation support for the embedding
        # if matplot lib rendering is slow do a number of iterations per frame
        # Total iterations = num_frames X iters_per_frame
        self.iters_per_frame = 5
        self.num_frames = int(self.iterations / self.iters_per_frame)
        self._stop_iter = False
        self._iter_count = 0
        self.timer_count = 0
        if self.demo_type in [DemoType.LABELLED_DEMO, DemoType.HYPERSPECTRAL_DEMO]:
            self.data_gui.init_plot(data, image_dimensions)
        elif self.demo_type == DemoType.POINT_DEMO:
            self.data_gui.init_metadata(self.meta_path, self.on_meta_colors, self.on_meta_select)

        sub_labels = None
        if labels is not None:
            sub_labels = labels[self.analysis.landmark_orig_indexes]

        disable_select = self.analysis.scale_id == 0
        self.embedding_viewer.init_plot(
            analysis.embedding,
            analysis.landmark_weights,
            self.on_selection,
            self.do_close,
            disable_select,
            top_level,
            sub_labels,
            color_norm,
        )

        # Fire up the embedding - drive the embedding and animation using a
        # timer
        self.timer = self.embedding_viewer.get_canvas_timer(50)
        self.timer.add_callback(self.iterate_tsne)
        self.timer.start()

    def iterate_tsne(self) -> None:
        """Develop the embedding by performing the tsne iterations
        and displaying the intermediate plots"""
        send_stop_event = False
        if self.analysis is None:
            return
        if not self._stop_iter:
            self.timer_count = self.timer_count + 1
            for j in range(self.iters_per_frame):
                self.analysis.do_iteration()
                self._iter_count = self.timer_count * self.iters_per_frame + j
                self.status.showMessage(f"Iteration: {self._iter_count}")

            if self.timer_count == self.num_frames - 1:
                self._stop_iter = True
                send_stop_event = True
                self.timer_count = 0
                self.status.showMessage("Iteration: Completed")

            # Update point positions
            self.embedding_viewer.update_plot(self.analysis.embedding)
        else:
            if self.timer_count % 10 == 0:
                self.embedding_viewer.force_refresh()

        if send_stop_event:
            self.embedding_viewer.force_refresh()
            time.sleep(0.1)
            self.analysis_stopped(self.analysis, self.embedding_viewer.get_figure_as_buffer())

    def data_index_from_selection(self, sel_indexes: List[int]) -> List[int]:
        """Selection indexes in this analysis are converted to original
        data point indexes"""
        data_indexes = []
        # Translate the landmark indexes to the original data indexes
        for i in sel_indexes:
            data_indexes.append(self.analysis.landmark_orig_indexes[i])
        return data_indexes

    def landmark_index_from_selection(self, sel_indexes: List[int]) -> List[int]:
        """Selection indexes in this analysis are converted to landmark
        indexes in this scale"""
        landmark_indexes = []
        # Translate the selection indexes to the scale indexes
        for i in sel_indexes:
            landmark_indexes.append(self.analysis.landmark_indexes[i])
        return landmark_indexes

    # Triggered by a selection in the embedding gui
    def on_selection(self, analysis_selection: List[int], make_new_analysis: bool) -> None:
        """analysis_selection is a list of indexes at this analysis scale
        If make_new_analysis is true start a new analysis controller"""
        landmark_indexes = self.landmark_index_from_selection(analysis_selection)
        if self.demo_type == DemoType.HYPERSPECTRAL_DEMO:
            # Pass area influenced to the hyperspectral viewer
            self.data_gui.set_static_mask(self.analysis.get_area_of_influence(landmark_indexes))

        if make_new_analysis:
            self.make_new_analysis(self.analysis, analysis_selection)
        else:
            if self.demo_type == DemoType.LABELLED_DEMO:
                # Pass data indexes to labelled viewer
                self.data_gui.set_image_indexes(self.data_index_from_selection(analysis_selection))

    #  Callbacks to be used by meta data manipulation GUIs
    def on_meta_ids(self, ids):
        """Point ids from the meta data (could extend to more metadata)"""
        pass  # pylint: disable=unnecessary-pass

    def on_meta_colors(self, color_array: np.ndarray) -> None:
        """Colors settings from a metadata viewer.
        The color_array is a numpy array of #XXXXXX colors for all data points. This
        needs to be filtered for the landmarks in this analysis"""

        # print(self.analysis.landmark_orig_indexes)
        analysis_colors = color_array[self.analysis.landmark_orig_indexes]
        # print(analysis_colors)
        self.embedding_viewer.set_face_colors(analysis_colors)

    def on_meta_select(self, data_index_array: List[int]) -> None:
        """Selection index from a metadata viewer.
        The index_array is a numpy array of indexes for all data points. This
        needs to be filtered for the landmarks in this analysis"""

        select = np.isin(self.analysis.landmark_orig_indexes, data_index_array)
        selected_indexes = np.where(select)
        # print(f'selected indexes {selected_indexes}')
        self.embedding_viewer.set_selection(selected_indexes)  # type: ignore

    def win_raise(self) -> None:
        """Raise this dialog to the top of the z-order"""
        self.raise_()
        self.activateWindow()

    def do_close(self) -> None:
        """Callbask to close the dialog"""
        self.cleanup(True)
        self.close()

    def cleanup(self, remove_analysis: bool = True) -> None:
        """Cleanup while closing"""
        if self.analysis is None:
            return
        if remove_analysis:
            print("Deleting analysis on close")
            self.remove_analysis(self.analysis.id)
        del self.analysis
        self.analysis = None

    # Override closeEvent for the widget
    def closeEvent(self, event) -> None:  # pylint: disable=invalid-name
        """Make sure that closing the dialog cleans up the analysis"""
        self.cleanup(True)
        event.accept()

    def kill(self) -> None:
        """Someone else has deleted the analysis close
        this dialog"""
        if self.analysis is not None:
            del self.analysis
        self.analysis = None
        self.do_close()

    @property
    def iter_stopped(self) -> bool:
        """Has the iteration stopped"""
        return self._stop_iter

    @property
    def iter_count(self) -> int:
        """The current iteration count"""
        return self._iter_count

    @property
    def figure_id(self) -> str:
        """The string id associated with this analysis"""
        return str(self.analysis)

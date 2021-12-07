#!/usr/bin/env python3
"""Provides creation and navigation of an hSNE manifold model"""

from io import BytesIO
from pathlib import Path
import queue
import sys

from matplotlib import colors

# The nptsne package and the hsne_analysis navigation support
import nptsne
from nptsne import hsne_analysis

# Standard support packages
import numpy as np
from PyQt5.QtWidgets import QApplication

# The demo GUI
from AnalysisController import AnalysisController
from ModelGui import ModelGui, AnalysisEvent
from ConfigClasses import DemoType
from typing import List, Union, Dict


class ModelController:
    """Control the creation and navigation of an hSNE manifold model
    using appropriate visualization and interaction GUIs depending on the data.
    This controller assumes that selections are hierarchical and that each
    selection produces a new GUI for viewing and further selection."""

    def __init__(self, embedder_type: hsne_analysis.EmbedderType) -> None:
        self.embedder_type = embedder_type
        self.analysis_model: hsne_analysis.AnalysisModel = None
        self.data: np.ndarray = np.empty(
            (
                1,
                1,
            )
        )
        self.analysis_guis: Dict[int, AnalysisController] = {}
        self.labels = None
        self.model_gui: ModelGui
        self.color_norm = None
        self.analysis_event_queue: queue.Queue = queue.Queue()
        self.im_size = (0, 0)
        self.labelcolor_filename = ""

    def run(self) -> None:
        """Display the control gui comprising a tree of the scales/analyses
        along with load and settings controls"""
        self.app = QApplication(sys.argv)
        self.model_gui = ModelGui(
            self.analysis_event_queue, self.tree_click, self.tree_del, self.tree_load
        )
        sys.exit(self.model_gui.exec_())
        # self.model_gui.run()

    def queue_new_analysis(self, analysis: hsne_analysis.Analysis) -> None:
        """Utility function for queuing an ADDED analysis"""
        self.analysis_event_queue.put(
            {
                "event": AnalysisEvent.ADDED,
                "id": analysis.id,
                "name": str(analysis),
                "scale_id": analysis.scale_id,
                "parent_id": analysis.parent_id,
                "number_of_points": analysis.number_of_points,
            }
        )

    def remove_analysis(self, analysis_id: int) -> List[int]:
        """Handle 1.)AnalysisEvent.REMOVED
        Callback remove an analysis in the analysis model"""
        removed_ids = self.analysis_model.remove_analysis(analysis_id)
        print("Updated analysis hierarchy: ")
        print(self.analysis_model.analysis_container)
        # TODO close associated GUIs
        for rid in removed_ids:
            self.analysis_event_queue.put({"event": AnalysisEvent.REMOVED, "id": rid})
            gui = self.analysis_guis.get(rid, None)
            if gui is not None:
                gui.kill()
                del self.analysis_guis[rid]
        return removed_ids

    def add_analysis(self, analysis: hsne_analysis.Analysis, selected_indexes: List[int]) -> None:
        """Handle 2.) AnalysisEvent.ADDED
        Callback to start a sub analysis in the analysis model"""
        print("Drilling down to new analysis")
        new_analysis = self.analysis_model.add_new_analysis(analysis, selected_indexes)
        print("Updated analysis hierarchy: ")
        print(self.analysis_model.analysis_container)
        print("Starting analysis GUI")

        analysis_gui = AnalysisController(
            self.model_gui.demo_type,
            self.add_analysis,
            self.remove_analysis,
            self.analysis_stopped,
        )

        if self.model_gui.demo_type is DemoType.POINT_DEMO:
            analysis_gui.set_metapath(self.labelcolor_filename)

        analysis_gui.start_embedding(
            self.data,
            new_analysis,
            self.model_gui.iterations,
            self.im_size,
            False,
            self.labels,
            self.color_norm,
        )
        self.analysis_guis[new_analysis.id] = analysis_gui
        self.queue_new_analysis(new_analysis)

    def analysis_stopped(self, analysis: hsne_analysis.Analysis, image_buf: BytesIO) -> None:
        """3.) AnalysisEvent.FINISHED
        Callback tohandle a completed analysis embedding"""
        self.analysis_event_queue.put(
            {
                "event": AnalysisEvent.FINISHED,
                "id": analysis.id,
                "name": str(analysis),
                "image_buf": image_buf,
            }
        )

    # Callbacks for the tree control
    # 1.) Clicking an item raises the window
    def tree_click(self, analysis_id: int):
        """Handle 1.) Clicking an item raises the window"""
        analysis_gui = self.analysis_guis[analysis_id]
        analysis_gui.win_raise()

    # 2.) Tree remove a numbe of analyses
    def tree_del(self, analysis_ids: List[int]):
        """Handle 2.) Tree remove - returns a list of ananlysis ids to deleter"""
        for rid in analysis_ids:
            if rid in self.analysis_guis:
                self.remove_analysis(rid)

    # 3.) Load an numpy file - offer the user the chance to preload an
    # hsnefile if one is avaliable
    def tree_load(
        self, filename: str, label_filename: str, labelcolor_filename: str, hsne_name: str
    ):
        """Handle 3.) Load an numpy file"""
        data_file_path = Path(filename)
        hsne_file_path = None
        if hsne_name:
            hsne_file_path = Path(hsne_name)
        test_file_path = data_file_path.with_suffix(".hsne")
        self.labelcolor_filename = labelcolor_filename

        data = np.load(data_file_path)
        self.start_hsne(data, data_file_path, hsne_file_path, label_filename)

    def __set_labels_and_color_norm(self, label_file):
        if not label_file or label_file == "":
            return (None, None)

        self.labels = np.load(label_file)
        bins = np.bincount(self.labels)
        num_labels = bins.shape[0]
        print(
            f"Making colormap for numlabels: {num_labels}\
            min: {self.labels.min()} max: {self.labels.max()}"
        )
        self.color_norm = colors.Normalize(vmin=self.labels.min(), vmax=self.labels.max())
        print(
            f"Color norm: {self.color_norm} "
            f"norm 0: {self.color_norm(0)} "
            f"norm 9: {self.color_norm(9)}"
        )

    # def get_label_colors_pair(self, labelcolor_file):
    #     """Return a dict with:
    #     {
    #         'label1_name': (label_list, color_list),
    #         'label2_name': (label_list, color_list),
    #         etc.
    #     }
    #     """
    #     pass

    def start_hsne(self, data, data_file: Path, hsne_file: Union[Path, None], label_file: str):
        """Initiate the embedding iteration in the analysis GUI"""
        print("Created hSNE")
        hsne = nptsne.HSne(True)

        number_of_scales = self.model_gui.scales
        print(f"Number of scales: {number_of_scales}")
        if hsne_file is None:
            print("hSNE from scratch")
            hsne.create_hsne(data, number_of_scales)
            hsne_file = data_file.with_suffix(".hsne")
            hsne.save(str(hsne_file))
        else:
            print("existing hSNE")
            hsne.load_hsne(data, str(hsne_file))

        print("start analysis model")
        self.data = data
        self.analysis_model = hsne_analysis.AnalysisModel(hsne, self.embedder_type)

        top_analysis = self.analysis_model.top_analysis

        # all_analyses_per_scale = {top_analysis.scale_id: {top_analysis.id: top_analysis}}

        self.__set_labels_and_color_norm(label_file)

        # The AnalysisGui is non-blocking
        # start with an analysis GUI containing all top scale landmarks
        is_top_level = True
        self.im_size = (0, 0)
        if self.model_gui.demo_type in [DemoType.LABELLED_DEMO, DemoType.HYPERSPECTRAL_DEMO]:
            self.im_size = (self.model_gui.im_size_x, self.model_gui.im_size_y)
        top_analysis_gui = AnalysisController(
            self.model_gui.demo_type,
            self.add_analysis,
            self.remove_analysis,
            self.analysis_stopped,
        )

        if self.model_gui.demo_type is DemoType.POINT_DEMO:
            top_analysis_gui.set_metapath(self.labelcolor_filename)

        top_analysis_gui.start_embedding(
            self.data,
            top_analysis,
            self.model_gui.iterations,
            self.im_size,
            False,
            self.labels,
            self.color_norm,
        )
        print(f"Top analysis has {top_analysis.number_of_points} points")
        self.analysis_guis[top_analysis.id] = top_analysis_gui
        self.queue_new_analysis(top_analysis)
        # Queue is used to pass changes in the analyses to the ModelGui
        # The ModelGui is blocking
        self.model_gui.set_analysis_model(self.analysis_model)

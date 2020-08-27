# -*- coding: utf-8 -*-
"""Model GUI classes.

This mGUI allows the user to choose the analysis type load data
and navigate and manipulate the resulting analysis model as it is formed.

Classes:
    AnalysisEvent
    DemoType
    ModelGui

"""
import sys
import os
import queue
from pathlib import Path
import math
from enum import Enum
import nptsne
import numpy as np
import PIL
from PIL import ImageQt, Image
from PyQt5.QtWidgets import (
    QApplication,
    QTreeView,
    QWidget,
    QGridLayout,
    QDialog,
    QGroupBox,
    QFormLayout,
    QPushButton,
    QLabel,
    QSpinBox,
    QFileDialog,
    QAbstractItemView,
    QComboBox,
    QHBoxLayout,
    QVBoxLayout,
    QLineEdit,
    QHeaderView)
from PyQt5.QtCore import Qt, QTimer, QSize, pyqtSlot
from PyQt5.QtGui import (QIcon, QStandardItemModel,
                         QStandardItem, QPixmap, QIntValidator)
from DemoConfig import CONFIGS


class AnalysisEvent(Enum):
    """The events resulting from the creation and deletion of analyses by the user"""
    ADDED = 1
    FINISHED = 2
    REMOVED = 3


class DemoType(Enum):
    """The style of data being processed. Supported are
        Labelled: MNIST style data - with or without labels
        Point: e.g. cell and gene data wit meta data for labels/colors
        Hyperspectral images: Array of equally size images where each pixel has several
            dimensions (wavelengths)"""
    LABELLED_DEMO, POINT_DEMO, HYPERSPECTRAL_DEMO = range(3)


class ModelGui(QDialog):
    """The gui to start and manipulate the analysis model"""
    ANALYSIS, ID, NUMPOINTS = range(3)

    NO_PARENT_ID = 0xFFFFFFFF

    def __init__(self, analysis_event_queue, select, delete, load):
        super(ModelGui, self).__init__()
        self.analysis_event_queue = analysis_event_queue
        self.select_callback = select
        self.delete_callback = delete
        self.load_callback = load

        self.name = None
        self.label_name = None
        self.meta_name = None
        self.hsne_name = None

        self.title = 'Analysis hierarchy viewer'
        self.left = 10
        self.top = 10
        self.width = 1000
        self.height = 400
        self.init_ui()
        self.id_item = {}
        self.root_id = None

    def init_ui(self):
        """All the ui layout in one place. Note: Part of the ui
        is switchable depending on the selected demo type, see the ui_matrix"""
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.model = self.create_analysis_model(self)
        self.analysis_model = None
        self.top_scale = None
        self.thumb_size = (40, 40)

        # The analysis tree
        self.tree = QTreeView()
        self.tree.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tree.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tree.setIconSize(QSize(*self.thumb_size))
        self.tree.setModel(self.model)

        self.tree.setAnimated(False)
        self.tree.setIndentation(20)
        self.tree.setSortingEnabled(True)

        self.tree.resize(640, 480)

        # Control layout
        controlLayout = QVBoxLayout()

        self.preconfigured_group = QGroupBox("Preconfigured")
        preconfigured_layout = QFormLayout(self)
        self.preconfigured_combo = QComboBox(self)
        self.preconfigured_combo.addItem('None', userData=None)
        for config in CONFIGS:
            self.preconfigured_combo.addItem(config.descriptor, userData=config)
        self.preconfigured_combo.currentIndexChanged[int].connect(
            self.on_preconfigured)    
        preconfigured_layout.addRow(
            QLabel("Load preset demo:"),
            self.preconfigured_combo)
        self.preconfigured_group.setLayout(preconfigured_layout)
        controlLayout.addWidget(self.preconfigured_group)

        # Data type settings
        self.demo_type_group = QGroupBox("Data type")
        data_type_layout = QFormLayout(self)
        self.data_type_combo = QComboBox(self)
        self.data_type_combo.addItem(
            "Image is a data point",
            DemoType.LABELLED_DEMO)
        self.data_type_combo.addItem(
            "Point and metadata",
            DemoType.POINT_DEMO)
        self.data_type_combo.addItem(
            "Hyperspectral image",
            DemoType.HYPERSPECTRAL_DEMO)
        data_type_layout.addRow(
            QLabel("Visualization style:"),
            self.data_type_combo)
        self.data_type_combo.currentIndexChanged[int].connect(
            self.on_demo_style)

        data_button = QPushButton("Data")
        data_button.clicked.connect(self.on_load)
        self.data_label = QLabel("<choose data .npy>")
        data_type_layout.addRow(data_button, self.data_label)

        self.xy_label = QLabel("Image size")
        self.label_x = QLabel("X:")
        self.label_y = QLabel("Y:")
        self.image_x = QLineEdit()
        self.image_x.setValidator(QIntValidator(1, 10000))
        self.image_y = QLineEdit()
        self.image_y.setValidator(QIntValidator(1, 10000))

        self.xy_container = QWidget()
        self.xy_layout = QHBoxLayout()
        self.xy_layout.setContentsMargins(0, 0, 0, 0)
        self.xy_layout.addWidget(self.label_x)
        self.xy_layout.addWidget(self.image_x)
        self.xy_layout.addWidget(self.label_y)
        self.xy_layout.addWidget(self.image_y)
        self.xy_container.setLayout(self.xy_layout)
        data_type_layout.addRow(self.xy_label, self.xy_container)

        self.label_button = QPushButton("Labels")
        self.label_button.clicked.connect(self.on_load_labels)
        self.label_label = QLabel("<optionally choose labels .npy>")
        data_type_layout.addRow(self.label_button, self.label_label)

        self.meta_button = QPushButton("Label/Color metadata")
        self.meta_button.clicked.connect(self.on_load_labelscolors)
        self.meta_label = QLabel("<optionally choose label/color .csv>")
        data_type_layout.addRow(self.meta_button, self.meta_label)
        self.demo_type_group.setLayout(data_type_layout)
        controlLayout.addWidget(self.demo_type_group)

        # Hsne settings
        self.hsne_group = QGroupBox("hSNE settings")
        self.hsne_form_layout = QFormLayout(self)

        hsne_button = QPushButton("Preload")
        hsne_button.clicked.connect(self.on_load_hsne)
        self.hsne_label = QLabel("<optionally choose existing .hsne>")
        self.hsne_form_layout.addRow(hsne_button, self.hsne_label)

        self.scale_spin = QSpinBox(self)
        self.scale_spin.setRange(1, 10)
        self.scale_spin.setValue(4)
        self.hsne_form_layout.addRow(QLabel("Scales:"), self.scale_spin)

        self.hsne_group.setLayout(self.hsne_form_layout)
        controlLayout.addWidget(self.hsne_group)

        # Embedding settings
        self.embedding_group = QGroupBox("Embedding settings")
        embed_form_layout = QFormLayout(self)
        self.iter_spin = QSpinBox(self)
        self.iter_spin.setRange(350, 1000)
        self.iter_spin.setSingleStep(5)
        self.iter_spin.setValue(500)
        embed_form_layout.addRow(QLabel("Iterations:"), self.iter_spin)
        self.embedding_group.setLayout(embed_form_layout)

        controlLayout.addWidget(self.embedding_group)

        clear_start_layout = QHBoxLayout()
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.on_start)
        self.start_button.setDisabled(True)
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.on_clear)

        clear_start_layout.addWidget(self.start_button)
        clear_start_layout.addWidget(self.clear_button)

        controlLayout.addLayout(clear_start_layout)

        self.delete_button = QPushButton("Delete selected")
        self.delete_button.clicked.connect(self.on_delete)

        # Selection
        self.tree.clicked.connect(self.on_selected)

        # Layout
        main_layout = QGridLayout()
        # row, col, rowSpan, colSpan
        main_layout.addWidget(self.tree, 0, 0, 10, 5)
        main_layout.addLayout(controlLayout, 0, 5, 10, 3)

        main_layout.addWidget(self.delete_button, 11, 2, 1, 2)
        self.setLayout(main_layout)
        self.counter = 0
        self.event_timer = QTimer(self)
        self.event_timer.start(500)
        self.event_timer.timeout.connect(self.update_tree)

        # Dynamic UI matrix
        # According to DemoType True widgets are shown False widgets hidden
        self.ui_matrix = {
            DemoType.LABELLED_DEMO: {
                True: [
                    self.label_button,
                    self.label_label,
                    self.xy_container,
                    self.xy_label],
                False: [
                    self.meta_button,
                    self.meta_label]},
            DemoType.POINT_DEMO: {
                True: [
                    self.meta_button,
                    self.meta_label],
                False: [
                    self.label_button,
                    self.label_label,
                    self.xy_container,
                    self.xy_label]},
            DemoType.HYPERSPECTRAL_DEMO: {
                True: [
                    self.xy_container,
                    self.xy_label],
                False: [
                    self.label_button,
                    self.label_label,
                    self.meta_button,
                    self.meta_label]}}

        self.show()
        self.on_demo_style(0)

    def set_analysis_model(self, analysis_model):
        # TODO empty event queue
        self.analysis_model = analysis_model
        self.top_scale = self.analysis_model.top_scale_id

    @property
    def iterations(self):
        return self.iter_spin.value()

    @property
    def scales(self):
        return self.scale_spin.value()

    @property
    def demo_type(self):
        return self.data_type_combo.currentData()

    @property
    def im_size_x(self):
        return int(self.image_x.text())

    @property
    def im_size_y(self):
        return int(self.image_y.text())
        
    @pyqtSlot(int)
    def on_preconfigured(self, index):
        config = self.preconfigured_combo.itemData(index)
        self.on_clear()
        if config is None:
            return
        if type(config).__name__ == "LabelledImage":
            self.data_type_combo.setCurrentIndex(0)
            self.name = config.data.data_file
            self.data_label.setText(config.data.data_file)
            self.label_name = config.data.label_file
            self.label_label.setText(config.data.label_file)
            if config.hsne.hsne_file != "":
                self.hsne_name = config.hsne.hsne_file
                self.__set_scale_from_hsne_file()
                self.scale_spin.setDisabled(True)
            elif config.hsne.scales > 0:
                self.scale_spin.setValue(config.hsne.scales)        
            if config.image.dim_x > 0 and config.image.dim_y > 0:
                self.image_x.setText(str(config.image.dim_x))
                self.image_y.setText(str(config.image.dim_y))   
           
        elif type(config).__name__ == "PointMeta":
            self.data_type_combo.setCurrentIndex(1)
            self.name = config.data.data_file
            self.data_label.setText(config.data.data_file)
            self.meta_name = config.data.meta_file
            self.meta_label.setText(config.data.meta_file)
            if config.hsne.hsne_file != "":
                self.hsne_name = config.hsne.hsne_file
                self.__set_scale_from_hsne_file()
                self.scale_spin.setDisabled(True)
            elif config.hsne.scales > 0:
                self.scale_spin.setValue(config.hsne.scales)
                
        elif type(config).__name__ == "HyperspectralImage":
            self.data_type_combo.setCurrentIndex(2)
            self.name = config.data.data_file
            self.data_label.setText(config.data.data_file)
            if config.hsne.hsne_file != "":
                self.hsne_name = config.hsne.hsne_file
                self.__set_scale_from_hsne_file()
                self.scale_spin.setDisabled(True)
            elif config.hsne.scales > 0:
                self.scale_spin.setValue(config.hsne.scales)        
            if config.image.dim_x > 0 and config.image.dim_y > 0:
                self.image_x.setText(str(config.image.dim_x))
                self.image_y.setText(str(config.image.dim_y))
                
        self.start_button.setEnabled(True)    

    @pyqtSlot(int)
    def on_demo_style(self, index):
        # set the visibility of the widgets according to the
        # type of demo being given
        for state in [False, True]:
            for widget in self.ui_matrix[self.demo_type][state]:
                widget.setVisible(state)

    @pyqtSlot()
    def on_load(self):
        workdir = os.path.dirname(os.path.abspath(__file__))
        result = QFileDialog.getOpenFileName(
            self,
            'Open a numpy file where each row is a data point and columns are dimensions',
            workdir,
            "Numpy files (*.npy)")
        if result[0]:
            self.hsne_label.setText("")
            self.hsne_name = None
            self.scale_spin.setEnabled(True)
            self.name = result[0]
            # print(f"Selected: {self.name}")
            self.start_button.setEnabled(True)
            if (self.demo_type == DemoType.LABELLED_DEMO or
                    self.demo_type == DemoType.HYPERSPECTRAL_DEMO):
                # partial data load (in memory) to read the shape
                the_data = np.load(self.name, mmap_mode='r')
                image_flat_size = the_data.shape[1]
                if self.demo_type == DemoType.HYPERSPECTRAL_DEMO:
                    image_flat_size = the_data.shape[0]
                xsize = int(math.sqrt(image_flat_size))
                ysize = int(image_flat_size / xsize)
                self.image_x.setText(str(xsize))
                self.image_y.setText(str(ysize))
            self.data_label.setText(str(Path(self.name).name))
    
    def __set_scale_from_hsne_file(self):
        scale_value = nptsne.HSne.read_num_scales(self.hsne_name)
        self.hsne_label.setText(str(Path(self.hsne_name).name))
        self.scale_spin.setValue(scale_value)
        self.scale_spin.setDisabled(True)        

    @pyqtSlot()
    def on_load_hsne(self):
        workdir = os.path.dirname(os.path.abspath(__file__))
        result = QFileDialog.getOpenFileName(
            self,
            'Open a pre-calculated hSNE analysis file .hsne',
            workdir,
            "hSNE files (*.hsne)")
        if result[0]:
            self.hsne_name = result[0]
            # print(f"Selected: {self.name}")
            self.__set_scale_from_hsne_file()

    @pyqtSlot()
    def on_load_labels(self):
        workdir = os.path.dirname(os.path.abspath(__file__))
        result = QFileDialog.getOpenFileName(
            self,
            'Open a numpy file where each row is an integer label',
            workdir,
            "Numpy files (*.npy)")
        if result[0]:
            self.label_name = result[0]
            self.label_label.setText(Path(self.label_name).name)

    @pyqtSlot()
    def on_load_labelscolors(self):
        workdir = os.path.dirname(os.path.abspath(__file__))
        result = QFileDialog.getOpenFileName(
            self,
            'Open a CSV file with header where the columns pairs of Label, #COLOR_',
            workdir,
            "CSV files (*.csv)")

        if result[0]:
            self.meta_name = result[0]
            self.meta_label.setText(Path(self.meta_name).name)

    @pyqtSlot()
    def on_start(self):
        self.load_callback(
            self.name,
            self.label_name,
            self.meta_name,
            self.hsne_name)

    @pyqtSlot()
    def on_selected(self):
        analysis_id = self._get_selected_id()
        if analysis_id:
            self.select_callback(int(analysis_id))

    @pyqtSlot()
    def on_delete(self):
        analysis_id = self._get_selected_id()
        if analysis_id:
            self.delete_callback([int(analysis_id)])

    @pyqtSlot()
    def on_clear(self):
        if not self.root_id is None:
            self.select_callback(int(self.root_id))
        self.clear()
        self.name = None
        self.data_label.setText("<choose data .npy>")
        self.label_name = None
        self.label_label.setText("<optionally choose labels .npy>")
        self.meta_name = None
        self.meta_label.setText("<optionally choose label/color .csv>")
        self.scale_spin.setValue(4)
        self.scale_spin.setEnabled(True)
        self.start_button.setDisabled(True)
        self.hsne_name = None
        self.hsne_label.setText("<optionally choose existing .hsne>")
        self.image_x.setText("")
        self.image_y.setText("")

    def _get_selected_id(self):
        index = self.tree.currentIndex()
        if index is None:
            return None
        return self.model.itemData(index.siblingAtColumn(self.ID))[0]

    def create_analysis_model(self, parent):
        model = QStandardItemModel(0, 3, parent)
        model.setHeaderData(self.ANALYSIS, Qt.Horizontal, "Analysis")
        model.setHeaderData(self.ID, Qt.Horizontal, "Id")
        model.setHeaderData(self.NUMPOINTS, Qt.Horizontal, "#Points")
        return model

    def add_test_analysis(self):
        parent_id = ModelGui.NO_PARENT_ID
        if self.counter > 0:
            parent_id = self.counter - 1
        self.add_analysis(
            self.counter,
            f"{self.counter} Blah blah blah",
            parent_id,
            150)
        self.counter = self.counter + 1

    def update_tree(self):
        # Update tree based on queued events
        while True:
            event = {}
            try:
                event = self.analysis_event_queue.get_nowait()
            except queue.Empty:
                break

            if event['event'] == AnalysisEvent.ADDED:
                self.add_analysis(
                    event['id'],
                    event['name'],
                    event['parent_id'],
                    event['number_of_points'])
                continue
            if event['event'] == AnalysisEvent.FINISHED:
                self.finish_analysis(
                    event['id'], event['name'], event['image_buf'])
                continue
            if event['event'] == AnalysisEvent.REMOVED:
                self.remove_analysis(event['id'])

    def add_analysis(self, analysis_id, name, parent_id, numpoints):
        im = ImageQt.ImageQt(Image.new('RGB', self.thumb_size, (100, 0, 200)))
        item = QStandardItem(QIcon(QPixmap.fromImage(im)), name)
        # Need to persist the thumbnails otherwise the ImageQT will get garbage
        # collected along with the memory
        item.__thumb = im
        if parent_id == ModelGui.NO_PARENT_ID:
            #print("Adding root")
            self.clear()
            self.model.insertRow(0, [item, QStandardItem(
                str(analysis_id)), QStandardItem(str(numpoints))])
            self.root_id = analysis_id
            self.id_item[analysis_id] = item
        else:
            #print("Adding child")
            parent = self.find_analysis_item(parent_id)
            if parent is not None:
                parent.appendRow([item, QStandardItem(
                    str(analysis_id)), QStandardItem(str(numpoints))])
                self.id_item[analysis_id] = item
                self.tree.expand(parent.index())

    def remove_analysis(self, analysis_id):
        if analysis_id == self.root_id:
            self.clear()
            return
        item = self.find_analysis_item(analysis_id)
        if item:
            if item.parent:
                try:
                    item.parent().removeRow(item.row())
                except RuntimeError:
                    # TODO fix bug that means this is being deleted twice
                    pass

            del self.id_item[analysis_id]

    def finish_analysis(self, analysis_id, name, image_buf):
        print("finished ", analysis_id)
        img = PIL.Image.open(image_buf)
        thumbnail = img.resize(self.thumb_size, PIL.Image.ANTIALIAS)
        # thumbnail.show()
        im = ImageQt.ImageQt(thumbnail)
        item = self.find_analysis_item(analysis_id)

        item.setIcon(QIcon(QPixmap.fromImage(im)))
        item.__thumb = im

    def find_analysis_item(self, analysis_id):
        """ Get the item using the numeric analysis_id """
        return self.id_item.get(analysis_id, None)

    def clear(self):
        print('Clear model content')
        if self.model is not None:
            # print('Remove rows')
            self.model.removeRows(0, self.model.rowCount())
        # print('Reset bookkeeping')
        self.id_item = {}
        self.root_id = None


# A main to allow inspection of layout
if __name__ == '__main__':
    APP = QApplication(sys.argv)
    DIALOG = ModelGui(queue.Queue(), None, None, None)
    #timer = QTimer(DIALOG)
    # timer.start(2000)
    # timer.timeout.connect(DIALOG.add_test_analysis)
    sys.exit(DIALOG.exec_())

# -*- coding: utf-8 -*-
"""View data as a composite (average) of multiple grayscale frames"""
import pandas as pd
import numpy as np
from PyQt5.QtWidgets import (
    QWidget,
    QFormLayout,
    QVBoxLayout,
    QComboBox,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QAbstractItemView,
    QHeaderView,
)
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QColor
from typing import Union, Callable, List


class MetaDataViewer(QWidget):
    """This is the QT Gui that can be used to manipulate
    the meta data in the Embedding Gui

    Assumes layout of the meta-data csv has an id followed
    by pairs of label + color columns

    id label0 color0 label1 color1 --- labelN colorN
    .  ...    ...    ...    ...    --- ...    ...
    .  ...    ...    ...    ...    --- ...    ...

    """

    def __init__(self):
        """View a composite image based
        on a subselection of the data
        """
        super(MetaDataViewer, self).__init__()
        self.class_combo = QComboBox(self)
        main_layout = QVBoxLayout()
        form_layout = QFormLayout()
        form_layout.addRow(QLabel("Class:"), self.class_combo)
        self.meta_table = QTableWidget(self)
        self.meta_table.itemSelectionChanged.connect(self.on_change_select)
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.meta_table, 6)
        self.setLayout(main_layout)
        self.headers = None
        self.class_combo.currentIndexChanged[int].connect(self.on_class)
        self.meta_path = None
        self.label_series = None
        self.color_series = None
        self.labels = None
        self.string_labels = None
        self.on_color_change = None
        self.on_select = None
        self.dframe = None

    def init_metadata(
        self,
        meta_path: Union[str, None],
        on_color_change: Callable[[np.ndarray], None],
        on_select=Callable[[List[int]], None],
    ):
        """Load the meta data and register the meta selection callbacks"""
        if meta_path is None:
            return
        self.on_color_change = on_color_change
        self.on_select = on_select
        self.meta_path = meta_path
        self.headers = pd.read_csv(meta_path, nrows=0)
        header_names = list(self.headers)
        self.meta_pairs = []
        if len(header_names) % 2 == 0:
            raise RuntimeError(
                """Expecting meta data to comprise an id
                    column followed by pairs of label/color columns"""
            )
        for i in range(1, len(header_names), 2):
            self.meta_pairs.append([header_names[i], header_names[i + 1]])
            self.class_combo.addItem(header_names[i], i)
        self.class_combo.setCurrentIndex(0)

    def __fill_table(self):
        """The table allows the user to select labels"""
        self.meta_table.clear()
        # select by row and allow building up multiple selections
        self.meta_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.meta_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.meta_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.meta_table.setShowGrid(True)
        self.meta_table.setRowCount(len(self.labels))
        self.meta_table.setColumnCount(2)
        self.meta_table.setHorizontalHeaderLabels(["Group", "Color"])
        self.meta_table.verticalHeader().hide()
        for i, label in enumerate(self.labels):
            # some label columns are not strings - whodathunkit!
            self.meta_table.setItem(i, 0, QTableWidgetItem(str(label)))
            color_item = QTableWidgetItem(" ")
            lab_col = self.unique_dframe[self.unique_dframe.iloc[:, 0] == label]
            color_item.setBackground(QColor(lab_col.iloc[0, 1]))
            self.meta_table.setItem(i, 1, color_item)

    @pyqtSlot(int)
    def on_class(self, index: int):
        """A new meta data class has been selected. Load
        and activate the pair of meta columns label + color"""
        if self.meta_path is None:
            return
        cols = self.meta_pairs[index]
        # load the columns corresponsing to the selected class
        dframe = pd.read_csv(self.meta_path, usecols=cols)
        self.label_series = dframe.iloc[:, 0]
        self.color_series = dframe.iloc[:, 1]
        self.unique_dframe = dframe.drop_duplicates()
        self.labels = list(self.label_series.unique())
        self.labels.sort()
        self.__fill_table()
        # Callback the currently loaded  colors
        self.on_color_change(self.color_series.to_numpy())

    @pyqtSlot()
    def on_change_select(self):
        """A meta data row has been selected in the table. Convert that
        to data indexes and callback to the Analysis Controller"""
        selection = self.meta_table.selectedIndexes()
        all_indexes = []
        for i in selection:
            group = self.labels[i.row()]
            group_indexes = list(self.label_series[self.label_series == group].index)
            all_indexes = all_indexes + group_indexes
        self.on_select(all_indexes)

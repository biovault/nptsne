"""A viewer for hyperspectral image data

    Includes controls for loading an blending a background image and
    choosing the current image index displayed. Hyperspectral and background
    data are displayed as gray scale
"""
import os
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.style as mplstyle
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QLabel,
    QSpinBox,
    QFormLayout,
    QPushButton,
    QFileDialog,
    QSlider,
)
from PyQt5.QtCore import pyqtSlot, Qt
from PIL import Image
from typing import Tuple


class HyperspectralImageCanvas(FigureCanvas):
    """This is the matplotlib based GUI for a single analysis
    It assumes the analysis is simple image data (this could be abstracted)"""

    def __init__(self, width=2, height=2):
        """View a composite image based
        on a subselection of the data
        """

        self.fig = Figure(figsize=(width, height))
        self.ix: plt.Axes = self.fig.add_subplot(111)
        self.ix.set_xticks([])
        self.ix.set_yticks([])
        self.blend: float = 0.5

        # the data and background image
        self.data: np.ndarray = None
        self.image_dimensions: Tuple[int, int] = None
        self.black_back: Image = None
        self.background: Image = None
        self.back_blend: Image = None
        self.data: np.ndarray = None
        self.alphas: np.ndarray = None
        self.index: int = None
        self.display_img: plt.Axes = None

        mplstyle.use("fast")
        super(HyperspectralImageCanvas, self).__init__(self.fig)
        self.fig.tight_layout(pad=0)
        plt.show(block=False)

    def init_plot(
        self, data: np.ndarray, image_dimensions: Tuple[int, int], index: int = 0
    ) -> None:
        """Initialize the image canvas with the hyperspectral data

        Args:
            data (np.ndarray): The hyperspectral data
            image_dimensions (array): Dimensions of the images given by each row of the data
            index (integer): Default image (row) index in the data
        """
        self.image_dimensions = image_dimensions
        # alpha will cause fade to black background
        self.black_back = Image.fromarray(np.full(image_dimensions, 0, dtype=np.uint8), "L")
        self.background = self.black_back
        self.back_blend = Image.blend(self.black_back, self.background, self.blend)
        self.data = np.reshape(data, (*image_dimensions, data.shape[1]))
        print(f"Reshaped: {self.data.shape}")
        self.alphas = np.full(image_dimensions, 255, dtype=np.uint8)
        self.index = index

        # start with a image 0
        self.display_img = self.ix.imshow(
            self.data[..., self.index], interpolation="bilinear", cmap="gray", vmin=0, vmax=255
        )

    def set_background(self, back_image):
        """Set a background image from a numpy array

        Args:
            back_image (numpy.ndarray): the image rendered as background
        """
        self.background = back_image
        self.back_blend = Image.blend(self.black_back, self.background, self.blend)
        self.set_image_index(self.index)

    def set_blend(self, value):
        """Set the blend factor

        Args:
            value (float): 0 to 1
        """
        self.blend = value
        self.back_blend = Image.blend(self.black_back, self.background, self.blend)
        self.set_image_index(self.index)

    def set_image_index(self, index):
        """Set the forground image index

        Args:
            index (integer): Must be in the range of the number of hyperspectral images in the data.
        """
        self.index = index
        image = Image.fromarray(self.data[..., index], "L")  # 8-bit black white
        # print(f"Image size: {image.size}")
        alfa_im = Image.fromarray(self.alphas, "L")
        # print(f"Alfa size: {alfa_im.size}")
        comp_image = Image.composite(image, self.back_blend, alfa_im)
        comp_array = np.array(comp_image)
        # print(f"comp array shape: {comp_array.shape}")
        self.display_img.set_clim(vmin=comp_array.min(), vmax=comp_array.max())
        self.display_img.set_array(np.reshape(comp_array, self.image_dimensions))
        self.force_refresh()

    def set_selection_alpha(self, mask):
        """Set a linear mask - will be reshapen to the image size

        Args:
            mask (np.ndarray): dtype np.uint8 maek - values 0 or 1
        """
        self.alphas = np.reshape(mask * 255, self.image_dimensions).astype(np.uint8)
        self.set_image_index(self.index)

    def force_refresh(self):
        """Redraw the image canvas"""
        fig_size = self.fig.get_size_inches()
        self.fig.set_size_inches(fig_size)
        self.fig.canvas.draw()


class HyperspectralImageViewer(QWidget):
    """
    The control widget for setting the visible
    layer, and the background image.
    """

    def __init__(self):
        super(HyperspectralImageViewer, self).__init__()
        self.main_layout = QVBoxLayout(self)
        self.image_widget = HyperspectralImageCanvas()
        self.main_layout.addWidget(self.image_widget)
        self.bkgrnd_name = None
        # self.control_layout = QHBoxLayout(self)
        self.control_layout = QFormLayout(self)
        # self.control_layout.addWidget(QLabel("Select image dimension: "))
        self.image_spin = QSpinBox(self)
        self.image_spin.setValue(0)
        self.image_spin.setRange(0, 0)
        self.image_spin.valueChanged[int].connect(self.on_image_changed)
        # self.control_layout.addWidget(self.image_spin)
        self.control_layout.addRow(QLabel("Select image dimension: "), self.image_spin)
        self.bkgrnd_button = QPushButton("Data")
        self.bkgrnd_button.clicked.connect(self.on_load_bkgrnd)
        self.bkgrnd_label = QLabel("<optionally choose background .png>")
        self.control_layout.addRow(self.bkgrnd_button, self.bkgrnd_label)
        self.blend_slider = QSlider(Qt.Horizontal, self)
        self.blend_slider.setValue(50)
        self.blend_slider.valueChanged.connect(self.change_blend)
        self.control_layout.addRow(QLabel("Blend: "), self.blend_slider)

        self.main_layout.addLayout(self.control_layout)
        self.main_layout.setStretch(0, 1)
        self.setLayout(self.main_layout)
        self.data = None

    def init_plot(self, data, image_dimensions):
        """Initialize the  plot image

        Args:
            data ([type]): [description]
            image_dimensions ([type]): [description]
        """
        num_images = data.shape[1]
        self.data = data
        print(f"num images {num_images}")
        self.image_spin.setRange(0, num_images - 1)
        self.image_widget.init_plot(data, image_dimensions, self.image_spin.value())

    @pyqtSlot(int)
    def on_image_changed(self, img_index):
        """The visible image index has changed

        Args:
            img_index (integer): The image index
        """
        self.image_widget.set_image_index(img_index)

    @pyqtSlot(int)
    def change_blend(self, value):
        """The blend (between background and foreground) has changed

        Args:
            value (float): Value in the range 0 to 1
        """
        self.image_widget.set_blend(value / 100)

    @pyqtSlot()
    def on_load_bkgrnd(self):
        """Load a background image"""
        workdir = os.path.dirname(os.path.abspath(__file__))
        result = QFileDialog.getOpenFileName(
            self,
            "A png background image the same size as the hyperspectral frame",
            workdir,
            "PNG files (*.png)",
        )
        if result[0]:
            self.bkgrnd_name = result[0]
            self.bkgrnd_label.setText(Path(self.bkgrnd_name).name)
            back_image = Image.open(self.bkgrnd_name)
            self.image_widget.set_background(back_image.convert("L"))

    def set_static_mask(self, mask):
        """Accept 1D num py array of 0 or 1.0 mask values"""
        self.image_widget.set_selection_alpha(mask)

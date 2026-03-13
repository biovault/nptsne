# -*- coding: utf-8 -*-
"""View data as a composite (average) of multiple grayscale frames"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimage
import matplotlib.style as mplstyle
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure
from typing import Tuple, List, Any


class CompositeImageViewer(FigureCanvas):
    """This is the matplotlib based GUI for a single analysis
    It assumes the analysis is simple image data (this could be abstracted)"""

    def __init__(self, width: int = 2, height: int = 2):
        """View a composite image based
        on a subselection of the data
        """

        self.fig = Figure(figsize=(width, height))
        self.ix: plt.Axes = self.fig.add_subplot(111)
        self.ix.set_xticks([])
        self.ix.set_yticks([])
        mplstyle.use("fast")
        super(CompositeImageViewer, self).__init__(self.fig)
        self.fig.tight_layout(pad=0)
        self.composite_digit: np.ndarray
        self.display_img: mpimage.AxesImage
        self.indexes: List[int]
        self.image_dimensions: Tuple[int, int]
        self.data: np.ndarray
        plt.show(block=False)

    def init_plot(self, data: np.ndarray, image_dimensions: Tuple[int, int]) -> None:
        """Start the imshow plot by showing dummy daya - a blank image"""
        self.image_dimensions = image_dimensions
        self.data = data

        # Display initial empty composite
        dummydata = np.zeros(image_dimensions, dtype=np.float32)
        self.composite_digit = np.zeros((image_dimensions[0] * image_dimensions[1],))
        self.display_img = self.ix.imshow(
            dummydata, interpolation="bilinear", cmap="gray", vmin=0, vmax=255
        )

    def set_image_indexes(self, indexes: List[int]) -> None:
        """Set the image indexes to be composited. These indexes are
        offsets in the data (image) dimension"""
        self.composite_digit = np.zeros((self.image_dimensions[0] * self.image_dimensions[1],))
        if len(indexes) > 0:
            for i in indexes:
                self.composite_digit = np.add(self.composite_digit, self.data[i, :])
            self.composite_digit = self.composite_digit / len(indexes)
        digit = np.reshape(self.composite_digit, self.image_dimensions)
        self.display_img.set_array(digit)
        self.display_img.set_clim(vmin=digit.min().min(), vmax=digit.max().max())
        self.force_refresh()

    def force_refresh(self) -> None:
        """Redraw the whole canvas"""
        fig_size = self.fig.get_size_inches()
        self.fig.set_size_inches(fig_size)
        self.fig.canvas.draw()

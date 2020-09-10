import nptsne
import numpy as np 
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.style as mplstyle
from matplotlib import colors as mcolors
from matplotlib.backends.backend_qt5agg import FigureCanvas 
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QLabel, QSpinBox
from PyQt5.QtCore import pyqtSlot
from PIL import Image

class HyperspectralImageCanvas(FigureCanvas):
    """This is the matplotlib based GUI for a single analysis
       It assumes the analysis is simple image data (this could be abstracted)"""
    
    def __init__(self, parent=None, width=2, height=2):
        """View a composite image based
           on a subselection of the data 
        """
        
        self.fig = Figure(figsize=(width, height)) 
        self.ix = self.fig.add_subplot(111)
        self.ix.set_xticks([])
        self.ix.set_yticks([])
        mplstyle.use("fast")
        super(HyperspectralImageCanvas, self).__init__(self.fig)
        self.fig.tight_layout(pad=0)
        plt.show(block=False)
    
    def init_plot(self, data, image_dimensions, index):
        self.image_dimensions = image_dimensions
        # alpha will cause fade to black background
        self.background = Image.fromarray(np.full(image_dimensions, 0, dtype=np.uint8), 'L')
        self.data = np.reshape(data, (*image_dimensions, data.shape[1]))
        print(f"Reshaped: {self.data.shape}")        
        self.alphas = np.full(image_dimensions, 255, dtype=np.uint8)
        self.index = 0
        
        # start with a image 0
        self.display_img = self.ix.imshow(self.data[..., self.index], interpolation='bilinear', cmap='gray', vmin=0, vmax=255)

    def set_image_index(self, index):
        self.index = index
        image = Image.fromarray(self.data[..., index], 'L') # 8-bit black white
        # print(f"Image size: {image.size}")
        alfa_im = Image.fromarray(self.alphas, 'L')
        # print(f"Alfa size: {alfa_im.size}")
        comp_image = Image.composite(image, self.background, alfa_im)
        comp_array = np.array(comp_image)
        # print(f"comp array shape: {comp_array.shape}")
        self.display_img.set_array(np.reshape(comp_array, self.image_dimensions))
        self.force_refresh()
        
    def set_selection_alpha(self, mask):
        self.alphas = np.reshape(mask * 255, self.image_dimensions).astype(np.uint8)
        self.set_image_index(self.index)
        
    def force_refresh(self):
        fig_size = self.fig.get_size_inches()
        self.fig.set_size_inches(fig_size)
        self.fig.canvas.draw()        
        
class HyperspectralImageViewer(QWidget): 
    def __init__(self):
        super(QWidget, self).__init__()
        self.main_layout = QVBoxLayout(self)
        self.image_widget = HyperspectralImageCanvas(self)
        self.main_layout.addWidget(self.image_widget)
        self.control_layout = QHBoxLayout(self)
        self.control_layout.addWidget(QLabel("Select image dimension: "))
        self.image_spin = QSpinBox(self)
        self.image_spin.setValue(0)
        self.image_spin.setRange(0,0)
        self.image_spin.valueChanged[int].connect(self.on_image_changed)
        self.control_layout.addWidget(self.image_spin)
        self.main_layout.addLayout(self.control_layout)
        self.main_layout.setStretch(0, 1)
        self.setLayout(self.main_layout)
        
    def init_plot(self, data, image_dimensions):
        num_images = data.shape[1]
        self.data = data
        print(f"num images {num_images}")
        self.image_spin.setRange(0, num_images-1)
        self.image_widget.init_plot(data, image_dimensions, self.image_spin.value())
        
    @pyqtSlot(int)
    def on_image_changed(self, img_index):     
        self.image_widget.set_image_index(img_index)
        
    def set_dynamic_indexes(self, indexes):
        pass
        
    def set_static_mask(self, mask):
        """ Accept 1D num py array of 0 or 1.0 mask values """
        self.image_widget.set_selection_alpha(mask)        
    
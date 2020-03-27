import nptsne
import numpy as np 
from nptsne import hsne_analysis
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.gridspec import GridSpec
import matplotlib.cm as cm
import matplotlib.patches as patches
from AnalysisGui import AnalysisGui

raw = np.fromfile('MNIST_1000.bin', np.float32)
X = np.reshape(raw, (1000, 784))
hsne = nptsne.HSne(True)
hsne.create_hsne(X, 2)
hsne.save('mnist_1000_hsne.bin')
analysis_model = hsne_analysis.AnalysisTree(hsne)
top_analysis = analysis_model.top_analysis

top_analysis_gui = AnalysisGui(X, top_analysis)

# TODO Use the analysis model to make more analyses
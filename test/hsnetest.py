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

all_analyses_per_scale = {top_analysis.scale_id: {top_analysis.id: top_analysis}}
analysis_guis = {}

def make_new_analysis(analysis, selected_indexes):
    """Callback to start a sub analysis in the analysis model"""
    print("Drilling down to new analysis")
    new_analysis = analysis_model.add_new_analysis(analysis, selected_indexes)
    print("Updated analysis hierarchy: ")
    print(analysis_model.analysis_container)
    print("Starting analysis GUI")
    analysis_guis[new_analysis.id] = AnalysisGui(X, new_analysis, make_new_analysis)

    
top_analysis_gui = AnalysisGui(X, top_analysis, make_new_analysis)
analysis_guis[top_analysis.id] = top_analysis_gui

# TODO Display a tree of the scales/analyses
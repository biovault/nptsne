import nptsne
import numpy as np 
from nptsne import hsne_analysis
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.gridspec import GridSpec
import matplotlib.cm as cm
import matplotlib.patches as patches
from AnalysisGui import AnalysisGui


raw = np.fromfile('MNIST_70000.bin', np.uint8)
X = np.reshape(raw, (70000, 784))
hsne = nptsne.HSne(True)
number_of_scales = 4
hsne.create_hsne(X, number_of_scales)
hsne.save('mnist_1000_hsne.bin')
analysis_model = hsne_analysis.AnalysisModel(hsne)
top_analysis = analysis_model.top_analysis

all_analyses_per_scale = {top_analysis.scale_id: {top_analysis.id: top_analysis}}
analysis_guis = {}

def remove_analysis(id):
    removed_ids = analysis_model.remove_analysis(id)
    print("Updated analysis hierarchy: ")
    print(analysis_model.analysis_container)
    # TODO close associated GUIs
    for id in removed_ids:
        gui = analysis_guis.get(id, None)
        if not gui is None:
            gui.kill()
            del analysis_guis[id]
    return removed_ids
    
def add_analysis(analysis, selected_indexes):
    """Callback to start a sub analysis in the analysis model"""
    print("Drilling down to new analysis")
    new_analysis = analysis_model.add_new_analysis(analysis, selected_indexes)
    print("Updated analysis hierarchy: ")
    print(analysis_model.analysis_container)
    print("Starting analysis GUI")
    analysis_guis[new_analysis.id] = AnalysisGui(X, new_analysis, add_analysis, remove_analysis)
    

top_analysis_gui = AnalysisGui(X, top_analysis, add_analysis, remove_analysis)
analysis_guis[top_analysis.id] = top_analysis_gui

# TODO Display a tree of the scales/analyses
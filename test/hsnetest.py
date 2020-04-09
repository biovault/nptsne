import nptsne
import numpy as np 
from nptsne import hsne_analysis
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.gridspec import GridSpec
import matplotlib.cm as cm
import matplotlib.patches as patches
from AnalysisGui import AnalysisGui
import sys
from ModelGui import ModelGui, AnalysisEvent
import queue
import PIL

def get_default_embedding_type():
    """GPU embedder will not work on remote desktop """
    default_embedder_type = hsne_analysis.EmbedderType.GPU
    if sys.platform == 'win32':
        # pip install pywin32
        try:
            import win32api
            isWindows = True
            SM_REMOTESESSION = 0x1000
            if 1 == win32api.GetSystemMetrics(SM_REMOTESESSION):
               default_embedder_type = hsne_analysis.EmbedderType.CPU 
        except ImportError as exception:
            print(exception, exception.mess)
            print("Assuming GPU")
    return default_embedder_type       

default_embedder_type = get_default_embedding_type()
print("Embedder: ", default_embedder_type)

# TODO Add loader to allow:
# 1.) loading other data
# 2.) reloading a previous .hsne output

raw = np.fromfile('MNIST_70000.bin', np.uint8)
X = np.reshape(raw, (70000, 784))
hsne = nptsne.HSne(True)
number_of_scales = 4
hsne.create_hsne(X, number_of_scales)
hsne.save('MNIST_70000.hsne')

analysis_model = hsne_analysis.AnalysisModel(hsne, default_embedder_type)
top_analysis = analysis_model.top_analysis

# Queue is used to pass changes in the analyses to the ModelGui

analysis_event_queue = queue.Queue()

all_analyses_per_scale = {top_analysis.scale_id: {top_analysis.id: top_analysis}}
analysis_guis = {}

# Utility function for queuing an ADDED analysis
def queue_new_analysis(analysis):
    analysis_event_queue.put({
        'event': AnalysisEvent.ADDED, 
        'id': analysis.id, 
        'name': str(analysis), 
        'scale_id': analysis.scale_id, 
        'parent_id': analysis.parent_id,
        'number_of_points': analysis.number_of_points})   
        
# Three callbacks for the AnalysisGui used to communicate status
# 1.)AnalysisEvent.REMOVED
def remove_analysis(id):
    removed_ids = analysis_model.remove_analysis(id)
    print("Updated analysis hierarchy: ")
    print(analysis_model.analysis_container)
    # TODO close associated GUIs
    for id in removed_ids:
        analysis_event_queue.put({
            'event': AnalysisEvent.REMOVED, 
            'id': id})
        gui = analysis_guis.get(id, None)
        if not gui is None:
            gui.kill()
            del analysis_guis[id]
    return removed_ids
    
# 2.) AnalysisEvent.ADDED   
def add_analysis(analysis, selected_indexes):
    """Callback to start a sub analysis in the analysis model"""
    print("Drilling down to new analysis")
    new_analysis = analysis_model.add_new_analysis(analysis, selected_indexes)
    print("Updated analysis hierarchy: ")
    print(analysis_model.analysis_container)
    print("Starting analysis GUI")
    analysis_guis[new_analysis.id] = AnalysisGui(X, new_analysis, add_analysis, remove_analysis, analysis_stopped)
    queue_new_analysis(new_analysis)

# 3.) AnalysisEvent.FINISHED     
def analysis_stopped(analysis_gui):
    completed_analysis = analysis_gui.analysis
    analysis_event_queue.put({
        'event': AnalysisEvent.FINISHED, 
        'id': completed_analysis.id, 
        'name': analysis_gui.figure_id,
        'image_buf': analysis_gui.get_figure_as_buffer()})    

# Callbacks for the tree control
# 1.) Clicking an item raises the window
def tree_click(analysis_id):
    analysis_gui = analysis_guis[analysis_id]
    analysis_gui.win_raise()

# 2.) deleting an item (the D key) removes the analysis (and children)    
def tree_del(analysis_id): 
    print('D on : ', analysis_id)
    remove_analysis(analysis_id)
    
# Display a tree of the scales/analyses
model_gui = ModelGui(analysis_model, analysis_event_queue, tree_click, tree_del)

# The AnalysisGui is non-blocking  
# start with an analysis GUI containing all top scale landmarks 
top_analysis_gui = AnalysisGui(X, top_analysis, add_analysis, remove_analysis, analysis_stopped)
analysis_guis[top_analysis.id] = top_analysis_gui
queue_new_analysis(top_analysis)
# The ModelGui is blocking
model_gui.run()





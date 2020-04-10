#!/usr/bin/env python3

# The nptsne package and the hsne_analysis navigation support
import nptsne
from nptsne import hsne_analysis
# The demo GUI
from AnalysisGui import AnalysisGui
from ModelGui import ModelGui, AnalysisEvent
# Standard support packages
import numpy as np 
from pathlib import Path
import queue
import sys
from tkinter import messagebox

# Handle running this via Windows Remote Desktop (i.e. no GPU)
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


analysis_model = None
data = None
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
    global analysis_model
    global analysis_guis
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
    global data
    global analysis_model
    global analysis_guis
    print("Drilling down to new analysis")
    new_analysis = analysis_model.add_new_analysis(analysis, selected_indexes)
    print("Updated analysis hierarchy: ")
    print(analysis_model.analysis_container)
    print("Starting analysis GUI")
    analysis_guis[new_analysis.id] = AnalysisGui(data, new_analysis, add_analysis, remove_analysis, analysis_stopped)
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
    
# 2.) Tree remove - returns a list of ananlysis ids to deleter
def tree_del(analysis_ids):
    for id in analysis_ids:
        if id in analysis_guis:
            remove_analysis(id)

# 3.) Load an numpy file - offer the user the chance to preload an hsnefile if one is avaliable    
def tree_load(filename):
    data_file_path = Path(filename)
    hsne_file_path = None
    test_file_path = data_file_path.with_suffix('.hsne')
    if test_file_path.exists():
        if messagebox.askyesno(
            title='Pre-existing hSNE file', 
            message=f'Do you wish toload the pre-calculate hSNE file: {test_file_path} ?') :
            hsne_file_path = test_file_path

    data = np.load(data_file_path)
    start_hsne(data, data_file_path, hsne_file_path)
    
model_gui = None
 
def start_hsne(X, data_file, hsne_file):
    global analysis_model
    global data
    # raw = np.fromfile('MNIST_70000.bin', np.uint8)
    # X = np.reshape(raw, (70000, 784))
    hsne = nptsne.HSne(True)
    number_of_scales = 4
    if hsne_file is None:
        print("hSNE from scratch")
        hsne.create_hsne(X, number_of_scales)
    else:
        print("existing hSNE")
        hsne.create_hsne(X, str(hsne_file))
        hsne_file = data_file.with_suffix('.hsne')
        hsne.save(str(hsne_file))
    
    print("start analysis model")
    data = X
    analysis_model = hsne_analysis.AnalysisModel(hsne, default_embedder_type)
    
    top_analysis = analysis_model.top_analysis

    all_analyses_per_scale = {top_analysis.scale_id: {top_analysis.id: top_analysis}}

    
    # The AnalysisGui is non-blocking  
    # start with an analysis GUI containing all top scale landmarks 
    top_analysis_gui = AnalysisGui(data, top_analysis, add_analysis, remove_analysis, analysis_stopped)
    analysis_guis[top_analysis.id] = top_analysis_gui
    queue_new_analysis(top_analysis)
    # Queue is used to pass changes in the analyses to the ModelGui
    # The ModelGui is blocking
    model_gui.set_analysis_model(analysis_model)


analysis_event_queue = queue.Queue()    
# Display a tree of the scales/analyses 
model_gui = ModelGui(analysis_event_queue, tree_click, tree_del, tree_load)
model_gui.run()





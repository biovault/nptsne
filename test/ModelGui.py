from tkinter import *
from tkinter import ttk
import copy
import queue
import PIL
from PIL import ImageTk

from enum import Enum

class AnalysisEvent(Enum):
    ADDED = 1
    FINISHED = 2
    REMOVED = 3
    
class ModelGui():
    """This is the tkinter based visulization of the analysis model"""
    
    NO_PARENT_ID = 0xFFFFFFFF
    
    def __init__(self, analysis_model, analysis_event_queue):
        """Create a new analysis model gui 
        """

        self.model = analysis_model
        self.top_scale =  analysis_model.top_scale_id
        self.analysis_event_queue = analysis_event_queue
        self.root_id = str(0)
        self.images = [] # used to save image references otherwise they are GCed
        
    def run(self):
        self.root = Tk()
        self.root.title("Analysis Tree")
        
        ttk.Style().configure('Treeview', rowheight=30)
        self.tree = ttk.Treeview(self.root, height = 10)

        self.tree["columns"] = ("id", "numpoints")
       
        self.tree.column("id", width=20, anchor='center')
        self.tree.column("numpoints", width=20, anchor='center')
       
        self.tree.heading("id", text="Id")
        self.tree.heading("numpoints", text="# Points")
        
        self.tree.pack(fill='both', expand=True)
        self.root.after(100, self.update)
        self.root.mainloop()

   
    def update(self):
        self.update_tree()
        self.root.after(1000, self.update)
        
    def update_tree(self):
        # Update tree based on queued events
        while True:
            event = {}
            try:
                event = self.analysis_event_queue.get_nowait()
            except queue.Empty:
                break
               
            if event['event'] == AnalysisEvent.ADDED:
                self.add_analysis(event['id'], event['name'], event['scale_id'], event['parent_id'], event['number_of_points'])
                continue
            if event['event'] == AnalysisEvent.FINISHED:
                self.finish_analysis(event['id'], event['name'], event['image_buf'])
                continue
            if event['event'] == AnalysisEvent.REMOVED:
                self.remove_analysis(event['id'])                
                
    def add_analysis(self, id, name, scale_id, parent_id, numpoints):
        # print("add ", id)
        im = PIL.Image.new('RGB', (30,30), (200,200,200))
        tk_thumbnail = ImageTk.PhotoImage(im)
        self.images.append(tk_thumbnail)
        if parent_id == ModelGui.NO_PARENT_ID:
            self.clear()
            x = self.tree.insert("", 'end', iid=str(id), text=name, image=tk_thumbnail, values=(id, numpoints))
            self.root_id = str(id)
            # print("Inserted id: ", x)
        else:
            if self.tree.exists(str(parent_id)):
                x = self.tree.insert(str(parent_id), 'end', iid=str(id), text=name, image=tk_thumbnail, values=(id, numpoints))
                self.tree.see(str(id))
                # print("Inserted id: ", x)
            
        
    def remove_analysis(self, id):
        # At the top clear everything and empty the queue
        # print("remove ", id)
        if id == self.root_id:
            self.clear()
            while True:            
                event = self.analysis_event_queue.get()
                if event is None:
                    break
        else:
            if self.tree.exists(str(id)):
                self.tree.delete(str(id))

    def finish_analysis(self, id, name, image_buf):
        # print("finished ", id)
        img = PIL.Image.open(image_buf)
        thumbnail = img.resize((30,30), PIL.Image.ANTIALIAS)
        # thumbnail.show()
        tk_thumbnail = ImageTk.PhotoImage(thumbnail)
        self.images.append(tk_thumbnail)
       
        self.tree.item(str(id), image=tk_thumbnail)
                
    def callback(self):
       self.root.quit() 
    
    def clear(self):
        self.tree.delete(*self.tree.get_children())


# Example Analysis
# Scale: 3
        # Analysis[id=0, num points=454, scale=3]

# Scale: 2
        # Analysis[id=1, num points=230, scale=2]    
from tkinter import (ttk, Tk, filedialog, messagebox)
import copy
import queue
import os
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
    
    def __init__(self, analysis_event_queue, select, delete, load):
        """Create a new analysis model gui 
        """
        
        self.analysis_event_queue = analysis_event_queue
        self.root_id = str(0)
        self.images = [] # used to save image references otherwise they are GCed
        self.select_callback = select
        self.delete_callback = delete
        self.load_callback = load
    
    def set_analysis_model(self, analysis_model):
        # TODO empt event queue
        self.model = analysis_model
        self.top_scale =  analysis_model.top_scale_id
        
    def run(self):
        self.root = Tk()
        self.root.title("Analysis Tree")
        self.treeframe = ttk.Frame(self.root, width=700, height=400, relief="groove") 
        self.treeframe.pack(fill='both', expand=True)
        
        ttk.Style().configure('Treeview', rowheight=30)
        self.tree = ttk.Treeview(self.treeframe, height = 10)

        self.tree["columns"] = ("id", "numpoints")
       
        self.tree.column("id", width=20, anchor='center')
        self.tree.column("numpoints", width=20, anchor='center')
       
        self.tree.heading("id", text="Id")
        self.tree.heading("numpoints", text="# Points")
        
        self.tree.grid(column=0, row=0, columnspan=5, rowspan=4, sticky='nsew', in_=self.treeframe)
        self.treeframe.grid_columnconfigure(0, weight=1)
        self.treeframe.grid_rowconfigure(0, weight=1)
        
        self.tree.bind("<<TreeviewSelect>>", self.select)
        
        self.delbtn = ttk.Button(self.treeframe, text="Delete selected")
        self.delbtn.grid(column=0, row=4, columnspan=2, sticky='s', in_=self.treeframe)
        self.delbtn.bind('<Button-1>', self.delete)
        
        self.control_frame = ttk.Frame(self.treeframe)
        self.control_frame.grid(column=6, row=0, rowspan=4, sticky='nsew', in_=self.treeframe)
        
        self.loadbtn = ttk.Button(self.control_frame, text="Load")
        self.loadbtn.grid(column=0, row=0, columnspan=1, sticky='new', in_=self.control_frame)
        self.loadbtn.bind('<Button-1>', self.load)
        
        self.loadlabelbtn = ttk.Button(self.control_frame, text="Load labels")
        self.loadlabelbtn.grid(column=0, row=1, columnspan=1, sticky='new', in_=self.control_frame)
        self.loadlabelbtn.bind('<Button-1>', self.load_labels)
        
        self.control_frame.rowconfigure(2, weight=1)

        self.gobtn = ttk.Button(self.control_frame, text="Start")
        self.gobtn.grid(column=0, row=3, columnspan=1, rowspan=1, sticky='sew', in_=self.control_frame)
        self.gobtn.bind('<Button-1>', self.go)         

        
        self.root.after(100, self.update)
        self.name = None
        self.label_name = None
        self.root.mainloop()

    def ask_load_hsne(self, file_path):
        print(f"Found file: {file_path}")
        return messagebox.askyesno(
            title='Pre-existing hSNE file', 
            message=f'Do you wish to load the pre-calculated hSNE file: {file_path} ?',
            parent = self.root) 
            
    def select(self, event):
        item = self.tree.item(self.tree.focus())
        if not item: return
        values = item["values"]
        if len(values) == 0: return
        self.select_callback(int(values[0]))
        self.root.lift()
        self.tree.focus(values[0])  
        
    def delete(self, event):
        selection = self.tree.selection()
        self.delete_callback([int(x) for x in selection])
        
    def load(self, event):
        workdir = os.path.dirname(os.path.abspath(__file__))
        self.name = filedialog.askopenfilename(initialdir=workdir, filetypes=[("Numpy files", "*.npy")], title='Open a numpy file where each row is a data point and columns are dimensions' )    
    
    def load_labels(self, event):
        workdir = os.path.dirname(os.path.abspath(__file__))
        self.label_name = filedialog.askopenfilename(initialdir=workdir, filetypes=[("Numpy files", "*.npy")], title='Open a numpy file where each row is an integer label' )
        
    def go(self, event):
        if self.name:
            self.load_callback(self.name, self.label_name)
        
        
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

   
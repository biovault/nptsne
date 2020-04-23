from tkinter import (ttk, Tk, filedialog, messagebox, IntVar, StringVar)
import copy
import queue
import os
import PIL
from PIL import ImageTk
from pathlib import Path

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
        self.content = ttk.Frame(self.root, width=1000, height=400, relief="groove") 
        self.content.pack(fill='both', expand=True)
        
        ttk.Style().configure('Treeview', rowheight=30)
        self.tree = ttk.Treeview(self.content)

        self.tree["columns"] = ("id", "numpoints")
        self.tree.column("#0",minwidth=300,width=300)
       
        self.tree.column("id", minwidth=40, width=60, anchor='center', stretch=False)
        self.tree.column("numpoints", minwidth=60, width=60, anchor='center', stretch=False)
       
        self.tree.heading("id", text="Id")
        self.tree.heading("numpoints", text="# Points")
        
        self.tree.grid(column=0, row=0, columnspan=5, rowspan=8, sticky='nsew')
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)
        
        self.tree.bind("<<TreeviewSelect>>", self.select)
        
        self.delbtn = ttk.Button(self.content, text="Delete selected")
        self.delbtn.grid(column=0, row=9, columnspan=2, sticky='s')
        self.delbtn.bind('<Button-1>', self.delete)
        
        #******* Right hand controls ****************
        
        #******* hSNE controls frame ****************
        self.control_frame = ttk.Labelframe(self.content, text='hSNE settings')
        self.control_frame.grid(column=6, row=0, rowspan=4, sticky='nsew')
        
        #******* hSNE controls ****************
        
        self.scales_val = IntVar()
        self.scales_spin = ttk.Spinbox(self.control_frame, from_=1, to=10, textvariable=self.scales_val)
        self.scales_spin.grid(column=1, row=0, columnspan=1, sticky='nse')
        self.scales_val.set(4)
        
        self.scales_label = ttk.Label(self.control_frame, text='Scales:')
        self.scales_label.grid(column=0, row=0, columnspan=1, sticky='nsw')
        
        self.loadbtn = ttk.Button(self.control_frame, text="Data")
        self.loadbtn.grid(column=0, row=1, columnspan=1, sticky='new')
        self.loadbtn.bind('<Button-1>', self.load)
        
        self.load_contents = StringVar()
        self.load_contents.set('<choose data .npy>')
        self.load_label = ttk.Label(self.control_frame, textvariable=self.load_contents)
        self.load_label.grid(column=1, row=1, columnspan=1, sticky='nsw')        
        
        self.loadlabelbtn = ttk.Button(self.control_frame, text="Labels")
        self.loadlabelbtn.grid(column=0, row=2, columnspan=1, sticky='new')
        self.loadlabelbtn.bind('<Button-1>', self.load_labels)
        
        self.loadlabels_contents = StringVar()
        self.loadlabels_contents.set('<optionally choose labels>')
        self.loadlabels_label = ttk.Label(self.control_frame, textvariable=self.loadlabels_contents)
        self.loadlabels_label.grid(column=1, row=2, columnspan=1, sticky='nsw')         
        

        #******* embedding controls frame ****************
        self.embedding_frame = ttk.Labelframe(self.content, text='Embedder settings')
        self.embedding_frame.grid(column=6, row=3, sticky='nsew', in_=self.content)
        
        #******* embedding controls ****************
        self.iters_val = IntVar()
        self.iters_spin = ttk.Spinbox(self.embedding_frame, from_=350, to=1000, increment=5, textvariable=self.iters_val)
        self.iters_spin.grid(column=1, row=0, columnspan=1, sticky='nse')
        self.iters_val.set(350)
        
        self.iters_label = ttk.Label(self.embedding_frame, text='Iterations:')
        self.iters_label.grid(column=0, row=0, columnspan=1, sticky='nsw')
        
        #********************************************
        # Padding
        self.content.rowconfigure(4, weight=1) 
        
        self.gobtn = ttk.Button(self.content, text="Start")
        self.gobtn.grid(column=6, row=5, sticky='nsew', in_=self.content)
        self.gobtn.bind('<Button-1>', self.go)  
        #*******End Right hand controls***********************
        # disable the start button until at least data is set
        self.gobtn.state(['disabled'])
        self.root.after(100, self.update)
        self.name = None
        self.label_name = None
        self.root.mainloop()

    @property
    def iterations(self):
        return self.iters_val.get()
        
    @property
    def scales(self):
        return self.scales_val.get()
        
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
        if self.name:
            self.gobtn.state(['!disabled'])
            self.load_contents.set(Path(self.name).name)
    
    def load_labels(self, event):
        workdir = os.path.dirname(os.path.abspath(__file__))
        self.label_name = filedialog.askopenfilename(initialdir=workdir, filetypes=[("Numpy files", "*.npy")], title='Open a numpy file where each row is an integer label' )
        if self.label_name:
            self.loadlabels_contents.set(Path(self.label_name).name)
        
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

   
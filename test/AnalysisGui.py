import nptsne
import numpy as np 
from nptsne import hsne_analysis
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.gridspec import GridSpec
import matplotlib.cm as cm
import matplotlib.patches as patches

class AnalysisGui:
    """This is the matplotlib based GUI for a single analysis
       It assumes the analysis is simple image data (this could be abstracted)"""
    
    def __init__(self, data, analysis):
        self.data = data
        self.analysis = analysis
        
        # Plot and image definition
        self.fig = plt.figure()
        # space for the plot and the digit display - spec is row,col
        gs = GridSpec(4,4)
        self.ax = self.fig.add_subplot(gs[:4,:3])
        self.ix = self.fig.add_subplot(gs[0,3])
        self.ix.set_xticks([])
        self.ix.set_yticks([])
        self.scatter = None
        self.rect = None
        self.extent = 2.8
        
        # Animation support 
        # if matplot lib rendering is slow do a number of iterations per frame
        # Total iterations = num_frames X iters_per_frame
        self.num_frames = 350
        self.iters_per_frame = 1
        self.stop_iter = False
        dummydata = np.zeros((28,28), dtype=np.float32)
        self.composite_digit = np.zeros((784,))
        self.digit_im = self.ix.imshow(dummydata, interpolation='bilinear', cmap='gray', vmin=0, vmax=255)
        
        # Callbacks
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_over)
        self.fig.canvas.mpl_connect('key_press_event', self.on_keypress)
        self.fig.canvas.mpl_connect('close_event', self.stop_loop)
        self.fig.canvas.mpl_connect('button_press_event', self.on_start_select)
        self.fig.canvas.mpl_connect('button_release_event', self.on_end_select)        
        
        # Brush support values    
        self.in_selection = False
        self.rect_xy = (None, None)  # start of selection rectangle
        self.dim_xy = (None, None)  # displacement
        self.rorg_xy = (None, None)  # The bottom left corner   

        # Fire up the plot - a continuous non blocking animation is run to refresh the GUI
        self.ani = animation.FuncAnimation(self.fig, self.iterate_tSNE, init_func=self.start_plot, frames=range(self.num_frames), interval=0.5, repeat=True, blit=True)
        plt.show(block=False)
        self.fig.canvas.start_event_loop(timeout=-1)
        
    def start_plot(self):
        self.ax.set(xlim=(-self.extent, self.extent), ylim=(-self.extent, self.extent))
        embedding = self.analysis.embedder.embedding
        x = embedding[:,0]
        y = embedding[:,1]
        self.scatter = self.ax.scatter(x,y,s=self.analysis.landmark_weights * 8, c='b', alpha=0.4, picker=1)
        rt = patches.Rectangle((-self.extent,-self.extent),0.1,0.1,linewidth=0.5,edgecolor='r',facecolor='none', alpha=0)
        self.rect = self.ax.add_patch(rt)
        return self.scatter, self.rect, 

    def quit(self):
        plt.close()

    def stop_loop(self, event):
        self.fig.canvas.stop_event_loop()    
    
    def iterate_tSNE(self, i):
        if not self.stop_iter: 
            for j in range(self.iters_per_frame):
                self.analysis.embedder.do_iteration()
            if i == self.num_frames - 1:
                self.stop_iter = True
        
        # can auto scale the axes
        # min = np.amin(embedding, axis=0)
        # max = np.amax(embedding, axis=0)
        # ax.set(xlim=(min[0], max[0]), ylim=(min[1], max[1]))
        self.scatter.set_offsets(self.analysis.embedder.embedding)
        digit = np.reshape(self.composite_digit, (28,28))
        self.digit_im.set_array(digit)
        # print("Digit data", digit)
        #ix.imshow(digit, interpolation='bilinear', cmap='gray', vmin=0, vmax=255)
        #plt.draw()
        return [self.scatter, self.rect, self.digit_im, ]

    def on_over(self, event): 
        """Handle two modes:
            1) Digit display mode
            2) Rectangle brush mode """
            
        if not self.in_selection: 
            # Show digits related to the landmark point
            cont, index = self.scatter.contains(event)
            if cont:
                # print("Landmark index(es): ", index['ind'])
                self.composite_digit = np.zeros((784,))
                for i in index['ind']:
                    digit_idx = self.analysis.landmark_orig_indexes[i] 
                    self.composite_digit = np.add(self.composite_digit, self.data[digit_idx,:])
                self.composite_digit = self.composite_digit/len(index['ind']) 
        else:
            #Calculate the origin and dimensions of the selection rectangle
            if not event.inaxes == self.scatter.axes: return
            width = abs(event.xdata - self.rect_xy[0])
            height = abs(event.ydata - self.rect_xy[1])
            org_x = min(self.rorg_xy[0], event.xdata)
            org_y = min(self.rorg_xy[1], event.ydata)
            self.rorg_xy = (org_x, org_y)
            self.rect.set_xy(self.rorg_xy)
            self.dim_xy = (width, height)
            self.rect.set_width(width)
            self.rect.set_height(height)
            self.rect.set_alpha(0.4)
        

    def on_keypress(self, event):
        if event.key in ['q', 'Q', 'escape']:
            self.quit()

    def on_start_select(self, event):
        self.in_selection = True
        if not event.inaxes == self.scatter.axes: return
        self.rect_xy = (event.xdata, event.ydata)
        self.rorg_xy = self.rect_xy
        print(self.rect_xy)

        
    def on_end_select(self, event):
        self.in_selection = False
        self.rect.set_alpha(0.0)
        self.get_selected_indexes()
        
    def get_selected_indexes(self):
        """Get the embedding points that fall in the current selection rectangle"""
        embedding = self.analysis.embedder.embedding
        indexes = np.arange(embedding.shape[0])
        selected_indexes = indexes[(embedding[:,0] > self.rorg_xy[0]) & (embedding[:,0] < self.rorg_xy[0] + self.dim_xy[0]) 
            & (embedding[:,1] > self.rorg_xy[1]) & (embedding[:,1] < self.rorg_xy[1] + self.dim_xy[1])]
        print(selected_indexes)
    
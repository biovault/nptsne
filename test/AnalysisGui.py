import nptsne
import numpy as np 
from nptsne import hsne_analysis
import matplotlib.pyplot as plt
import matplotlib.style as mplstyle 
from matplotlib import animation
from matplotlib.gridspec import GridSpec
import matplotlib.cm as cm
import matplotlib.patches as patches
import io
import time

class AnalysisGui:
    """This is the matplotlib based GUI for a single analysis
       It assumes the analysis is simple image data (this could be abstracted)"""
    
    def __init__(self, data, analysis, make_new_analysis, remove_analysis, analysis_stopped, top_level=False):
        """Create a new analysis gui

            
        """
        
        mplstyle.use("fast")
        self.data = data
        self.analysis = analysis
        self.make_new_analysis = make_new_analysis
        self.remove_analysis = remove_analysis
        self.analysis_stopped = analysis_stopped
        self.top_level = top_level
        
        # Plot and image definition
        self.fig = plt.figure(num=str(analysis))
        # space for the plot and the digit display - spec is row,col
        gs = GridSpec(4,4)
        self.ax = self.fig.add_subplot(gs[:4,:3])
        self.ax.margins(0.05, 0.05)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ix = self.fig.add_subplot(gs[0,3])
        self.ix.set_xticks([])
        self.ix.set_yticks([])
        self.fig.tight_layout()
        self.scatter = None
        self.rect = None
        self.extent = 2.8
        self.cleanup = True
        
        # Animation support 
        # if matplot lib rendering is slow do a number of iterations per frame
        # Total iterations = num_frames X iters_per_frame
        self.num_frames = 70
        self.iters_per_frame = 5
        self._stop_iter = False
        self._iter_count = 0
        dummydata = np.zeros((28,28), dtype=np.float32)
        self.composite_digit = np.zeros((784,))
        self.digit_im = self.ix.imshow(dummydata, interpolation='bilinear', cmap='gray', vmin=0, vmax=255)
        
        # Callbacks
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_over)
        self.fig.canvas.mpl_connect('key_press_event', self.on_keypress)
        self.fig.canvas.mpl_connect('close_event', self.stop_loop)
        self.fig.canvas.mpl_connect('button_press_event', self.on_start_select)
        self.fig.canvas.mpl_connect('button_release_event', self.on_end_select)  
        self.fig.canvas.mpl_connect('close_event', self.handle_close)        
        
        # Brush support values    
        self.in_selection = False
        self.rect_xy = (None, None)  # start of selection rectangle
        self.dim_xy = (None, None)  # displacement
        self.rorg_xy = (None, None)  # The bottom left corner   

        # Fire up the plot - a continuous non blocking animation is run to refresh the GUI
        self.ani = animation.FuncAnimation(self.fig, self.iterate_tSNE, init_func=self.start_plot, frames=range(self.num_frames), interval=100, repeat=True, blit=True)

        plt.show(block=False)    

    def win_raise(self):
        plt.figure(str(self.analysis))
        cfm = plt.get_current_fig_manager()
        #cfm.window.activateWindow()
        cfm.window.raise_()
        
    def start_plot(self):
        # self.ax.set(xlim=(-self.extent, self.extent), ylim=(-self.extent, self.extent))
        embedding = self.analysis.embedding
        #if 0 == embedding.shape[0]:
        #    embedding = np.zeros((self.data.shape[0], 2))
        # print("Embedding shape: ", embedding.shape)
        x = embedding[:,0]
        y = embedding[:,1]
        self.scatter = self.ax.scatter(x,y,s=self.analysis.landmark_weights * 8, c='b', alpha=0.4, picker=10)
        #self.ax.relim()
        #self.ax.autoscale_view()
        rt = patches.Rectangle((-self.extent,-self.extent),0.1,0.1,linewidth=0.5,edgecolor='r',facecolor='none', alpha=0)
        self.rect = self.ax.add_patch(rt)
        return self.scatter, self.rect, 

    def quit(self):
        """Close the plot and cleanup model"""
        plt.close(self.fig)
        
    def kill(self):
        """Close the plot with no cleanup of id in model"""
        self.cleanup = False
        plt.close(self.fig)
        
    def handle_close(self, evt):
        if self.cleanup: 
            self.remove_analysis(self.analysis.id)
        del self.analysis
    
    def stop_loop(self, event):
        self.fig.canvas.stop_event_loop()    
    
    def iterate_tSNE(self, i):
        send_stop_event = False
        if not self._stop_iter: 
            for j in range(self.iters_per_frame):
                self.analysis.do_iteration()
                self._iter_count = i*self.iters_per_frame + j
                self.fig.canvas.toolbar.set_message(f"Iteration: {self._iter_count}")
                
            if i == self.num_frames - 1:
                self._stop_iter = True
                send_stop_event = True
        
        # can auto scale the axes
        embedding = self.analysis.embedding
        min = np.amin(embedding, axis=0)
        max = np.amax(embedding, axis=0)

        #self.ax.autoscale_view()
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        
        #    self.ax.set(xlim=(min[0] - 1, max[0] + 1), ylim=(min[1] - 1, max[1] + 1))

        self.scatter.set_offsets(embedding)
        if (xlim[1] - xlim[0]) > (max[0] - min[0]) or (ylim[1] - ylim[0]) > (max[1] - min[1]) : 
            self.ax.set(xlim=(min[0] - 2, max[0] + 2), ylim=(min[1] - 2, max[1] + 2))
            self.ax.relim()
            self.ax.autoscale_view()
        digit = np.reshape(self.composite_digit, (28,28))
        self.digit_im.set_array(digit)
        # print("Digit data", digit)
        #ix.imshow(digit, interpolation='bilinear', cmap='gray', vmin=0, vmax=255)
        #plt.draw()
        if send_stop_event:
            plt.figure(str(self.analysis))
            def delayed_notification(analysis_gui):
                time.sleep(0.5)
                # Force a redraw by resizing the figure
                fig_size = plt.gcf().get_size_inches()
                plt.gcf().set_size_inches(1.0 * fig_size)
                analysis_gui.analysis_stopped(analysis_gui)
            #t = threading.Thread(target=delayed_notification, args=(self,)) 
            #t.start()
            delayed_notification(self)
        # Quirk - when only the top level plot is visible 
        # the screent is not correctly updated
        if self.top_level == 0:
            if i % 10 == 0:
                fig_size = plt.gcf().get_size_inches()
                plt.gcf().set_size_inches(1.0 * fig_size)            
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
        self.dim_xy = (0, 0)
        self.rect.set_xy(self.rorg_xy)
        self.rect.set_width(0)
        self.rect.set_height(0)
        self.rect.set_alpha(0.4)

        
    def on_end_select(self, event):
        self.in_selection = False
        self.rect.set_alpha(0.0)
        self.get_selected_indexes()
        
    def get_selected_indexes(self):
        """Get the embedding points that fall in the current selection rectangle"""
        embedding = self.analysis.embedding
        # Get the ordered indexes at this analysis level 0 - n-1
        indexes = np.arange(embedding.shape[0])
        selected_indexes = indexes[(embedding[:,0] > self.rorg_xy[0]) & (embedding[:,0] < self.rorg_xy[0] + self.dim_xy[0]) 
            & (embedding[:,1] > self.rorg_xy[1]) & (embedding[:,1] < self.rorg_xy[1] + self.dim_xy[1])]
        print(selected_indexes)
        if selected_indexes.shape[0] > 0:
        # Call back the ananlysis model to create a new analysis
            self.make_new_analysis(self.analysis, selected_indexes)
            
    def get_figure_as_buffer(self):     
        """Return the figure as a png image in a buffer"""
        # Force a redraw by resizing the figure
        fig_size = plt.gcf().get_size_inches()
        plt.gcf().set_size_inches(1.0 * fig_size)
        buf = io.BytesIO()
        extent = self.ax.get_tightbbox(self.fig.canvas.get_renderer()).transformed(self.fig.dpi_scale_trans.inverted())
        
        self.fig.savefig(buf, bbox_inches=extent)
        return buf
        
    @property
    def iter_stopped(self):
        return self._stop_iter
    
    @property
    def iter_count(self):
        return self._iter_count
        
    @property    
    def figure_id(self):
        return str(self.analysis)
        
    
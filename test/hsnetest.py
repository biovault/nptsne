import nptsne
import numpy as np 
from nptsne import hsne_analysis
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.gridspec import GridSpec
import matplotlib.cm as cm
import matplotlib.patches as patches

raw = np.fromfile('MNIST_1000.bin', np.float32)
X = np.reshape(raw, (1000, 784))
hsne = nptsne.HSne(True)
hsne.create_hsne(X, 2)
hsne.save('mnist_1000_hsne.bin')
analysis_model = hsne_analysis.AnalysisTree(hsne)
top_analysis = analysis_model.top_analysis
top_analysis.landmark_weights.shape
top_embedder = top_analysis.embedder
embedding = top_embedder.embedding 
print("embedding shape")
embedding.shape
print("original indexes shape")
top_analysis.landmark_orig_indexes.shape
x = embedding[:,0]
y = embedding[:,1]
fig = plt.figure()
# space for the plot and the digit display - spec is row,col
gs = GridSpec(4,4)
ax = fig.add_subplot(gs[:4,:3])
ix = fig.add_subplot(gs[0,3])
ix.set_xticks([])
ix.set_yticks([])

scatter = None
rect = None
default_rect = None
extent = 2.8
def start_plot():
    global scatter
    global rect
    ax.set(xlim=(-extent, extent), ylim=(-extent, extent))
    scatter = ax.scatter(x,y,s=top_analysis.landmark_weights * 8, c='b', alpha=0.4, picker=1)
    rt = patches.Rectangle((-extent,-extent),0.1,0.1,linewidth=0.5,edgecolor='r',facecolor='none', alpha=0)
    rect = ax.add_patch(rt)
    default_rect = rect
    return scatter, rect, 

# if matplot lib rendering is slow do a number of iterations per frame
num_frames = 350
iters_per_frame = 1
stop_anim = False
dummydata = np.zeros((28,28), dtype=np.float32)
composite_digit = np.zeros((784,))
digit_im = ix.imshow(dummydata, interpolation='bilinear', cmap='gray', vmin=0, vmax=255)

def quit():
    plt.close()

def stop_loop(event):
    fig.canvas.stop_event_loop()    
    
def iterate_tSNE(i):
    global stop_anim
    if not stop_anim: 
        for j in range(iters_per_frame):
            top_embedder.do_iteration()
        if i == num_frames - 1:
            stop_anim = True
    
    # can auto scale the axes
    # min = np.amin(embedding, axis=0)
    # max = np.amax(embedding, axis=0)
    # ax.set(xlim=(min[0], max[0]), ylim=(min[1], max[1]))
    scatter.set_offsets(embedding)
    digit = np.reshape(composite_digit, (28,28))
    digit_im.set_array(digit)
    # print("Digit data", digit)
    #ix.imshow(digit, interpolation='bilinear', cmap='gray', vmin=0, vmax=255)
    #plt.draw()
    return [scatter, rect, digit_im, ]
    
# Brush support values    
in_selection = False
rect_xy = (None, None)  # start of selection rectangle
dim_xy = (None, None)  # displacement
rorg_xy = (None, None)  # The bottom left corner

def on_over(event): 
    global composite_digit
    global dim_xy
    global rorg_xy
    global rect_xy
    if not in_selection: 
        cont, index = scatter.contains(event)
        if cont:
            # print("Landmark index(es): ", index['ind'])
            composite_digit = np.zeros((784,))
            for i in index['ind']:
                digit_idx = top_analysis.landmark_orig_indexes[i] 
                composite_digit = np.add(composite_digit, X[digit_idx,:])
            composite_digit = composite_digit/len(index['ind']) 
    else:
        if not event.inaxes == scatter.axes: return
        width = abs(event.xdata - rect_xy[0])
        height = abs(event.ydata - rect_xy[1])
        org_x = min(rorg_xy[0], event.xdata)
        org_y = min(rorg_xy[1], event.ydata)
        rorg_xy = (org_x, org_y)
        rect.set_xy(rorg_xy)
        dim_xy = (width, height)
        rect.set_width(width)
        rect.set_height(height)
        rect.set_alpha(0.4)
        

def on_keypress(event):
    if event.key in ['q', 'Q', 'escape']:
        quit()



def on_start_select(event):
    global in_selection
    global rect_xy
    global rorg_xy
    in_selection = True
    if not event.inaxes == scatter.axes: return
    rect_xy = (event.xdata, event.ydata)
    rorg_xy = rect_xy
    print(rect_xy)

    
def on_end_select(event):
    global in_selection
    in_selection = False
    rect.set_alpha(0.0)
    get_selected_indexes()
    
def get_selected_indexes():
    """Get the embedding points that fall in the current selection rectangle"""
    indexes = np.arange(embedding.shape[0])
    selected_indexes = indexes[(embedding[:,0] > rorg_xy[0]) & (embedding[:,0] < rorg_xy[0] + dim_xy[0]) 
        & (embedding[:,1] > rorg_xy[1]) & (embedding[:,1] < rorg_xy[1] + dim_xy[1])]
    print(selected_indexes)
       
    
    
#start_plot()
ani = animation.FuncAnimation(fig, iterate_tSNE, init_func=start_plot, frames=range(num_frames), interval=0.5, repeat=True, blit=True)
fig.canvas.mpl_connect('motion_notify_event', on_over)
fig.canvas.mpl_connect('key_press_event', on_keypress)
fig.canvas.mpl_connect('close_event', stop_loop)
fig.canvas.mpl_connect('button_press_event', on_start_select)
fig.canvas.mpl_connect('button_release_event', on_end_select)

plt.show(block=False)
fig.canvas.start_event_loop(timeout=-1)

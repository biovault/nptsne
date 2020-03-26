import nptsne
import numpy as np 
from nptsne import hsne_analysis
import matplotlib.pyplot as plt
from matplotlib import animation

raw = np.fromfile('MNIST_1000.bin', np.float32)
X = np.reshape(raw, (1000, 784))
hsne = nptsne.HSne(True)
hsne.create_hsne(X, 2)
hsne.save('mnist_1000_hsne.bin')
analysis_model = hsne_analysis.AnalysisTree(hsne)
top_analysis = analysis_model.top_analysis
top_embedder = top_analysis.embedder
embedding = top_embedder.embedding 
embedding.shape
x = embedding[:,0]
y = embedding[:,1]
fig, ax = plt.subplots()

scatter = None
def start_plot():
    global scatter
    extent = 2.8
    ax.set(xlim=(-extent, extent), ylim=(-extent, extent))
    scatter = ax.scatter(x,y)
    return scatter,

# if matplot lib rendering is slow do a number of iterations per frame
num_frames = 350
iters_per_frame = 1

def iterate_tSNE(i):
    for j in range(iters_per_frame):
        top_embedder.do_iteration()
    # can auto scale the axes
    # min = np.amin(embedding, axis=0)
    # max = np.amax(embedding, axis=0)
    # ax.set(xlim=(min[0], max[0]), ylim=(min[1], max[1]))
    scatter.set_offsets(embedding)
    return scatter,

stop_anim = False
ani = animation.FuncAnimation(fig, iterate_tSNE, init_func=start_plot, frames=range(num_frames), interval=0.5, repeat=False, blit=True)
plt.show(block=False)

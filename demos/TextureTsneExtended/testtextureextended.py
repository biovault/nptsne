import os
import nptsne
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib import rc
import numpy as np

from six.moves import urllib
from scipy.io import loadmat
from matplotlib import colors as mcolors
from timeit import default_timer as timer

root = Path(__file__).resolve().parent.parent
mnist_raw = loadmat(root / 'data' / 'mnist-original.mat')
mnist = {
    'data': mnist_raw['data'].T,
    'target': mnist_raw['label'][0],
    'COL_NAMES': ['label', 'data']
}

colors = ['#EE3333', '#FF9900', '#FFEE00', '#AACC11', '#44AA77', '#0099EE', '#0066BB', '#443388', '#992288', '#EE0077']
# norm = mcolors.Normalize(vmin=0, vmax=9)

# mcolors.ListedColormap(colors)
rc('lines', linewidth=2)
rc('lines', markersize=1)

tsne = nptsne.TextureTsneExtended(False)
embeddings = []
if tsne.init_transform(mnist['data']):
    print('Init succeeded')

step_size = 100
for i in range(20):
    plt.figure(i + 1)
    start = timer()
    stop_exaggeration = False
    # reduce the forces from iteration 1000 
    if i == 10:
        tsne.start_exaggeration_decay()
        print(f'exaggeration stopping at {tsne.decay_started_at}')
    embedding = tsne.run_transform(verbose=True, iterations=100)
    end = timer()
    print(f'got embedding in {end - start}')
    print(f'iteration count {tsne.iteration_count}')
    xyembed = np.copy(embedding.reshape((70000, 2)))
    #embeddings.append(xyembed)
    print(f"subplot {i+1}")
    #plt.subplot(3,4,i+1)
    # plt.gca().set_title('Iter: ' + str(100*(i+1)))
    cmap=mcolors.ListedColormap(colors)
    plt.scatter(xyembed[..., 0], xyembed[..., 1], c=mnist['target'], cmap=mcolors.ListedColormap(colors), facecolors='None', marker='o')
    labels = np.arange(0, 10)
    loc = labels
    cb = plt.colorbar(cmap=cmap, boundaries=np.linspace(-0.5, 9.5 ,11))
    cb.set_ticks(loc)
    cb.set_ticklabels(labels)    
    plt.draw()
    plt.savefig(f'testext_{i:02}.png')

tsne.close() 

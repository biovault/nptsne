import os
import nptsne
import matplotlib.pyplot as plt
from matplotlib import rc
import numpy as np

from six.moves import urllib
from scipy.io import loadmat
from matplotlib import colors as mcolors
from timeit import default_timer as timer

mnist_path = 'mnist-original.mat'
if not os.path.isfile(mnist_path):
    mnist_alternative_url = 'https://github.com/amplab/datascience-sp14/raw/master/lab7/mldata/mnist-original.mat'
    response = urllib.request.urlopen(mnist_alternative_url)
    with open(mnist_path, 'wb') as f:
        content = response.read()
        f.write(content)
mnist_raw = loadmat(mnist_path)
mnist = {
    'data': mnist_raw['data'].T,
    'target': mnist_raw['label'][0],
    'COL_NAMES': ['label', 'data']
}

colors = ['#FF0000', '#FF9900', '#CCFF00', '#33FF00', '#00FF66', '#00FFFF', '#0066FF', '#3300FF', '#CC00FF', '#FF0099']
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
    plt.scatter(xyembed[..., 0], xyembed[..., 1], c=mnist['target'], cmap=mcolors.ListedColormap(colors), facecolors='None', marker='o')
    plt.draw()
    plt.savefig(f'testext_{i:02}.png')

tsne.close() 

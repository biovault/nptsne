import os
import nptsne
import matplotlib.pyplot as plt
from matplotlib import rc

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

tsne = nptsne.TextureTsne(False)
embedding = None
try:
    # followin
    for i in range(1):
        start = timer()
        embedding = tsne.fit_transform(mnist['data'])
        end = timer()
        print(f'got embedding in {end - start}')
except Exception as ex:
    print('Error....')
    print(ex)

colors = ['#FF0000', '#FF9900', '#CCFF00', '#33FF00', '#00FF66', '#00FFFF', '#0066FF', '#3300FF', '#CC00FF', '#FF0099']
# norm = mcolors.Normalize(vmin=0, vmax=9)
xyembed = embedding.reshape((70000, 2))
# mcolors.ListedColormap(colors)
rc('lines', linewidth=2)
rc('lines', markersize=1)
plt.scatter(xyembed[..., 0], xyembed[..., 1], c=mnist['target'], cmap=mcolors.ListedColormap(colors), facecolors='None', marker='o')
plt.show()

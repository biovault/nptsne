import os
import nptsne
import matplotlib.pyplot as plt
from matplotlib import rc
import numpy as np
import umap

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
    'label': mnist_raw['label'].T,
    'COL_NAMES': ['label', 'data']
}

colors = ['#FF0000', '#FF9900', '#CCFF00', '#33FF00', '#00FF66', '#00FFFF', '#0066FF', '#3300FF', '#CC00FF', '#FF0099']

rc('lines', linewidth=2)
rc('lines', markersize=1)

# extract 1 data point in 10  : p=[.1, .9]
# generate and index array with approximately 1/10 of data row numbers
idx = np.where(np.random.choice([1, 0], size=70000, p=[.1, .9]))
subLabel = np.squeeze(mnist['label'][idx])
subData =  mnist['data'][idx]

print(subLabel.shape, subData.shape)

umap_embed = umap.UMAP().fit_transform(subData)

print(umap_embed.shape)
plt.figure(40)
print(subLabel)
print(umap_embed)
plt.scatter(umap_embed[..., 0], umap_embed[..., 1], c=subLabel, cmap=mcolors.ListedColormap(colors), facecolors='None', marker='o')
plt.draw()
plt.savefig(f'testexum_00.png')
    
tsne = nptsne.TextureTsneExtended(verbose=True)

print(f'Init tSNE from umap, shape: {umap_embed.shape}')
if tsne.init_transform(subData, umap_embed):
    print('Init from umap succeeded')

step_size = 100
for i in range(20):
    plt.figure(i + 1)
    start = timer()
    exaggeration_iter = 100
    # reduce the forces from 1000 
    if i == 10:
        tsne.start_exaggeration_decay()
        print(f'exaggeration stopping at {tsne.decay_started_at}')

    embedding = tsne.run_transform(verbose=True, iterations=100)
    end = timer()
    print(f'got embedding in {end - start}')
    xyembed = np.copy(embedding.reshape((-1, 2)))
    #plt.subplot(3,4,i+1)
    # plt.gca().set_title('Iter: ' + str(100*(i+1)))
    plt.scatter(xyembed[..., 0], xyembed[..., 1], c=subLabel, cmap=mcolors.ListedColormap(colors), facecolors='None', marker='o')
    plt.draw()
    plt.savefig(f'testexum_{1+i:02}.png')

tsne.close()  



        



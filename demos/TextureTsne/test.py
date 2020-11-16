#!/usr/bin/env python
"""Create a t-SNE embedding using GPU accelerated t-SNE in the nptsne package"""
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors as mcolors
from scipy.io import loadmat
import nptsne

root = Path(__file__).resolve().parent.parent
mnist_raw = loadmat(root / 'data' / 'mnist-original.mat')
mnist = {
    'data': mnist_raw['data'].T,
    'target': mnist_raw['label'][0],
    'COL_NAMES': ['label', 'data']
}

colors = ['#EE3333', '#FF9900', '#FFEE00', '#AACC11', '#44AA77',
    '#0099EE', '#0066BB', '#443388', '#992288', '#EE0077']

tsne = nptsne.TextureTsne(True)  # True triggers verbose output
embed = tsne.fit_transform(mnist['data'])
print(embed.shape)
embed = embed.reshape(70000,2)
cmap=mcolors.ListedColormap(colors)
# norm = mcolors.BoundaryNorm(0, 9)

sc = plt.scatter(embed[...,0], embed[...,1], s = 1, c=mnist['target'],
    vmin=0, vmax=9, cmap=cmap, facecolors='None', marker='o')
labels = np.arange(0, 10)
loc = labels
cb = plt.colorbar(sc, boundaries=np.linspace(-0.5, 9.5 ,11))
cb.set_ticks(loc)
cb.set_ticklabels(labels)
plt.show()

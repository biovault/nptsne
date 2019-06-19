#!/usr/bin/env python
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import loadmat
mnist = loadmat('mnist-original.mat')
mnist['data'].shape
import nptsne
tsne = nptsne.TextureTsne(True)
embed = tsne.fit_transform(mnist['data'].T)
print(embed.shape)
embed = embed.reshape(70000,2)
plt.scatter(embed[...,0], embed[...,1], s = 1, c=mnist['label'][0], cmap=plt.cm.get_cmap("Paired", 10))
plt.colorbar(ticks=range(10))
plt.show()


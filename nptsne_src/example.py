import numpy as np
import nptsne
import matplotlib.pyplot as plt

inarray = np.fromfile('MNIST_1000.bin', np.float32)
mnist_arr = inarray.reshape(1000,784)

tsne = nptsne.TextureTsne(True)
	
embedding = tsne.fit_transform(mnist_arr)

xyembed = embedding.reshape((1000,2))
plt.scatter(xyembed[...,0], xyembed[...,1])
plt.show()

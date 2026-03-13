import numpy as np
import nptsne

from scipy.spatial.distance import pdist, squareform
import matplotlib.pyplot as plt
from matplotlib import colors as mcolors

mnist = np.load(r"D:\Projects\nptsne\demos\data\MNIST_70000.npy")
labels = np.load(r"D:\Projects\nptsne\demos\data\MNIST_70000_label.npy")
subset_size = 10000
indexes = np.random.choice(np.arange(69999), subset_size, replace=False)
mnist = mnist[indexes, ...]
labels = labels[indexes]
dist_matrix = squareform(pdist(mnist, metric="sqeuclidean"))

tsne = nptsne.TextureTsneExtended(verbose=True)
tsne.init_transform_with_distance_matrix(dist_matrix)
tsne.run_transform(iterations=250)
tsne.start_exaggeration_decay()
embedding = tsne.run_transform(iterations=750)

xyembed = np.copy(embedding.reshape((subset_size, 2)))
colors = [
    "#EE3333",
    "#FF9900",
    "#FFEE00",
    "#AACC11",
    "#44AA77",
    "#0099EE",
    "#0066BB",
    "#443388",
    "#992288",
    "#EE0077",
]

sc = plt.scatter(
    xyembed[..., 0], xyembed[..., 1], marker="o", cmap=mcolors.ListedColormap(colors), c=labels
)
plt.show()
tsne.close()

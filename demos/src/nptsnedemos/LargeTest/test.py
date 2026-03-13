from data_sources import get_mouse_Zheng, get_MNIST
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import nptsne
from nptsne import KnnAlgorithm
from matplotlib import colors as mcolors
import math
import numpy as np

num_points = 1306127  # all in Zheng 1306127
X, y, colors, unique_colors = get_mouse_Zheng(num_points=num_points)
# X, y, colors, unique_colors = get_MNIST(num_points=num_points)
print(f"data shape {X.shape}")

tsne = nptsne.TextureTsne(True, perplexity=50, knn_algorithm=KnnAlgorithm.Annoy)
embed = tsne.fit_transform(X)
embed = embed.reshape(num_points, 2)
kl_values = tsne.kl_values
cmap = mcolors.ListedColormap(colors)

plt.figure(1)
plt.tight_layout()
sc = plt.scatter(
    embed[..., 0],
    embed[..., 1],
    s=40 / math.log10(num_points),
    c=colors,
    vmin=0,
    vmax=9,
    cmap=cmap,
    marker="o",
)
labels = np.arange(0, 10)
loc = labels
cb = plt.colorbar(sc, boundaries=np.linspace(-0.5, 9.5, 11))
cb.set_ticks(loc)
cb.set_ticklabels(labels)
plt.figure(2)
plt.plot(range(0, kl_values.shape[0]), kl_values)
plt.show()

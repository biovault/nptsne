from pathlib import Path
import numpy as np
import nptsne
from scipy.io import loadmat
from scipy.spatial.distance import pdist, squareform
import matplotlib.pyplot as plt
from matplotlib import colors as mcolors


def main():

    root = Path(__file__).resolve().parent.parent
    mnist_raw = loadmat(root / "data" / "mnist-original.mat")

    mnist_dict = {
        "data": mnist_raw["data"].T,
        "target": mnist_raw["label"][0],
        "COL_NAMES": ["label", "data"],
    }

    mnist = mnist_dict["data"]
    labels = mnist_dict["target"]
    subset_size = 10000
    print(f"Calculate a euclidean distance matrix for {subset_size} MNIST data points")
    indexes = np.random.choice(np.arange(69999), subset_size, replace=False)
    mnist = mnist[indexes, ...]
    labels = labels[indexes]
    dist_matrix = squareform(pdist(mnist, metric="sqeuclidean"))

    tsne = nptsne.TextureTsneExtended(verbose=True)
    print(f"Initialize tSNE with the distance matrix")
    tsne.init_transform_with_distance_matrix(dist_matrix)
    print(f"Start the embedding tSNE")
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


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent
    print(f"The rootdir is {root}")
    main()

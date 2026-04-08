from .data_sources import get_mouse_Zheng, get_MNIST
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import nptsne
from nptsne import GpgpuSneType
from nptsne import KnnAlgorithm
from matplotlib import colors as mcolors
import math
import numpy as np
import sys

def main():
  num_points = 1306127  # all in Zheng 1306127
  X, y, colors, unique_colors = get_mouse_Zheng(num_points=num_points)
  # X, y, colors, unique_colors = get_MNIST(num_points=num_points)
  print(f"data shape {X.shape}")
  print(f"Run tSNE on {num_points} points")
  tsne_type = GpgpuSneType.AutoDetect
  if len(sys.argv) > 1:
    typestr = str.upper(sys.argv[1]) 
    if typestr == "COMPUTE":
      tsne_type = GpgpuSneType.ComputeShader
    if typestr == "VULKAN":
      tsne_type = GpgpuSneType.ComputeShaderVulkan
    if typestr == "RASTER":
      tsne_type = GpgpuSneType.Raster

  tsne = nptsne.TextureTsne(True, perplexity=50, knn_algorithm=KnnAlgorithm.Annoy, gpgpu_sne_type=tsne_type)
  embed = tsne.fit_transform(X)
  embed = embed.reshape(num_points, 2)
  kl_values = tsne.kl_values
  cmap = mcolors.ListedColormap(colors)

  subset_size = 100000
  print(f"Plotting a {subset_size} point subset of the embedding")
  indexes = np.random.choice(np.arange(num_points-1), subset_size, replace=False)

  print(f"colors applied {np.array(colors)[indexes[0:50]]}")

  plt.figure(1)
  plt.tight_layout()
  sc = plt.scatter(
      embed[indexes, 0],
      embed[indexes, 1],
      s=40 / math.log10(num_points),
      c=np.array(colors)[indexes],
      marker="o",
  )
  labels = np.arange(0, 10)
  loc = labels
  plt.figure(2)
  plt.plot(range(0, kl_values.shape[0]), kl_values)
  plt.show()

if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    print(f"The rootdir is {root}")
    main()
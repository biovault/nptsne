#!/usr/bin/env python
"""Create a t-SNE embedding using GPU accelerated t-SNE in the nptsne package"""
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors as mcolors
from scipy.io import loadmat
import nptsne
from nptsne import GpgpuSneType
import math
import sys

def main():
  root = Path(__file__).resolve().parent.parent
  mnist_raw = loadmat(root / "data" / "mnist-original.mat")
  mnist = {
      "data": mnist_raw["data"].T,
      "target": mnist_raw["label"][0],
      "COL_NAMES": ["label", "data"],
  }

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

  tsne_type = GpgpuSneType.AutoDetect
  if len(sys.argv) > 1:
    typestr = str.upper(sys.argv[1]) 
    if typestr == "COMPUTE":
      tsne_type = GpgpuSneType.ComputeShader
    if typestr == "VULKAN":
      tsne_type = GpgpuSneType.ComputeShaderVulkan
    if typestr == "RASTER":
      tsne_type = GpgpuSneType.Raster
  # True triggers verbose output
  tsne = nptsne.TextureTsne(True, gpgpu_sne_type=tsne_type)  
  embed = tsne.fit_transform(mnist["data"])
  print(embed.shape)
  num_points = 70000
  embed = embed.reshape(num_points, 2)
  kl_values = tsne.kl_values
  cmap = mcolors.ListedColormap(colors)
  # norm = mcolors.BoundaryNorm(0, 9)

  plt.figure(1)
  plt.tight_layout()
  sc = plt.scatter(
      embed[..., 0],
      embed[..., 1],
      s=40 / math.log10(num_points),
      c=mnist["target"],
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

if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    print(f"The rootdir is {root}")
    main()
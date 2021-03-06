"""demonstrate that the HSNE transition matrix can be used for Louvain clustering"""
from pathlib import Path
import nptsne
import numpy as np
import community as community_louvain
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.lines import Line2D

matplotlib.use("Qt5Agg")

# Data is in the demo/data directory
dataroot = Path(__file__).resolve().parent.parent / 'data'

X = np.load(dataroot / 'MNIST_70000.npy')
lab = np.load(dataroot / 'MNIST_70000_label.npy')
print(f'Size data: {X.shape}')
hsne = nptsne.HSne(True)
# Create a 3 scale HSNE analysis from the MNIST data
hsne.create_hsne(X, 3)
print(f'Num scales: {hsne.num_scales} Num points {hsne.num_data_points}')
scale2 = hsne.get_scale(2)
print(f'Num points in scale 2 {scale2.num_points}')
tmatrix = scale2.transition_matrix

row = []
col = []
data = []

for r_ind, rcol in enumerate(tmatrix):
    for tup in rcol:
        if not isinstance(tup, tuple):
            continue
        row.append(r_ind)
        col.append(tup[0])
        data.append(tup[1])

def make_nxgraph_from_sparse_data(drow, dcol, weights):
    """Get igraph graph from row cols indexes and weights
    Code is adapted from scanpy utils"""

    g = nx.Graph()
    g.add_weighted_edges_from(list(zip(drow, dcol, weights)))
    return g

graph = make_nxgraph_from_sparse_data(row, col, data)

# sparse = coo_matrix((data, (row, col)), shape = (len(tmatrix), len(tmatrix)))

markers = [r'$\alpha$', r'$\beta$', r'$\gamma$', r'$\delta$', r'$\epsilon$', \
            r'$\zeta$', r'$\eta$', r'$\theta$', r'$\iota$', r'$\kappa$', \
            r'$\lambda$', r'$\mu$', r'$\nu$', r'$\xi$', \
            r'$\omicron$', r'$\pi$', r'\$\rho$', r'$\sigma$', \
            r'$\tau$', r'$\upsilon$', r'$\phi$', r'$\chi$', \
            r'$\psi$', r'$\omega$']


print('Apply Louvain partitioning')
partition = community_louvain.best_partition(graph, resolution=0.7)

print('Calculate network spring layout, this may take some time...')
pos = nx.spring_layout(graph)
cmap = matplotlib.cm.get_cmap('rainbow_r')
legend_coms = []
com_label =[]

print('Plotting figure')
fig = plt.figure()
ax = fig.add_subplot(1,1,1)

for com in set(partition.values()) :
    list_nodes = [nodes for nodes in partition.keys()
                                if partition[nodes] == com]
    ids =  scale2.landmark_orig_indexes[list_nodes]
    labs = lab[ids]
    # print(labs)
    edgecolors = [cmap(label/9.0) for label in labs]
    # print(edgecolors)
    legend_coms.append(markers[com])
    nx.draw_networkx_nodes(
        graph, pos, list_nodes, node_size = 70,
        edgecolors=edgecolors, linewidths=0.15,
        node_color=edgecolors,
        node_shape=markers[com],
        ax=ax)


nx.draw_networkx_edges(graph, pos, alpha=0.01, ax=ax)

legend_lines = []
bins = np.bincount(lab)
unique_lab = np.unique(lab).tolist()
for l in unique_lab:
    legend_lines.append(Line2D([0], [0], color=cmap(l/9.0)))

ax.legend(legend_lines, unique_lab, loc='lower right')
ax.set_title(f'Partition has {len(legend_coms)} Louvain communities: ' + ', '.join(legend_coms))
plt.tight_layout()
plt.show()

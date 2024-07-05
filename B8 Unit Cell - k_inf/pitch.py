import os
import torch
import torchvision
from torchvision.utils import make_grid
from wigner_3d import NODES
import numpy as np
from torchvision.transforms import Compose, ToTensor, Normalize
from scipy.spatial import Voronoi, voronoi_plot_2d, ConvexHull, Delaunay

def get_default_device():
    """Use GPU if available, else CPU"""
    if torch.cuda.is_available():
        return torch.device('cuda')
    else:
        return torch.device('cpu')

def to_device(data, device):
    """Move tensor(s) to chosen device"""
    if isinstance(data, (list,tuple)):
        return [to_device(x, device) for x in data]
    return data.to(device, non_blocking=True)

device = get_default_device()

def delaunayAdjacencyMatrix(nodes):
    """Computes an adjacency matrix of the delaunay graph with M[i][j] -> 1 if is_adjacent(n_i, n_j) else 0"""
    n = len(nodes)
    d = Delaunay(nodes)
    adjTensor = torch.zeros(n,n,device=device)
    for i in d.simplices:
        for j in range(len(i)-1):
            for k in range(j+1,len(i)):
                adjTensor[i[j]][i[k]] = 1.0
                adjTensor[i[k]][i[j]] = 1.0
    return adjTensor

def l2Matrix(nodes):
    """Computes a matrix of L2 norms with M[i][j] -> ||n_i - n_j||"""
    nodesTensor = to_device(torch.Tensor(nodes), device)
    nodesL2 = nodesTensor.expand(len(nodes),len(nodes),len(nodes[0]))
    nodesL2 = nodesL2 - nodesL2.transpose(0,1)
    nodesL2 = torch.linalg.norm(nodesL2, dim=2)
    return nodesL2


nodesL2 = l2Matrix(NODES)
adjMatrix = delaunayAdjacencyMatrix(NODES)
nodesL2 = adjMatrix*nodesL2
edges = torch.count_nonzero(nodesL2)
print(torch.sum(nodesL2)/edges) # takes the average adjacent L2 norm
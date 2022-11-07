"""
*************************************************************************************************************
*                                                                                                           *
*   GTex data visualizer developed by Ugo Lomoio at Magna Graecia University of Catanzaro                   *
*                                                                                                           *
*                                                                                                           *
*************************************************************************************************************
"""

import numpy as np 
from networkx.algorithms.centrality import degree_centrality as degree_centrality_nx
from networkx.algorithms.centrality import eigenvector_centrality as eigenvector_centrality_nx
from networkx.algorithms.centrality import closeness_centrality as closeness_centrality_nx
from networkx.algorithms.centrality import betweenness_centrality as betweenness_centrality_nx

from cdlib.algorithms import leiden as leiden_cdlib
from cdlib.algorithms import louvain as louvain_cdlib
from sklearn.cluster import SpectralClustering
from operator import itemgetter

def extract_labels_from_coms(coms):
    
    return {node: label for label, com in enumerate(coms) for node in com}

def community_louvain(G):
    """
    Implementation from the cdlib library for the community extraction Louvain algorithm.

    Parameters:
        G: networkx.graph, the graph (the PCN) you want to extract the communities
    Returns:
        labels: numpy.array, the extracted communities
    """
    coms = louvain_cdlib(G).communities
    labels = extract_labels_from_coms(coms)
    return labels

def community_leiden(G):
    """
    Implementation from the cdlib library for the community extraction Leiden algorithm.

    Parameters:
        G: networkx.graph, the graph (the PCN) you want to extract the communities
    Returns:
        labels: numpy.array, the extracted communities
    """
    coms = leiden_cdlib(G).communities
    labels = extract_labels_from_coms(coms)
    return labels


def spectral_clustering(A, node_names, n_clusters = 2):
    """
    Spectral clustering following the sci-kit learn implementation.
    Parameters:
        A: numpy.array, the adjacency matrix of the graph.
        node_names: list or array like, node names of the graph G obtained with list(G.nodes)
        n_clusters: int, default None. The number of clusters
    Returns:
        labels: np.array, extracted clusters
    """
    clustering = SpectralClustering(n_clusters=n_clusters, affinity='precomputed').fit(A)
    labels = {node_names[i]: cluster for i, cluster in enumerate(clustering.labels_)}
    return labels

def betweenness_centrality(G, n=10):
    """
    Compute the betweenness centrality of the nodes of the graph using the networkx implementation.
    Parameters:
        G: networkx.graph, the graph (the PCN) you want to compute the betweenness centrality.
        n: int, default equals to 10, number of best nodes with highest centrality to print.
    Returns:
        centralities: dict {node: P_coef[node]}, for each node is linked its betweenness centrality
    """
    bc = betweenness_centrality_nx(G)
  
    sorted_bc = sorted(bc.items(), key=itemgetter(1), reverse=True)
    print("Top {} nodes by betweenness centrality".format(n))
    for d in sorted_bc[:n]:
        print(d)

    return bc

def eigenvector_centrality(G, n=10):
    """
    Compute the eigenvector centrality of the nodes of the graph using the networkx implementation.
    Parameters:
        G: networkx.graph, the graph (the PCN) you want to compute the eigenvector centrality.
        n: int, default equals to 10, number of best nodes with highest centrality to print.
    Returns:
        centralities: dict {node: eigenvector_centrality[node]}, for each node is linked its eigenvector centrality
    """
    ec = eigenvector_centrality_nx(G, max_iter=10000)

    sorted_ec = sorted(ec.items(), key=itemgetter(1), reverse=True)
    print("Top {} nodes by eigenvector centrality".format(n))
    for d in sorted_ec[:n]:
        print(d)

    return ec

def degree_centrality(G, n=10):
    """
    Compute the degree centrality of the nodes of the graph using the networkx implementation.
    Parameters:
        G: networkx.graph, the graph (the PCN) you want to compute the degree centrality.
        n: int, default equals to 10, number of best nodes with highest centrality to print.
    Returns:
        centralities: dict {node: degree_centrality[node]}, for each node is linked its degree centrality
    """
    dc = degree_centrality_nx(G)

    sorted_dc = sorted(dc.items(), key=itemgetter(1), reverse=True)
    print("Top {} nodes by degree centrality".format(n))
    for d in sorted_dc[:n]:
        print(d)

    return dc

def closeness_centrality(G, n=10):
    """
    Compute the closeness centrality of the nodes of the graph using the networkx implementation.
    Parameters:
        G: networkx.graph, the graph (the PCN) you want to compute the closeness centrality.
        n: int, default equals to 10, number of best nodes with highest centrality to print.
    Returns:
        centralities: dict {node: closeness_centrality[node]}, for each node is linked its closeness centrality
    """
    cc = closeness_centrality_nx(G)

    sorted_cc = sorted(cc.items(), key=itemgetter(1), reverse=True)
    print("Top {} nodes by closeness_centrality".format(n))
    for d in sorted_cc[:n]:
        print(d)

    return cc


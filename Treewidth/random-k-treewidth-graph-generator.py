from sage.graphs.generators.basic import CompleteGraph
from sage.graphs.graph import Graph
import random

'''
k: Treewidth
vertices: Total number of vertices required
n: Number of edges to be deleted; default value is None
m: Number of edges to be contracted; default value is None
'''
def random_graph_with_treewidth_k(k, vertices, n=None, m=None):
    vertex_count = k+1
    base_graph = CompleteGraph(vertex_count)
    g = Graph(base_graph)
    i = vertices - vertex_count

    if vertices < vertex_count:
        raise ValueError("Number of vertices should be greater than the treewidth.")

    while i:
        selected_vertex = random.choice(g.vertices())
        adjacent_vertices = g.neighbors(selected_vertex)
        prev_vertices = random.sample(adjacent_vertices, k-1)
        prev_vertices.append(selected_vertex)
        new_vertex = vertex_count
        g.add_vertex(new_vertex)
        for v in prev_vertices:
            g.add_edge(v, new_vertex)
        prev_vertices.append(new_vertex)
        if g.is_clique(prev_vertices):
            vertex_count += 1
            i -= 1
        else:
            g.delete_vertex(new_vertex)

    if n is not None:
        delete_random_edges(g, n)

    if m is not None:
        contract_random_edges(g, m)

    return g

def delete_random_edges(g, n):
    edges = list(g.edges())
    edges_to_delete = random.sample(edges, min(n, len(edges)))
    for edge in edges_to_delete:
        g.delete_edge(edge)

def contract_random_edges(g, m):
    edges = list(g.edges())
    edges_to_contract = random.sample(edges, min(m, len(edges)))
    for edge in edges_to_contract:
        g.contract_edge(edge)

g = random_graph_with_treewidth_k(3, 4, None, None)
#show(g)

#from sage.graphs.graph_decompositions.tree_decomposition import treewidth
#ans = treewidth(g)
#print("Treewidth:", ans)

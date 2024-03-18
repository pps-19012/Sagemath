import time
from sage.graphs.graph_decompositions.vertex_separation import path_decomposition
from sage.graphs.graph import Graph

def generate_complete_binary_tree(levels):
    tree = Graph()
    total_nodes = 2**levels - 1
    for i in range(1, total_nodes + 1):
        tree.add_vertex(i)
    for i in range(1, total_nodes // 2 + 1):
        tree.add_edge(i, 2 * i)
        tree.add_edge(i, 2 * i + 1)
    return tree


levels = [10, 20, 40, 80, 160]
trees = [generate_complete_binary_tree(l) for l in levels]


print(f"{'Levels':<15}{'Time Elapsed (s)':<20}")

for i in range(len(levels)):
    l = levels[i]
    t = trees[i]
    start = time.time()
    ans = path_decomposition(t)
    end = time.time()
    elapsed = end - start
    print(f"{l:<15}{elapsed:<20.6f}")

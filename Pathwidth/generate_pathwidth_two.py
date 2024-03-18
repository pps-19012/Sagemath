from sage.graphs.generators.basic import CompleteGraph
k = 3
g = CompleteGraph(k)
vertices = 4
while k <= vertices-1:
    g.add_vertex(k)
    g.add_edge(k, k-1)
    g.add_edge(k, k-2)
    k += 1
#show(g)

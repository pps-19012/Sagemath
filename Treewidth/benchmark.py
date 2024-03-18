# Time taken to compute treewidth vs Time taken to find if atmost k
from sage.graphs.generators.basic import CompleteGraph
from sage.graphs.generators.basic import CycleGraph
from sage.graphs.generators.basic import StarGraph

func = {CompleteGraph : 'Complete Graph', CycleGraph : 'Cycle Graph', StarGraph : 'Star Graph'}
vert = [1, 10, 100, 1000, 10000]

print(f"{'Vertices':<10}{'Graph Type':<20}{'Time taken to compute treewidth':<35}{'Time taken to find if atmost k':<35}")

for f in func:
    for v in vert:
        g = CompleteGraph(100)
        # show(g)

        start = time.time()
        ans = treewidth(g)
        end = time.time()
        elapsed1 = end - start

        start = time.time()
        ans = treewidth(g, k = 3)
        end = time.time()
        elapsed2 = end - start
        
        print(f"{v:<10}{func[f]:<20}{elapsed1:<35.6f}{elapsed2:<30.6f}")
#         print(elapsed1, elapsed2)

v = 10
pg = 'Petersen Graph'
g = Graph(graphs.PetersenGraph())
# show(g)

start = time.time()
ans = treewidth(g)
end = time.time()
elapsed1 = end - start

start = time.time()
ans = treewidth(g, k = 2)
end = time.time()
elapsed2 = end - start

print(f"{v:<10}{pg:<20}{elapsed1:<35.6f}{elapsed2:<30.6f}")
# print(elapsed1, elapsed2)

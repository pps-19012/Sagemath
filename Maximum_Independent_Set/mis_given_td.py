from sage.graphs.graph_decompositions.tree_decomposition import *
from sage.graphs.generators.basic import CompleteGraph
import time
import itertools
import cProfile

def powerset(s):
    x = len(s)
    masks = [1 << i for i in range(x)]
    for i in range(1 << x):
        yield [ss for mask, ss in zip(masks, s) if i & mask]

def generate_graph_pathwidth_two(vertices):
    k = 3
    g = CompleteGraph(k)
    while k <= vertices-1:
        g.add_vertex(k)
        g.add_edge(k, k-1)
        g.add_edge(k, k-2)
        k += 1
    return g

def mis(g):
    start = time.time()
    td = g.treewidth(certificate=True)
    powersets = {}
    for v in td.vertices():
        powersets[v] = list(powerset(v))
    profiler = cProfile.Profile()
    profiler.enable()
    mis_set, mis_val = compute_mis(g, td, powersets, td_neighbors={v: list(td.neighbors(v)) for v in td.vertices()})
    profiler.disable()
    profiler.print_stats(sort='cumtime')
    
    end = time.time()
    print("TIME ELAPSED IN MIS NOT GIVEN TREE DECOMPOSITION:", end-start)
    return (mis_set, mis_val)

def compute_mis(g, td, powersets, td_neighbors):
    start = time.time()
    max_nei = 0
    for v in td.vertices():
        if len(td_neighbors[v]) > max_nei:
            max_nei = len(td_neighbors[v])
            root_node = v
            
    bags = {}
    q = [(root_node, 0)]
    visit = set()
    leaf_nodes = []
    while q:
        childPresent = False
        node, level = q.pop(0)
        visit.add(node)
        if level not in bags:
            bags[level] = []
        bags[level].append(node)
        for nei in td_neighbors[node]:
            if nei not in visit:
                childPresent = True
                q.append((nei, level+1))
        if not childPresent:
            leaf_nodes.append(node)

    bag_number = {}
    bn = 0
    for k, ver in bags.items():
        for v in ver:
            bag_number[v] = bn
            bn += 1

    number_to_bag = {}
    for k, v in bag_number.items():
        number_to_bag[v] = k

    # Initialize table A
    a_c = len(td.vertices())
    A = {None:{}}
    
    bags_processed_A = [False for _ in range(a_c)]
    for b in leaf_nodes:
        for v in b:
            if v not in A:
                A[v] = {}
            A[v][bag_number[b]] = {v}
        bags_processed_A[bag_number[b]] = True

    leaf_pairs = []
    q = [root_node]
    visit = set()
    while q:
        node = q.pop(0)
        visit.add(node)
        for nei in td_neighbors[node]:
            if nei not in visit:
                q.append(nei)
                if node in leaf_nodes or nei in leaf_nodes:
                    leaf_pairs.append((bag_number[nei], bag_number[node]))

    B = {None:{}}
    # Bottom of B
    for i, j in leaf_pairs:
        # Fill None
        B[None][(i,j)] = number_to_bag[i] - number_to_bag[j]
        
        # Fill Leaf Pairs
        inter = number_to_bag[i] & number_to_bag[j]
        for v in inter:
            if v not in B:
                B[v] = {}
            if v in (number_to_bag[i] & number_to_bag[j]):
                B[v][(i,j)] = {v}

    for i in range(len(bags_processed_A)-1, -1, -1):
        if bags_processed_A[i]:
            continue
            
        # Compute A(S, i)
        powerset_of_bag_node = powersets[number_to_bag[i]]
        for k in powerset_of_bag_node:
            tmp = set(k)
            for nei in td_neighbors[number_to_bag[i]]:
                j = bag_number[nei]
                if j < i:
                    continue
                common = set(k) & set(nei)
                if len(common) == 0:
                    if (j, i) in B[None]:
                        tmp = tmp | set(B[None][(j, i)])
                elif len(common) == 1:
                    v = list(common)[0]
                    if v in B and (j, i) in B[v]:
                        tmp = tmp | (B[v][(j, i)] - (common & set(number_to_bag[j])))
                else:
                    v = tuple(common)
                    if v in B and (j, i) in B[v]:
                        tmp = tmp | (B[v][(j, i)] - (common & set(number_to_bag[j])))
            if len(k) == 0:
                s = None
            elif len(k) == 1:
                s = k[0]
            else:
                s = tuple(k)    
                if s not in B:
                    continue
            if s not in A:
                A[s] = {}
            A[s][i] = tmp
            if len(tmp) == 1:
                temp = list(tmp)[0]
            elif len(tmp) > 1:
                temp = tuple(tmp)
            if temp not in A:
                A[temp] = {}
                A[temp][i] = tmp

        # Compute B(S, i, j)
        for nei in td_neighbors[number_to_bag[i]]:
            j = bag_number[nei]
            if j > i:
                continue

            for l in powersets[number_to_bag[i]]:
                if len(l) == 0:
                    s_prime = None
                elif len(l) == 1:
                    s_prime = l[0]
                else:
                    s_prime = tuple(l)
                k = set(l) & set(number_to_bag[j])
                if len(k) == 0:
                    s = None
                elif len(k) == 1:
                    s = list(k)[0]
                else:
                    s = tuple(k)
                if (s_prime not in A) or (i not in A[s_prime]):
                    continue
                    
                if s not in B:
                    B[s] = {}
                if (i, j) not in B[s]:
                    B[s][(i, j)] = A[s_prime][i]
                else:
                    if len(B[s][(i, j)]) <= len(A[s_prime][i]):
                        B[s][(i, j)] = A[s_prime][i]
                        
        bags_processed_A[i] = True
        
    mis_set = {}
    for v in A.keys():
        if 0 in A[v] and len(A[v][0]) > len(mis_set):
            mis_set = A[v][0]
    end = time.time()
    print("TIME ELAPSED IN MIS GIVEN TREE DECOMPOSITION:", end-start)
    return (mis_set, len(mis_set))


def main():
    g = generate_graph_pathwidth_two(1000)
    misSet = mis(g)
    print("MIS SET FROM CUSTOM IMPLEMENTATION:", misSet)
    
    start1 = time.time()
    misSet1 = g.independent_set()
    end1 = time.time()
    print("MIS SET FROM SAGE IMPLEMENTATION:", misSet1)
    print("TIME ELAPSED IN SAGE IMPLEMENTATION:", end1-start1)

main()

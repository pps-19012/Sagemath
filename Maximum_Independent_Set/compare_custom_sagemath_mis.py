from sage.graphs.graph_decompositions.tree_decomposition import *
from sage.graphs.generators.basic import CompleteGraph
from sage.graphs.independent_sets import IndependentSets
import time

def generate_graph_pathwidth_two(vertices):
    k = 3
    g = CompleteGraph(k)
    while k <= vertices-1:
        g.add_vertex(k)
        g.add_edge(k, k-1)
        g.add_edge(k, k-2)
        k += 1
    #show(g)
    return g

def custom_mis(g):
    start = time.time()
    td = g.treewidth(certificate=True)
    #show(td)
    mis_set, mis_val = compute_mis(g, td)
    #mis_set, mis_val = compute_mis2(g, td)
    end = time.time()
    print("TIME ELAPSDED IN CUSTOM_MIS:", end-start)
    return (mis_set, mis_val)

def compute_mis2(g, td):
    show(td)
    max_nei = 0
    for v in td.vertices():
        if len(td.neighbors(v)) > max_nei:
            max_nei = len(td.neighbors(v))
            root_node = v
    print("Root Node:", root_node)
    print("Neighbours of Root Node:", td.neighbors(root_node))

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
        for nei in td.neighbors(node):
            if nei not in visit:
                childPresent = True
                q.append((nei, level+1))
        if childPresent == False:
            leaf_nodes.append(node)

    print("Leaf Nodes:", leaf_nodes)
    
    bag_number = {}
    bn = 0
    for k, ver in bags.items():
        for v in ver:
            bag_number[v] = bn
            bn += 1

    number_to_bag = {}
    for k, v in bag_number.items():
        number_to_bag[v] = k
        
    return None, 0

def compute_mis(g, td):
    start = time.time()
    max_nei = 0
    for v in td.vertices():
        if len(td.neighbors(v)) > max_nei:
            max_nei = len(td.neighbors(v))
            root_node = v

    print("Root Node:", root_node)
    print("Neighbours of Root Node:", td.neighbors(root_node))

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
        for nei in td.neighbors(node):
            if nei not in visit:
                childPresent = True
                q.append((nei, level+1))
        if childPresent == False:
            leaf_nodes.append(node)

    print("Leaf Nodes:", leaf_nodes)


    # Define Table A
    a_r = len(g.vertices()) + 1
    a_c = len(td.vertices())
    A = {None:{}}

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
    for v in g.vertices():
        A[v] = {}
        
    bags_processed_A = [False for _ in range(a_c)]
    for b in leaf_nodes:
        for v in b:
            A[v][bag_number[b]] = {v}
        bags_processed_A[bag_number[b]] = True
    
    for k, v in A.items():
        print(k, ':', v)

    pairs = {}
    leaf_pairs = []
    q = [root_node]
    visit = set()
    b_set = set()
    while q:
        node = q.pop(0)
        visit.add(node)
        for nei in td.neighbors(node):
            if nei not in visit:
                pairs[(bag_number[nei], bag_number[node])] = [node & nei]
                q.append(nei)
                b_set.update(node&nei)
                if node in leaf_nodes or nei in leaf_nodes:
                    leaf_pairs.append((bag_number[nei], bag_number[node]))

    b_r = len(b_set) + 1
    b_c = len(pairs)
    B = {None:{}}
    for v in b_set:
        B[v] = {}
    # Bottom of B
    for i, j in leaf_pairs:
        # Fill None
        B[None][(i,j)] = number_to_bag[i] - number_to_bag[j]
        # Fill Leaf Pairs
        for ver in pairs[(i, j)]:
            for v in ver:
                B[v][(i,j)] = {v} & set(number_to_bag[i]) & set(number_to_bag[j])
    print('-------------------------------------------------------')
    for k, v in B.items():
        print(k, ':', v)
    for i in range(len(bags_processed_A)-1, -1, -1):
        if bags_processed_A[i]:
            continue
            
        # Compute A
        new_A = list(number_to_bag[i]) + [None]
        for v in new_A:
            if v == None:
                tmp = set()
                for nei in td.neighbors(number_to_bag[i]):
                    j = bag_number[nei]
                    key = (max(i, j), min(i, j))
                    if key in B[None]:
                        tmp = tmp | (set(B[None][key]))
                A[None][i] = tmp
            elif v in b_set:
                tmp = {v}
                for nei in td.neighbors(number_to_bag[i]):
                    j = bag_number[nei]
                    if j < i:
                        continue
                    key = (j, i)
                    if (v in B) and (key in B[v]):
                        tmp = tmp | (set(B[v][key]) - ({v} & set(number_to_bag[j])))
                    elif key in B[None]:
                        tmp = tmp | (set(B[None][key]))
                    A[v][i] = tmp
                    #if tuple(tmp) not in A.keys():
                    #    A[tuple(tmp)] = {}
                    #    A[tuple(tmp)][i] = tmp
        
        print('------------------------------------------------------------')
        print(bags_processed_A)
        for k, v in A.items():
            print(k, ':', v)
        #Compute B
        for nei in td.neighbors(number_to_bag[i]):
            j = bag_number[nei]
            if j > i:
                continue
            for v in (number_to_bag[i] & number_to_bag[j]):
                common = {v} & set(number_to_bag[i]) & set(number_to_bag[j])
                max_val = 0
                max_set = {}
                for ver in common:
                    if ver not in A:
                        continue
                    s = A[ver][i]
                    if len(s) > max_val:
                        max_set = s
                        max_val = len(s)
                B[v][(i, j)] = max_set
            B[None][(i, j)] = A[None][i]
        bags_processed_A[i] = True
        for k, v in B.items():
            print(k, ':', v)

    mis_set = {}
    for v in A.keys():
        if 0 in A[v]:
            if len(A[v][0]) > len(mis_set):
                mis_set = A[v][0]
    
    #for v in g.vertices():
    #    if v not in A:
    #        mis_set = mis_set | {v}
            
    end = time.time()
    print("TIME ELAPSDED IN COMPUTE_MIS:", end-start)
    return (mis_set, len(mis_set))

def main():
    g = generate_graph_pathwidth_two(10)
    #start = time.time()
    Im = IndependentSets(g, maximal=True)
    #end = time.time()
    #print("TIME ELAPSED IN SAGEMATH FUNCTION:", end-start)
    maxLen = 0
    maxSet = set()
    for s in list(Im):
        if len(s) > maxLen:
            maxSet = s
            maxLen = len(s)
    misSet = custom_mis(g)
    print("MIS SET FROM SAGEMATH FUNCTION:", maxSet)
    print("MIS SET FROM CUSTOM IMPLEMENTATION:", misSet)

main()

from sage.graphs.graph_decompositions.tree_decomposition import *
from sage.graphs.generators.basic import CompleteGraph
from sage.graphs.independent_sets import IndependentSets
import time
import itertools

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
    #show(g)
    return g

def custom_mis(g):
    start = time.time()
    td = g.treewidth(certificate=True)
    #show(td)
    mis_set, mis_val = compute_mis2(g, td)
    end = time.time()
    print("TIME ELAPSDED IN CUSTOM_MIS:", end-start)
    return (mis_set, mis_val)

def compute_mis2(g, td):
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
        
    print('--------------------------------INITIALIZE A-----------------------')
    for k, v in A.items():
        print(k, ':', v)
        
    leaf_pairs = []
    q = [root_node]
    visit = set()
    while q:
        node = q.pop(0)
        visit.add(node)
        for nei in td.neighbors(node):
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
            B[v][(i,j)] = {v} & set(number_to_bag[i]) & set(number_to_bag[j])
    print('--------------------------------INITIALIZE B-----------------------')
    for k, v in B.items():
        print(k, ':', v)
        
    for i in range(len(bags_processed_A)-1, -1, -1):
        if bags_processed_A[i]:
            continue
        
        powerset_of_bag_node = list(powerset(number_to_bag[i]))
        # Compute A(S, i)
        for k in powerset_of_bag_node:
            #print("K:", k)
            tmp = set(k)
            for nei in td.neighbors(number_to_bag[i]):
                j = bag_number[nei]
                if j < i:
                    continue
                common = list(set(k) & set(nei))
                #print("Common:", common)
                if len(common) == 0:
                    if (j, i) in B[None]:
                        tmp = tmp | set(B[None][(j, i)])
                elif len(common) == 1:
                    v = common[0]
                    if v in B and (j, i) in B[v]:
                        tmp = tmp | (set(B[v][(j, i)]) - (set(common) & set(number_to_bag[j])))
                else:
                    v = tuple(common)
                    if v in B and (j, i) in B[v]:
                        tmp = tmp | (set(B[v][(j, i)]) - (set(common) & set(number_to_bag[j])))
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
                temp = tuple(list(tmp))
            if temp not in A:
                A[temp] = {}
                A[temp][i] = tmp
               
        print('----------------COMPUTE A---------BAG NUMBER:',i,'-------------------')
        print(bags_processed_A)
        for k, v in A.items():
            print(k, ':', v)
            
        for nei in td.neighbors(number_to_bag[i]):
            j = bag_number[nei]
            if j < i:
                continue
            
            powerset_of_bag_edge = list(powerset(number_to_bag[i] & number_to_bag[j]))
            for l in powerset_of_bag_edge:
                if len(l) == 0:
                    s = None
                elif len(l) == 1:
                    s = l[0]
                else:
                    s = tuple(l)
                max_val = 0
                max_set = {}
                for k in list(powerset(number_to_bag[j])):
                    if len(k) == 0:
                        s_prime = None
                    elif len(k) == 1:
                        s_prime = k[0]
                    else:
                        s_prime = tuple(k)
                    if (s_prime not in A) or (j not in A[s_prime]):
                        continue
                    ms = A[s_prime][j]
                    if len(ms) > max_val:
                        max_set = ms
                        max_val = len(ms)
                if s not in B:
                    B[s] = {}
                B[s][(j, i)] = max_set
                if len(max_set) == 1:
                    new = list(max_set)[0]
                elif len(max_set) > 1:
                    new = tuple(list(max_set))
                if new not in B:
                    B[new] = {}
                    B[new][(j, i)] = tuple(list(max_set))
        print('----------------COMPUTE B---------BAG NUMBER:',i,'-------------------')
        for k, v in B.items():
            print(k, ':', v)

        bags_processed_A[i] = True

    return None, 0


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

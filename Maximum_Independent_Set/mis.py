from sage.graphs.graph_decompositions.tree_decomposition import *
from sage.graphs.graph import Graph

def generate_random_graph(num_vertices, edge_probability):
    g = Graph()
    g.add_vertices(range(num_vertices))
    
    for v in range(num_vertices):
        for u in range(v+1, num_vertices):
            if random() < edge_probability:
                g.add_edge(v, u)
    
    return g

#random_graph = generate_random_graph(10, 0.3)
#g = random_graph

#CUSTOM GRAPH
g = Graph()
g.add_vertices({0, 1, 2, 3, 4, 5, 6, 7})
g.add_edge(0, 1)
g.add_edge(0, 2)
g.add_edge(1, 2)
g.add_edge(1, 4)
g.add_edge(1, 5)
g.add_edge(1, 6)
g.add_edge(2, 3)
g.add_edge(2, 4)
g.add_edge(3, 4)
g.add_edge(4, 6)
g.add_edge(4, 7)
g.add_edge(5, 6)
g.add_edge(6, 7)

#-----------------ACTUAL CODE-------------------------------
# g will be provided to MIS function
# returns MIS and its length

td = g.treewidth(certificate=True)

max_nei = 0
for v in td.vertices():
    if len(td.neighbors(v)) > max_nei:
        max_nei = len(td.neighbors(v))
        root_node = v
        
print("Root Node:", root_node)
# print("Neighbours of Root Node:", td.neighbors(root_node))

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
bags_processed_A = [False for _ in range(a_c)]
for b in leaf_nodes:
    for v in b:
        if v not in A:
            A[v] = {}
        A[v][a_c - bag_number[b] - 1] = {v}
    bags_processed_A[bag_number[b]] = True

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

# Bottom of B
for i, j in leaf_pairs:
    # Fill None
    B[None][(i,j)] = number_to_bag[i] - number_to_bag[j]
    # Fill Leaf Pairs
    for ver in pairs[(i, j)]:
        for v in ver:
            if v not in B:
                B[v] = {}
            B[v][(i,j)] = {v} & set(number_to_bag[i]) & set(number_to_bag[j])

for i in range(len(bags_processed_A)-1, -1, -1):
    if bags_processed_A[i]:
        continue
    count = 1
    # Compute A
    for v in A.keys():
        if v == None:
            tmp = set()
            for nei in td.neighbors(number_to_bag[i]):
                j = bag_number[nei]
                key = (max(i, j), min(i, j))
                if key in B[None]:
                    tmp = tmp | (set(B[None][key]))
            A[None][a_c - i - 1] = tmp
        elif (v in number_to_bag[i]) and (v in b_set):
            tmp = {v}
            for nei in td.neighbors(number_to_bag[i]):
                j = bag_number[nei]
                if j < i:
                    continue
                key = (max(i, j), min(i, j))
                if key in B[v]:
                    tmp = tmp | (set(B[v][key]) - ({v} & set(number_to_bag[max(i, j)])))
                elif key in B[None]:
                    tmp = tmp | (set(B[None][key]))
                if v not in A:
                    A[v] = {}
                A[v][a_c - i - 1] = tmp
        
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
                s = A[ver][a_c - i - 1]
                if len(s) > max_val:
                    max_set = s
                    max_val = len(s)
            B[v][(i, j)] = max_set
        B[None][(i, j)] = A[None][a_c - i - 1]
    bags_processed_A[i] = True

mis_val = 0
mis_set = {}
for v in A.keys():
    if (a_c - 1) in A[v]:
        if len(A[v][a_c - 1]) > mis_val:
            mis_set = A[v][a_c - 1]
            mis_val = len(A[v][a_c - 1])

print('-------------------------------Table A------------------------------')
for k, v in A.items():
    if k == None:
        k = "None"
    print(f"{str(k):10} : {v}")
    
print('------------------------------Table B------------------------------')
for k, v in B.items():
    if k == None:
        k = "None"
    print(f"{str(k):10} : {v}")

print('-------------------------------------------------------------------')
print("MIS SET:", mis_set, " | ", "MIS VAL:", mis_val)

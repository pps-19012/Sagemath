def powerset(s):
    """
    Computes Powerset of a given Sage Set

    Args:
        s ('sage.sets.set.Set_object_enumerated_with_category'): Set S containing the vertices that are present in a node of tree decomposition of a graph.

    Yields:
        <class 'generator'>: Powerset of the set S
    """
    x = len(s)
    masks = [1 << i for i in range(x)]
    for i in range(1 << x):
        yield [ss for mask, ss in zip(masks, s) if i & mask]
        
# g: graph, td: tree decomposition
def mis(g, td):
    """
    Determines the Maximum Independent Set (MIS) for a graph using its tree decomposition
    
    Args:
        g ('sage.graphs.graph.Graph'): Arbitrary Graph G
        td ('sage.graphs.graph.Graph'): Tree Decomposition of Graph G
        
    Algorithm:    
    This function uses Dynamic Programming approach to find the MIS utilizing the treewidth parameter k from its tree decomposition.
    
        Notations:
        - X_i: a node of the tree decomposition
        - D_i: the union of the sets X_j descending from X_i
        - A(S, i): the size of the largest independent subset I of D_i such that:
            - I ∩ X_i = S
        - B(S, i, j): the size of the largest independent subset I of D_i such that:
            - X_i and X_j are adjacent pair
            - X_i is farther from the root of the tree decomposition than X_j
            - I ∩ X_i ∩ X_j = S
        
        Note: I am referring the bags of the tree decomposition as nodes in the following explanations.
        
        Implementation:
        - We assume one of the nodes as root node and accordingly find leaf nodes.
        - Initialize table A and table B using the vertices present in leaf nodes.
        - For each next step, we move closer to the root node starting from the leaf nodes.
        - Compute the next state of table A using table B by the following:
            - A(S, i) = |S| +  Σ (B(S ∩ X_j, j, i) - |S ∩ X_j|) over all neighbours j
            - To simplify, for every subset in each node we are computing the maximum independent set possible including that subset.
        - Compute the next state of table B using table A by the following:
            - B(S, i, j) = maximum of A(S', i) where S' is a subset of X_i and S = S' ∩ X_j
            - To simplify, for every subset shared between two neighbours we are maximum independent set possible including that subset.
            
    This approach is faster as maximum number of subsets at any node can be at most 2^k where k is the tree width of the graph.
    Thus, the time taken to find MIS is proportional to a constant 2^k.

    Returns:
        tuple('set', 'int'): (Maximum Independet Set (MIS), Cardinality of MIS)
    """
    
    # Root node can be chose at random but here it is the bag with maximum of neighbours in tree decomposition.
    # This is seems to make calculations a little faster as tree depth is usually less by choosing such a root node.
    max_nei = 0
    for v in td.vertices():
        if len(td.neighbors(v)) > max_nei:
            max_nei = len(td.neighbors(v))
            root_node = v

    # find leaf nodes
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

    # map bags to numbers
    bag_number = {}
    bn = 0
    for k, ver in bags.items():
        for v in ver:
            bag_number[v] = bn
            bn += 1

    # map numbers to bags
    number_to_bag = {}
    for k, v in bag_number.items():
        number_to_bag[v] = k

    # initialize table A
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
        for nei in td.neighbors(node):
            if nei not in visit:
                q.append(nei)
                if node in leaf_nodes or nei in leaf_nodes:
                    leaf_pairs.append((bag_number[nei], bag_number[node]))

    # initialize table B
    B = {None:{}}

    for i, j in leaf_pairs:
        # fill null
        B[None][(i,j)] = number_to_bag[i] - number_to_bag[j]
        
        # fill leaf pairs
        inter = number_to_bag[i] & number_to_bag[j]
        for v in inter:
            if v not in B:
                B[v] = {}
            if v in (number_to_bag[i] & number_to_bag[j]):
                B[v][(i,j)] = {v}

    # compute rest of states of table A and table B
    for i in range(len(bags_processed_A)-1, -1, -1):
        if bags_processed_A[i]:
            continue
            
        # compute A(S, i)
        
        powerset_of_bag_node = powerset(number_to_bag[i])
        # iterate over all the subsets of X_i
        for k in powerset_of_bag_node:
            tmp = set(k)
            for nei in td.neighbors(number_to_bag[i]):
                j = bag_number[nei]
                if j < i:
                    continue
                
                # intersection with neighbours X_j to get MIS for each subtree descending from X_i
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
                
            # set state in table A
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

        # compute B(S, i, j)
        for nei in td.neighbors(number_to_bag[i]):
            j = bag_number[nei]
            if j > i:
                continue
            
            # iterate over all subsets S' of X_i
            for l in powerset(number_to_bag[i]):
                if len(l) == 0:
                    s_prime = None
                elif len(l) == 1:
                    s_prime = l[0]
                else:
                    s_prime = tuple(l)
                
                # intersection with neighbours X_j to get MIS among all neighbours descending from X_i
                k = set(l) & set(number_to_bag[j])
                if len(k) == 0:
                    s = None
                elif len(k) == 1:
                    s = list(k)[0]
                else:
                    s = tuple(k)
                if (s_prime not in A) or (i not in A[s_prime]):
                    continue
                
                # set state in table B
                if s not in B:
                    B[s] = {}
                if (i, j) not in B[s]:
                    B[s][(i, j)] = A[s_prime][i]
                else:
                    if len(B[s][(i, j)]) <= len(A[s_prime][i]):
                        B[s][(i, j)] = A[s_prime][i]
        
        # bag X_i is processed, move to its neighbours in next iteration                
        bags_processed_A[i] = True

    # iterate over A(S, 0) to find the largest independent set for X_i(i = 0) or root node
    mis_set = {}
    for v in A.keys():
        if 0 in A[v] and len(A[v][0]) > len(mis_set):
            mis_set = A[v][0]
          
    return (mis_set, len(mis_set))

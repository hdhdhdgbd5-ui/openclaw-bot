# ADVANCED ALGORITHMS MASTERCLASS
## NP-Hard, Graph Theory & Computational Complexity

---

## 1. NP-COMPLETE PROBLEMS DEEP DIVE

### 1.1 The P vs NP Problem
```
P (Polynomial Time):     Problems solvable in O(n^k)
NP (Nondeterministic Polynomial): Solutions verifiable in O(n^k)
NP-Complete:            Hardest problems in NP
NP-Hard:                At least as hard as NP-Complete
```

### 1.2 Famous NP-Complete Problems

#### Traveling Salesman Problem (TSP)
```python
"""
Traveling Salesman Problem - Dynamic Programming Solution
Time: O(n^2 * 2^n) | Space: O(n * 2^n)
"""
from functools import lru_cache
import itertools

def tsp_dp(distance_matrix):
    n = len(distance_matrix)
    ALL_VISITED = (1 << n) - 1
    
    @lru_cache(None)
    def dp(current, visited):
        if visited == ALL_VISITED:
            return distance_matrix[current][0]
        
        min_dist = float('inf')
        for next_city in range(n):
            if not (visited & (1 << next_city)):
                dist = distance_matrix[current][next_city] + dp(next_city, visited | (1 << next_city))
                min_dist = min(min_dist, dist)
        return min_dist
    
    return dp(0, 1)

# Example usage
distances = [
    [0, 10, 15, 20],
    [10, 0, 35, 25],
    [15, 35, 0, 30],
    [20, 25, 30, 0]
]
print(f"TSP Optimal: {tsp_dp(distances)}")
```

#### Hamiltonian Path (Backtracking)
```python
def hamiltonian_path(graph, start=0):
    n = len(graph)
    path = [start]
    visited = {start}
    
    def backtrack():
        if len(path) == n:
            return True
        
        current = path[-1]
        for neighbor in range(n):
            if neighbor not in visited and graph[current][neighbor]:
                visited.add(neighbor)
                path.append(neighbor)
                
                if backtrack():
                    return True
                
                path.pop()
                visited.remove(neighbor)
        return False
    
    if backtrack():
        return path
    return None
```

#### SAT (Boolean Satisfiability)
```python
"""
2-SAT Solver - Linear Time O(V + E)
"""
from collections import defaultdict, deque

class TwoSAT:
    def __init__(self, n):
        self.n = n
        self.adj = defaultdict(list)
        self.radj = defaultdict(list)
    
    def add_implication(self, u, v):
        """(u OR v) -> (!u -> v) AND (!v -> u)"""
        self.adj[u].append(v)
        self.radj[v].append(u)
        self.adj[v ^ 1].append(u ^ 1)
        self.radj[u ^ 1].append(v ^ 1)
    
    def satisfy(self):
        # Kosaraju's SCC algorithm
        visited = [False] * (2 * self.n)
        order = []
        
        def dfs(v):
            visited[v] = True
            for to in self.adj[v]:
                if not visited[to]:
                    dfs(to)
            order.append(v)
        
        for v in range(2 * self.n):
            if not visited[v]:
                dfs(v)
        
        comp = [-1] * (2 * self.n)
        assignment = [False] * self.n
        
        def rdfs(v, cl):
            comp[v] = cl
            for to in self.radj[v]:
                if comp[to] == -1:
                    rdfs(to, cl)
        
        j = 0
        for v in reversed(order):
            if comp[v] == -1:
                rdfs(v, j)
                j += 1
        
        for i in range(self.n):
            if comp[2*i] == comp[2*i+1]:
                return None
            assignment[i] = comp[2*i] > comp[2*i+1]
        
        return assignment

# Example: (A OR B) AND (NOT A OR C) AND (NOT B OR NOT C)
sat = TwoSAT(3)
sat.add_implication(0, 1)  # A -> C
sat.add_implication(2, 1)  # NOT A -> C
sat.add_implication(1, 2)  # NOT A -> NOT B
sat.add_implication(3, 0)  # C -> NOT B (wrong order fix below)
sat.add_implication(2, 3)  # NOT B -> NOT C
sat.add_implication(1, 0)  # C -> A
result = sat.satisfy()
print(f"2-SAT Solution: {result}")
```

---

## 2. GRAPH ALGORITHMS

### 2.1 Strongly Connected Components (Kosaraju + Tarjan)
```python
"""
Tarjan's Algorithm - O(V + E)
Finds SCCs in linear time
"""
class TarjanSCC:
    def __init__(self, graph):
        self.graph = graph
        self.n = len(graph)
        self.index = 0
        self.stack = []
        self.on_stack = [False] * self.n
        self.index_arr = [-1] * self.n
        self.low_link = [0] * self.n
        self.sccs = []
    
    def strong_connect(self, v):
        self.index_arr[v] = self.index
        self.low_link[v] = self.index
        self.index += 1
        self.stack.append(v)
        self.on_stack[v] = True
        
        for w in self.graph[v]:
            if self.index_arr[w] == -1:
                self.strong_connect(w)
                self.low_link[v] = min(self.low_link[v], self.low_link[w])
            elif self.on_stack[w]:
                self.low_link[v] = min(self.low_link[v], self.index_arr[w])
        
        if self.low_link[v] == self.index_arr[v]:
            scc = []
            while True:
                w = self.stack.pop()
                self.on_stack[w] = False
                scc.append(w)
                if w == v:
                    break
            self.sccs.append(scc)
    
    def find_sccs(self):
        for v in range(self.n):
            if self.index_arr[v] == -1:
                self.strong_connect(v)
        return self.sccs
```

### 2.2 Maximum Flow (Edmonds-Karp + Dinic)
```python
"""
Dinic's Algorithm - O(E * sqrt(V)) for unit capacity, O(V^2 * E) general
"""
from collections import deque

class Dinic:
    def __init__(self, n):
        self.n = n
        self.graph = [[] for _ in range(n)]
    
    def add_edge(self, u, v, capacity):
        forward = [v, capacity, None]
        backward = [u, 0, forward]
        forward[2] = backward
        self.graph[u].append(forward)
        self.graph[v].append(backward)
    
    def bfs(self, s, t, level):
        for i in range(self.n):
            level[i] = -1
        level[s] = 0
        q = deque([s])
        
        while q:
            v = q.popleft()
            for to, cap, rev in self.graph[v]:
                if cap > 0 and level[to] < 0:
                    level[to] = level[v] + 1
                    q.append(to)
        return level[t] >= 0
    
    def dfs(self, v, t, f, level, it):
        if v == t:
            return f
        for i in range(it[v], len(self.graph[v])):
            it[v] = i
            to, cap, rev = self.graph[v][i]
            if cap > 0 and level[v] < level[to]:
                d = self.dfs(to, t, min(f, cap), level, it)
                if d > 0:
                    self.graph[v][i][1] -= d
                    rev[1] += d
                    return d
        return 0
    
    def max_flow(self, s, t):
        flow = 0
        level = [-1] * self.n
        
        while self.bfs(s, t, level):
            it = [0] * self.n
            while True:
                f = self.dfs(s, t, float('inf'), level, it)
                if f == 0:
                    break
                flow += f
        return flow
```

### 2.3 Minimum Spanning Tree (Prim + Kruskal + Boruvka)
```python
"""
Boruvka's Algorithm - O(E * log V)
Each iteration halves the number of components
"""
class BoruvkaMST:
    def __init__(self, n, edges):
        self.n = n
        self.edges = edges  # [(u, v, weight), ...]
        self.parent = list(range(n))
        self.rank = [0] * n
    
    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    
    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px == py:
            return False
        if self.rank[px] < self.rank[py]:
            px, py = py, px
        self.parent[py] = px
        if self.rank[px] == self.rank[py]:
            self.rank[px] += 1
        return True
    
    def mst(self):
        mst_edges = []
        components = set(range(self.n))
        
        while len(components) > 1:
            cheapest = {}
            
            for u, v, w in self.edges:
                cu, cv = self.find(u), self.find(v)
                if cu == cv:
                    continue
                
                if cu not in cheapest or w < cheapest[cu][2]:
                    cheapest[cu] = (u, v, w)
                if cv not in cheapest or w < cheapest[cv][2]:
                    cheapest[cv] = (u, v, w)
            
            for comp in list(components):
                if comp in cheapest:
                    u, v, w = cheapest[comp]
                    if self.union(u, v):
                        mst_edges.append((u, v, w))
                        components.discard(self.find(u))
                        components.discard(self.find(v))
            
            if not cheapest:
                return None  # Graph not connected
        
        return mst_edges
```

---

## 3. STRING ALGORITHMS

### 3.1 Suffix Automaton
```python
"""
Suffix Automaton - O(N) construction
Allows O(1) substring queries
"""
class SuffixAutomaton:
    def __init__(self):
        self.next = {}
        self.link = {}
        self.len = {}
        self.first = 0
        self.last = 0
        self.size = 1
        self.next[self.first] = {}
        self.link[self.first] = -1
        self.len[self.first] = 0
    
    def extend(self, c):
        p = self.last
        cur = self.size
        self.size += 1
        self.len[cur] = self.len[p] + 1
        self.next[cur] = {}
        
        while p != -1 and c not in self.next[p]:
            self.next[p][c] = cur
            p = self.link[p]
        
        if p == -1:
            self.link[cur] = 0
        else:
            q = self.next[p][c]
            if self.len[p] + 1 == self.len[q]:
                self.link[cur] = q
            else:
                clone = self.size
                self.size += 1
                self.len[clone] = self.len[p] + 1
                self.next[clone] = self.next[q].copy()
                self.link[clone] = self.link[q]
                
                while p != -1 and self.next[p].get(c) == q:
                    self.next[p][c] = clone
                    p = self.link[p]
                
                self.link[q] = self.link[cur] = clone
        
        self.last = cur
    
    def contains(self, s):
        v = 0
        for c in s:
            if c not in self.next[v]:
                return False
            v = self.next[v][c]
        return True
```

### 3.2 Aho-Corasick (Multi-pattern Matching)
```python
"""
Aho-Corasick - O(text_len + patterns_len + matches)
"""
from collections import deque

class AhoCorasick:
    def __init__(self):
        self.next = {}
        self.fail = {}
        self.output = {}
        self.root = 0
        self.next[self.root] = {}
        self.fail[self.root] = 0
        self.output[self.root] = []
        self.size = 1
    
    def add_pattern(self, pattern):
        v = 0
        for c in pattern:
            if c not in self.next[v]:
                self.next[v][c] = self.size
                self.next[self.size] = {}
                self.fail[self.size] = 0
                self.output[self.size] = []
                self.size += 1
            v = self.next[v][c]
        self.output[v].append(pattern)
    
    def build(self):
        queue = deque()
        for c, v in self.next[0].items():
            queue.append(v)
            self.fail[v] = 0
        
        while queue:
            u = queue.popleft()
            for c, v in self.next[u].items():
                queue.append(v)
                f = self.fail[u]
                while f and c not in self.next[f]:
                    f = self.fail[f]
                self.fail[v] = self.next[f].get(c, 0)
                self.output[v] += self.output[self.fail[v]]
    
    def search(self, text):
        results = []
        v = 0
        for i, c in enumerate(text):
            while v and c not in self.next[v]:
                v = self.fail[v]
            v = self.next[v].get(c, 0)
            for pattern in self.output[v]:
                results.append((i - len(pattern) + 1, pattern))
        return results
```

---

## 4. COMPUTATIONAL GEOMETRY

### 4.1 Convex Hull (Graham Scan + Monotone Chain)
```python
"""
Convex Hull - O(N log N)
"""
def convex_hull(points):
    points = sorted(set(points))
    if len(points) <= 1:
        return points
    
    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    
    lower = []
    for p in points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    
    upper = []
    for p in reversed(points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    
    return lower[:-1] + upper[:-1]

### 4.2 Point in Polygon (Ray Casting)
def point_in_polygon(point, polygon):
    x, y = point
    inside = False
    n = len(polygon)
    j = n - 1
    
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    
    return inside
```

---

## 5. ADVANCED DATA STRUCTURES

### 5.1 Treap (Randomized BST)
```python
"""
Treap - O(log N) average for all operations
Combines BST + Heap properties
"""
import random

class TreapNode:
    def __init__(self, key, val):
        self.key = key
        self.val = val
        self.prio = random.random()
        self.left = None
        self.right = None

class Treap:
    def __init__(self):
        self.root = None
    
    def rotate_right(self, y):
        x = y.left
        y.left = x.right
        x.right = y
        return x
    
    def rotate_left(self, x):
        y = x.right
        x.right = y.left
        y.left = x
        return y
    
    def insert(self, root, key, val):
        if not root:
            return TreapNode(key, val)
        if key < root.key:
            root.left = self.insert(root.left, key, val)
            if root.left.prio < root.prio:
                root = self.rotate_right(root)
        else:
            root.right = self.insert(root.right, key, val)
            if root.right.prio < root.prio:
                root = self.rotate_left(root)
        return root
    
    def search(self, root, key):
        if not root:
            return None
        if key == root.key:
            return root.val
        elif key < root.key:
            return self.search(root.left, key)
        else:
            return self.search(root.right, key)
```

### 5.2 Link-Cut Tree (Dynamic Tree)
```python
"""
Link-Cut Tree - O(log N) for tree operations
Used for dynamic connectivity, path queries
"""
class LinkCutNode:
    def __init__(self, val):
        self.val = val
        self.sum = val
        self.left = None
        self.right = None
        self.parent = None
        self.rev = False

class LinkCutTree:
    def is_root(self, x):
        return not x.parent or (x.parent.left != x and x.parent.right != x)
    
    def push(self, x):
        if x and x.rev:
            x.left, x.right = x.right, x.left
            if x.left: x.left.rev ^= True
            if x.right: x.right.rev ^= True
            x.rev = False
    
    def pull(self, x):
        x.sum = x.val
        if x.left:
            x.sum += x.left.sum
        if x.right:
            x.sum += x.right.sum
    
    def rotate(self, x):
        y = x.parent
        z = y.parent
        if not self.is_root(y):
            if z.left == y: z.left = x
            else: z.right = x
        x.parent = z
        
        if y.left == x:
            y.left = x.right
            if x.right: x.right.parent = y
            x.right = y
        else:
            y.right = x.left
            if x.left: x.left.parent = y
            x.left = y
        y.parent = x
        self.pull(y)
        self.pull(x)
    
    def splay(self, x):
        stack = []
        y = x
        stack.append(y)
        while not self.is_root(y):
            y = y.parent
            stack.append(y)
        while stack:
            self.push(stack.pop())
        
        while not self.is_root(x):
            y = x.parent
            z = y.parent
            if not self.is_root(y):
                if (y.left == x) ^ (z.left == y):
                    self.rotate(x)
                else:
                    self.rotate(y)
            self.rotate(x)
    
    def access(self, x):
        last = None
        while x:
            self.splay(x)
            x.right = last
            self.pull(x)
            last = x
            x = x.parent
        if last:
            self.splay(last)
    
    def make_root(self, x):
        self.access(x)
        x.rev ^= True
        self.push(x)
    
    def find_root(self, x):
        self.access(x)
        while True:
            self.push(x)
            if not x.left:
                break
            x = x.left
        self.splay(x)
        return x
    
    def link(self, x, y):
        self.make_root(x)
        if self.find_root(y) != x:
            x.parent = y
    
    def cut(self, x, y):
        self.make_root(x)
        self.access(y)
        if y.left == x:
            y.left.parent = None
            y.left = None
            self.pull(y)
```

---

## 6. APPROXIMATION ALGORITHMS

### 6.1 Vertex Cover (2-Approximation)
```python
"""
Vertex Cover - 2-approximation using matching
"""
def vertex_cover_approx(edges):
    """edges: list of (u, v)"""
    graph = {}
    for u, v in edges:
        graph.setdefault(u, []).append(v)
        graph.setdefault(v, []).append(u)
    
    cover = set()
    remaining = set(graph.keys())
    
    while remaining:
        u = remaining.pop()
        if u in graph:
            for v in graph[u]:
                if v in remaining:
                    cover.add(u)
                    cover.add(v)
                    remaining.discard(v)
                    remaining.discard(u)
                    break
    
    return cover
```

### 6.2 TSP Approximation (Christofides)
```python
"""
Christofides Algorithm - 1.5-approximation for metric TSP
"""
def christofides_tsp(graph):
    """
    graph: adjacency matrix
    Returns approx 1.5x optimal tour
    """
    # 1. Find MST
    mst = kruskal_mst(graph)
    
    # 2. Find odd degree vertices in MST
    odd_vertices = [v for v in range(len(graph)) if degree_in_mst(mst, v) % 2 == 1]
    
    # 3. Minimum weight perfect matching on odd vertices
    matching = min_weight_matching(graph, odd_vertices)
    
    # 4. Combine MST + matching to get Eulerian circuit
    eulerian = combine_mst_matching(mst, matching)
    
    # 5. Shortcut to get Hamiltonian (skip repeated vertices)
    return shortcut_hamiltonian(eulerian)
```

---

## 7. RANDOMIZED ALGORITHMS

### 7.1 Miller-Rabin Primality Test
```python
"""
Miller-Rabin - O(k * log^3 n)
k iterations, error probability < 4^-k
"""
import random

def mulmod(a, b, mod):
    return (a * b) % mod

def powmod(a, d, mod):
    result = 1
    a = a % mod
    while d:
        if d & 1:
            result = mulmod(result, a, mod)
        d >>= 1
        a = mulmod(a, a, mod)
    return result

def is_prime(n, k=40):
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False
    
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = powmod(a, d, n)
        
        if x == 1 or x == n - 1:
            continue
        
        for _ in range(r - 1):
            x = mulmod(x, x, n)
            if x == n - 1:
                break
        else:
            return False
    
    return True
```

### 7.2 Skip Lists
```python
"""
Skip List - O(log N) average for all operations
Probabilistic balanced data structure
"""
import random

class SkipListNode:
    def __init__(self, key, level):
        self.key = key
        self.forward = [None] * (level + 1)

class SkipList:
    MAX_LEVEL = 16
    
    def __init__(self):
        self.header = SkipListNode(None, self.MAX_LEVEL)
        self.level = 0
    
    def random_level(self):
        lvl = 0
        while random.random() < 0.5 and lvl < self.MAX_LEVEL:
            lvl += 1
        return lvl
    
    def search(self, key):
        current = self.header
        for i in range(self.level, -1, -1):
            while current.forward[i] and current.forward[i].key < key:
                current = current.forward[i]
        current = current.forward[0]
        if current and current.key == key:
            return current
        return None
    
    def insert(self, key):
        update = [None] * (self.MAX_LEVEL + 1)
        current = self.header
        
        for i in range(self.level, -1, -1):
            while current.forward[i] and current.forward[i].key < key:
                current = current.forward[i]
            update[i] = current
        
        current = current.forward[0]
        if not current or current.key != key:
            lvl = self.random_level()
            if lvl > self.level:
                for i in range(self.level + 1, lvl + 1):
                    update[i] = self.header
                self.level = lvl
            
            node = SkipListNode(key, lvl)
            for i in range(lvl + 1):
                node.forward[i] = update[i].forward[i]
                update[i].forward[i] = node
    
    def delete(self, key):
        update = [None] * (self.MAX_LEVEL + 1)
        current = self.header
        
        for i in range(self.level, -1, -1):
            while current.forward[i] and current.forward[i].key < key:
                current = current.forward[i]
            update[i] = current
        
        current = current.forward[0]
        if current and current.key == key:
            for i in range(self.level + 1):
                if update[i].forward[i] == current:
                    update[i].forward[i] = current.forward[i]
            while self.level > 0 and not self.header.forward[self.level]:
                self.level -= 1
            return True
        return False
```

---

## 8. PRACTICE PROBLEMS & SOLUTIONS

### Problem 1: Longest Common Subsequence (4 variants)
```python
# Classic LCS - O(mn)
def lcs(s1, s2):
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    
    # Backtrack to find the LCS string
    lcs_str = []
    i, j = m, n
    while i > 0 and j > 0:
        if s1[i-1] == s2[j-1]:
            lcs_str.append(s1[i-1])
            i -= 1
            j -= 1
        elif dp[i-1][j] > dp[i][j-1]:
            i -= 1
        else:
            j -= 1
    
    return ''.join(reversed(lcs_str)), dp[m][n]

# Space-optimized LCS - O(min(m,n))
def lcs_optimized(s1, s2):
    if len(s1) < len(s2):
        s1, s2 = s2, s1
    
    m, n = len(s1), len(s2)
    prev = [0] * (n + 1)
    curr = [0] * (n + 1)
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i-1] == s2[j-1]:
                curr[j] = prev[j-1] + 1
            else:
                curr[j] = max(prev[j], curr[j-1])
        prev, curr = curr, prev
    
    return prev[n]

# Longest Common Substring - O(mn)
def longest_common_substring(s1, s2):
    m, n = len(s1), len(s2)
    max_len = 0
    end_idx = 0
    
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
                if dp[i][j] > max_len:
                    max_len = dp[i][j]
                    end_idx = i
    
    return s1[end_idx - max_len:end_idx], max_len
```

### Problem 2: All-Pairs Shortest Path (Floyd-Warshall variants)
```python
# Floyd-Warshall with path reconstruction
def floyd_warshall_with_path(n, edges):
    INF = float('inf')
    dist = [[INF] * n for _ in range(n)]
    nxt = [[-1] * n for _ in range(n)]
    
    for i in range(n):
        dist[i][i] = 0
    
    for u, v, w in edges:
        dist[u][v] = w
        nxt[u][v] = v
    
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    nxt[i][j] = nxt[i][k]
    
    def get_path(u, v):
        if dist[u][v] == INF:
            return None
        path = [u]
        while u != v:
            u = nxt[u][v]
            path.append(u)
        return path
    
    return dist, get_path
```

---

## COMPLEXITY CHEAT SHEET

| Algorithm | Time | Space |
|-----------|------|-------|
| Quick Sort | O(n log n) avg | O(log n) |
| Merge Sort | O(n log n) | O(n) |
| Heap Sort | O(n log n) | O(1) |
| Dijkstra | O((V+E) log V) | O(V) |
| Bellman-Ford | O(VE) | O(V) |
| Floyd-Warshall | O(V^3) | O(V^2) |
| Kosaraju SCC | O(V+E) | O(V) |
| Dinic Flow | O(V^2 E) | O(E) |
| KMP | O(n+m) | O(m) |
| Rabin-Karp | O(n+m) avg | O(1) |
|Suffix Array | O(n log n) | O(n) |
| Treap | O(log n) avg | O(n) |
| Skip List | O(log n) avg | O(n) |
| B-Tree | O(log n) | O(n) |
| Red-Black | O(log n) | O(n) |

---

*End of Advanced Algorithms Masterclass*

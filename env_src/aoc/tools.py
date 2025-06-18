from __future__ import annotations
import collections
import heapq
import functools
import math
from typing import Any, Callable, Dict, Generator, List, Tuple, TypeVar, Union

Node = TypeVar('Node')

# --- Performance & Recursion Helpers ---

def memoize(func: Callable) -> Callable:
    """A decorator to cache the results of a function."""
    cache = {}
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        key = (args, frozenset(kwargs.items()))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    return wrapper

# --- Common Data Structures ---

class TreeNode:
    """A simple TreeNode for building tree structures."""
    def __init__(self, value: Any, parent: TreeNode | None = None):
        self.value = value
        self.parent = parent
        self.children: List['TreeNode'] = []

    def add_child(self, child_node: 'TreeNode'):
        self.children.append(child_node)

# --- Grid & Geometry Tools ---

class Grid:
    """A helper class for 2D grids, providing easy access and neighbor finding."""
    def __init__(self, grid_data: List[List[Any]]):
        self.grid = grid_data
        self.height = len(grid_data)
        self.width = len(grid_data[0]) if self.height > 0 else 0

    def __getitem__(self, coords: Tuple[int, int]) -> Any:
        x, y = coords
        return self.grid[y][x]

    def __setitem__(self, coords: Tuple[int, int], value: Any):
        x, y = coords
        self.grid[y][x] = value

    def __iter__(self) -> Generator[Tuple[int, int, Any], None, None]:
        for y in range(self.height):
            for x in range(self.width):
                yield x, y, self.grid[y][x]

    def neighbors(self, x: int, y: int, diagonal: bool = False) -> Generator[Tuple[int, int], None, None]:
        deltas = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        if diagonal:
            deltas.extend([(-1, -1), (-1, 1), (1, -1), (1, 1)])

        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                yield nx, ny

def manhattan_distance(p1: Tuple[int, int], p2: Tuple[int, int]) -> int:
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def add_vec(v1: Tuple[int, int], v2: Tuple[int, int]) -> Tuple[int, int]:
    return v1[0] + v2[0], v1[1] + v2[1]

def shoelace_area(vertices: List[Tuple[int, int]]) -> float:
    area = 0.0
    n = len(vertices)
    for i in range(n):
        j = (i + 1) % n
        area += vertices[i][0] * vertices[j][1]
        area -= vertices[j][0] * vertices[i][1]
    return abs(area) / 2.0

def bresenham_line(p1: Tuple[int, int], p2: Tuple[int, int]) -> List[Tuple[int, int]]:
    x1, y1 = p1
    x2, y2 = p2
    points = []
    dx, dy = abs(x2 - x1), -abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx + dy
    while True:
        points.append((x1, y1))
        if x1 == x2 and y1 == y2:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x1 += sx
        if e2 <= dx:
            err += dx
            y1 += sy
    return points

# --- Graph Algorithms ---

def bfs(graph: Dict[Node, List[Node]], start_node: Node) -> Generator[Node, None, None]:
    visited = {start_node}
    queue = collections.deque([start_node])
    while queue:
        node = queue.popleft()
        yield node
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

def dfs(graph: Dict[Node, List[Node]], start_node: Node) -> Generator[Node, None, None]:
    visited = set()
    stack = [start_node]
    while stack:
        node = stack.pop()
        if node not in visited:
            visited.add(node)
            yield node
            # Add neighbors to the stack in reverse to visit them in a more standard order
            for neighbor in reversed(graph.get(node, [])):
                if neighbor not in visited:
                    stack.append(neighbor)

def dijkstra(graph: Dict[Node, List[Tuple[Node, int]]], start: Node, end: Node) -> Tuple[Union[int, float], List[Node]]:
    """
    Finds the shortest path in a weighted graph using Dijkstra's algorithm.

    Args:
        graph: Adjacency list where graph[node] = [(neighbor, weight), ...].
        start: The starting node.
        end: The target node.

    Returns:
        A tuple of (total_distance, path_list). Distance is float('inf') if no path is found.
    """
    pq = [(0, start, [])]  # (distance, node, path)
    visited = set()

    while pq:
        dist, node, path = heapq.heappop(pq)

        if node in visited:
            continue

        path = path + [node]
        visited.add(node)

        if node == end:
            return dist, path

        for neighbor, weight in graph.get(node, []):
            if neighbor not in visited:
                heapq.heappush(pq, (dist + weight, neighbor, path))

    return float('inf'), []

# --- Interval Tools ---

def merge_intervals(intervals: List[List[int]]) -> List[List[int]]:
    if not intervals:
        return []
    intervals.sort(key=lambda x: x[0])
    merged = [intervals[0]]
    for current in intervals[1:]:
        last = merged[-1]
        if current[0] <= last[1]:
            last[1] = max(last[1], current[1])
        else:
            merged.append(current)
    return merged

# --- Advanced Math Tools ---

def chinese_remainder_theorem(n: List[int], a: List[int]) -> int:
    """
    Solves a system of congruences using the Chinese Remainder Theorem.
    x ≡ a_i (mod n_i)
    """
    sum_val = 0
    prod = math.prod(n)
    for n_i, a_i in zip(n, a):
        p = prod // n_i
        sum_val += a_i * pow(p, -1, n_i) * p
    return sum_val % prod

# --- Tree Traversal Algorithms ---

def pre_order_traversal(root: TreeNode) -> Generator[TreeNode, None, None]:
    """
    Performs a pre-order traversal of a tree, yielding each node.
    (Parent, then children)
    """
    yield root
    for child in root.children:
        yield from pre_order_traversal(child)

def post_order_traversal(root: TreeNode) -> Generator[TreeNode, None, None]:
    """
    Performs a post-order traversal of a tree, yielding each node.
    (Children, then parent)
    """
    for child in root.children:
        yield from post_order_traversal(child)
    yield root

def in_order_traversal(root: TreeNode) -> Generator[TreeNode, None, None]:
    """
    Performs an in-order traversal of a tree, yielding each node.
    (Left-most child, then parent, then remaining children).
    Note: Primarily for binary trees, but generalized for n-ary trees.
    """
    if not root.children:
        yield root
        return

    # In-order traverse the first child's subtree
    yield from in_order_traversal(root.children[0])

    # Visit the root node
    yield root

    # In-order traverse the rest of the children's subtrees
    for child in root.children[1:]:
        yield from in_order_traversal(child)

"""Implementation of a weighted directed graph data structure."""

from collections import deque
from dataclasses import dataclass
from typing import Generic, TypeVar

from src.dsa.bimap import BiMap

D = TypeVar('D')

@dataclass
class Vertex(Generic[D]):
    """Graph vertex."""
    def __init__(self, data: D):
        self.data: D = data
        self.name: str = ""

class DirectedGraph(Generic[D]):
    """Weighted graph.

    Negative values in the matrix indicate that the edge is pointed in the other direction.
    """
    _new_id: int = 0

    def __init__(self, size: int = 0):
        self._vertices: list[Vertex[D]] = []
        self._adjacency_matrix: list[list[int]] = []

        self._available_ids: deque[int] = deque()
        self._id_index: BiMap[int, int] = BiMap({})

        for _ in range(size):
            self._available_ids.append(self._new_id)
            self._new_id += 1

    def adjacent(self, v: int, u: int) -> bool:
        """Test whether there is an edge from vertex v to vertex u."""
        return self._adjacency_matrix[v][u] > 0

    def neighbors(self, vertex_id: int) -> list[int]:
        """Retrieve an array of vertex IDs that are accessible from the vertex."""
        result: list[int] = []
        for i in self._adjacency_matrix[self._id_index[vertex_id]]:
            if self._adjacency_matrix[self._id_index[vertex_id]][i] > 0:
                result.append(self._id_index.get_key(i))

        return result

    def add_vertex(self, v: Vertex[D]) -> int:
        """Add a vertex to the graph."""
        self._vertices.append(v)
        self._adjacency_matrix.append([0 for _ in range(len(self._adjacency_matrix))])

        for row in self._adjacency_matrix:
            row.append(0)

        if len(self._available_ids) == 0:
            self._available_ids.append(self._new_id)
            self._new_id += 1
        vid = self._available_ids.popleft()
        self._id_index[vid] = len(self._vertices) - 1
        return vid

    def remove_vertex(self, vertex_id: int) -> None:
        """Remove a vertex if it exists."""
        if vertex_id in self._id_index.keys():
            raise NotImplementedError

    def add_edge(self, v1_id: int, v2_id: int, weight: int) -> None:
        """Add an edge from vertex v1 to vertex v2 if it does not exist"""
        v1_index = self._id_index[v1_id]
        v2_index = self._id_index[v2_id]

        self._adjacency_matrix[v1_index][v2_index] =  weight
        self._adjacency_matrix[v2_index][v2_index] = -weight

    def remove_edge(self, v1_id: int, v2_id: int) -> None:
        """Remove an edge from v1 to v2, if it exists."""
        v1_index = self._id_index[v1_id]
        v2_index = self._id_index[v2_id]

        self._adjacency_matrix[v1_index][v2_index] = 0
        self._adjacency_matrix[v2_index][v2_index] = 0

    def get_vertex(self, vertex_id: int) -> Vertex[D]:
        """Get the vertex associated with the specified ID."""
        return self._vertices[self._id_index[vertex_id]]

    def set_vertex(self, vertex_id: int, v: Vertex[D]) -> None:
        """Update the vertex data associated with the specified ID, if it exists."""
        if vertex_id in self._id_index.keys():
            self._vertices[self._id_index[vertex_id]] = v

    def get_edge(self, v1_id: int, v2_id: int) -> int:
        """Get the weight associated with the edge from v1 to v2."""
        return self._adjacency_matrix[self._id_index[v1_id]][self._id_index[v2_id]]

    def set_edge(self, v1_id: int, v2_id: int, weight: int) -> None:
        """Update the weight associated with the edge from v1 to v2."""
        v1_index = self._id_index[v1_id]
        v2_index = self._id_index[v2_id]

        self._adjacency_matrix[v1_index][v2_index] =  weight
        self._adjacency_matrix[v2_index][v2_index] = -weight

    def find(self, name: str) -> int:
        """Find a vertex based on its name."""
        for i in range(len(self._vertices)):
            if self._vertices[i].name == name:
                return self._id_index.get_key(i)
        return -1

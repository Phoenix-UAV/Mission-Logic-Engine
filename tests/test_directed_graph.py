"""Test the DirectedGraph class"""
from src.dsa.directed_graph import Vertex, DirectedGraph

def test_directed_graph():
    """
    Test the directed graph implementation.

    The following graph will be used for testing:
    A -1-> B -2-> C
    |3     ^
    V      |2
    D -3-> E
    """
    graph: DirectedGraph[str] = DirectedGraph()
    id_a = graph.add_vertex(Vertex("A"))
    id_b = graph.add_vertex(Vertex("B"))
    id_c = graph.add_vertex(Vertex("C"))
    id_d = graph.add_vertex(Vertex("D"))
    id_e = graph.add_vertex(Vertex("E"))

    assert len(graph._adjacency_matrix) == len(graph._vertices)
    assert len(graph._adjacency_matrix[0]) == len(graph._vertices)

    graph.add_edge(id_a, id_b, 1)
    graph.add_edge(id_a, id_d, 3)
    graph.add_edge(id_d, id_e, 3)
    graph.add_edge(id_e, id_b, 2)
    graph.add_edge(id_b, id_c, 2)

    assert graph.adjacent(id_a, id_b)
    assert graph.adjacent(id_d, id_e)
    assert not graph.adjacent(id_c, id_b)
    assert graph.neighbors(id_a) == [id_b, id_d]

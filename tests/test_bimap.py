"""Test the BiMap class"""
from src.dsa.bimap import BiMap

def test_bimap():
    """Test the BiMap class"""

    my_bimap: BiMap[int, int] = BiMap({})

    my_bimap[0] = 9
    my_bimap[1] = 4

    assert my_bimap.get_value(0) == 9
    assert my_bimap.get_key(9) == 0
    assert list(my_bimap.keys()) == [0, 1]
    assert list(my_bimap.values()) == [9, 4]

    my_bimap[0] = 2
    assert my_bimap.get_key(2) == 0
    assert my_bimap.get_value(0) == 2

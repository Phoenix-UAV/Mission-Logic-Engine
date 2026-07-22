"""Definition for a bidirectional map data structure."""

from typing import TypeVar, Generic, override

K = TypeVar('K')
V = TypeVar('V')

class BiMap(Generic[K, V]):
    """Bidirectional map."""
    def __init__(self, pairs: dict[K, V]):
        self._key_to_value: dict[K, V] = pairs
        self._value_to_key: dict[V, K] = {}

        for key in self._key_to_value.keys():
            self._value_to_key[self._key_to_value[key]] = key

    def __getitem__(self, key: K) -> V:
        return self._key_to_value[key]

    def __setitem__(self, key: K, value: V):
        self._key_to_value[key] = value
        self._value_to_key[value] = key

    def __delitem__(self, key: K):
        value = self._key_to_value[key]
        del self._key_to_value[key]
        del self._value_to_key[value]

    @override
    def __repr__(self):
        return str(self._key_to_value)

    def get_key(self, value: V) -> K:
        """Get the key associated with the value"""
        return self._value_to_key[value]

    def get_value(self, key: K) -> V:
        """Get the value associated with the key"""
        return self._key_to_value[key]

    def keys(self):
        """Get the registered keys in the map"""
        return self._key_to_value.keys()

    def values(self):
        """Get the registered values in the map"""
        return self._key_to_value.values()

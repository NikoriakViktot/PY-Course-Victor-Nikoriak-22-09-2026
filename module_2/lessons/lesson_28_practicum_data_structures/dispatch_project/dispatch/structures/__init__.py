"""Структури даних диспетчерської: стек, черга, купа, префіксне дерево, LRU-кеш."""

from dispatch.structures.errors import EmptyError
from dispatch.structures.heap import MinHeap
from dispatch.structures.lru import LRUCache
from dispatch.structures.queue import Queue
from dispatch.structures.stack import Stack
from dispatch.structures.trie import Trie

__all__ = ["EmptyError", "LRUCache", "MinHeap", "Queue", "Stack", "Trie"]

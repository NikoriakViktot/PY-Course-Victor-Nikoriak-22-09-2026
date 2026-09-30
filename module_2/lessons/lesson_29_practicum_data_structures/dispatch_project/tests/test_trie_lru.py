import pytest

from dispatch.structures import LRUCache, Trie


def test_trie_prefix_search_sorted(addresses):
    trie = Trie(addresses)
    assert trie.starts_with("Хр") == ["Хрещатик, 1", "Хрещатик, 22"]
    assert trie.starts_with("Ки") == []


def test_trie_contains_only_whole_words(addresses):
    trie = Trie(addresses)
    assert "Хорива, 5" in trie
    assert "Хорива" not in trie


def test_trie_counts_unique_words():
    trie = Trie(["Поділ", "Поділ", "Позняки"])
    assert len(trie) == 2
    assert list(trie) == ["Поділ", "Позняки"]


def test_trie_limit(addresses):
    assert Trie(addresses).starts_with("", limit=2) == ["Оболонська, 12", "Олегівська, 3"]


def test_lru_evicts_least_recently_used():
    cache = LRUCache(2)
    cache.put("a", 1)
    cache.put("b", 2)
    cache.get("a")          # a — щойно використаний
    cache.put("c", 3)       # місця немає: викидаємо b
    assert "b" not in cache
    assert cache.keys() == ["a", "c"]


def test_lru_counts_hits_and_misses():
    cache = LRUCache(1)
    cache.put("a", 1)
    assert cache.get("a") == 1
    assert cache.get("x", "немає") == "немає"
    assert (cache.hits, cache.misses) == (1, 1)


def test_lru_update_existing_key_keeps_size():
    cache = LRUCache(2)
    cache.put("a", 1)
    cache.put("a", 10)
    assert len(cache) == 1
    assert cache.get("a") == 10


def test_lru_capacity_must_be_positive():
    with pytest.raises(ValueError):
        LRUCache(0)

class _Node:
    __slots__ = ("children", "is_word")

    def __init__(self):
        self.children = {}      # літера -> _Node
        self.is_word = False


class Trie:
    """Префіксне дерево: слова зі спільним початком ділять одну гілку.

    Пошук слова і префікса — O(довжина слова), незалежно від кількості слів.
    """

    def __init__(self, words=()):
        self._root = _Node()
        self._size = 0
        for word in words:
            self.add(word)

    def add(self, word):
        node = self._root
        for letter in word:
            node = node.children.setdefault(letter, _Node())
        if not node.is_word:
            node.is_word = True
            self._size += 1

    def _find(self, prefix):
        node = self._root
        for letter in prefix:
            node = node.children.get(letter)
            if node is None:
                return None
        return node

    def __contains__(self, word):
        node = self._find(word)
        return node is not None and node.is_word

    def starts_with(self, prefix, limit=None):
        """Усі слова з цим префіксом в алфавітному порядку (не більше limit)."""
        node = self._find(prefix)
        if node is None:
            return []
        words = []
        self._collect(node, prefix, words, limit)
        return words

    def _collect(self, node, path, words, limit):
        """Обхід у глибину (рекурсія, урок 22); літери — за алфавітом."""
        if limit is not None and len(words) >= limit:
            return
        if node.is_word:
            words.append(path)
        for letter in sorted(node.children):
            self._collect(node.children[letter], path + letter, words, limit)

    def __len__(self):
        return self._size

    def __iter__(self):
        return iter(self.starts_with(""))

    def __repr__(self):
        return f"Trie({len(self)} слів)"

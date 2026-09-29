"""Архітектурний аудит Python-проєкту: хто кого імпортує, чи є цикли, які модулі — «вузли». Урок 51.

Лише стандартна бібліотека (ast): проєкт не треба встановлювати й запускати.

    python architecture_audit.py шлях/до/пакета [шлях/до/іншого/пакета ...]
    python architecture_audit.py ../../../module_5/lessons/lesson_50_ci_cd/news_hub/news_hub --mermaid

Що друкує:
- модулі з кількістю рядків, вхідними (fan-in) і вихідними (fan-out) залежностями;
- цикли імпортів (сильно зв'язані компоненти графа) — кандидати на переділ відповідальностей;
- з --mermaid — граф залежностей для сторінки чи README.
"""
import argparse
import ast
from collections import defaultdict
from pathlib import Path


def module_name(path: Path, root: Path) -> str:
    parts = list(path.relative_to(root.parent).with_suffix("").parts)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def collect(packages: list[Path]) -> tuple[dict[str, set[str]], dict[str, int]]:
    """Граф {модуль: {внутрішні модулі, які він імпортує}} і кількість рядків у кожному модулі."""
    files = {module_name(f, pkg): f for pkg in packages for f in pkg.rglob("*.py")
             if "migrations" not in f.parts and not f.name.startswith("test")}
    internal = set(files)
    graph: dict[str, set[str]] = defaultdict(set)
    lines: dict[str, int] = {}
    for name, path in files.items():
        source = path.read_text(encoding="utf-8")
        lines[name] = source.count("\n")
        package = name if path.name == "__init__.py" else name.rpartition(".")[0]
        for node in ast.walk(ast.parse(source)):
            targets: list[str] = []
            if isinstance(node, ast.Import):
                targets = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                base = node.module or ""
                if node.level:                                  # відносний імпорт: from ..db import x
                    anchor = package.split(".")[: len(package.split(".")) - node.level + 1]
                    base = ".".join(anchor + ([base] if base else []))
                # from pkg import module → залежність від module; from module import name → від module
                targets = [f"{base}.{alias.name}" if f"{base}.{alias.name}" in internal else base
                           for alias in node.names]
            for target in targets:
                while target and target not in internal:        # a.b.c → a.b → a: найближчий свій модуль
                    target = target.rpartition(".")[0]
                if target and target != name:
                    graph[name].add(target)
        graph.setdefault(name, set())
    return dict(graph), lines


def cycles(graph: dict[str, set[str]]) -> list[list[str]]:
    """Сильно зв'язані компоненти (алгоритм Тар'яна) з понад одним модулем — цикли імпортів."""
    index: dict[str, int] = {}
    low: dict[str, int] = {}
    stack: list[str] = []
    on_stack: set[str] = set()
    found: list[list[str]] = []
    counter = [0]

    def visit(node: str) -> None:
        index[node] = low[node] = counter[0]
        counter[0] += 1
        stack.append(node)
        on_stack.add(node)
        for nxt in graph.get(node, ()):
            if nxt not in index:
                visit(nxt)
                low[node] = min(low[node], low[nxt])
            elif nxt in on_stack:
                low[node] = min(low[node], index[nxt])
        if low[node] == index[node]:
            component = []
            while True:
                member = stack.pop()
                on_stack.discard(member)
                component.append(member)
                if member == node:
                    break
            if len(component) > 1:
                found.append(sorted(component))

    for node in sorted(graph):
        if node not in index:
            visit(node)
    return found


def mermaid(graph: dict[str, set[str]]) -> str:
    """Граф для Mermaid: id вузла — повне ім'я, підпис — коротке (або повне, якщо коротке не унікальне)."""
    names = {n for n in graph if "." in n}                  # без кореневих __init__ пакетів
    last: dict[str, int] = defaultdict(int)
    for name in names:
        last[name.rpartition(".")[2]] += 1

    def node(name: str) -> str:
        label = name.rpartition(".")[2]
        if last[label] > 1:                                 # urls у двох пакетах → hello_app/urls
            label = name.replace(".", "/")
        return f'{name.replace(".", "_")}["{label}"]'

    lines = ["graph LR"]
    for source in sorted(names):
        for target in sorted(graph[source] & names):
            lines.append(f"    {node(source)} --> {node(target)}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("packages", nargs="+", type=Path)
    parser.add_argument("--mermaid", action="store_true")
    args = parser.parse_args()
    graph, lines = collect([p.resolve() for p in args.packages])
    fan_in: dict[str, int] = defaultdict(int)
    for targets in graph.values():
        for target in targets:
            fan_in[target] += 1
    print(f"{'модуль':<34} {'рядків':>6} {'fan-in':>6} {'fan-out':>7}")
    for name in sorted(graph, key=lambda n: (-fan_in[n], n)):
        print(f"{name:<34} {lines[name]:>6} {fan_in[name]:>6} {len(graph[name]):>7}")
    found = cycles(graph)
    print("\nцикли імпортів:", found or "немає")
    if args.mermaid:
        print("\n" + mermaid(graph))


if __name__ == "__main__":
    main()

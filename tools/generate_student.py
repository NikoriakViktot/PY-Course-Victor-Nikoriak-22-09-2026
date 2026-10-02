#!/usr/bin/env python3
"""Студентські версії ноутбуків: без рішень і без клітинок викладача.

Майстер-ноутбук (з рішеннями) → `<назва>_student.ipynb` поруч:

- код між `# BEGIN SOLUTION` і `# END SOLUTION` прибирається в УСІХ клітинках коду (тег не потрібен);
  на його місці — `# YOUR CODE HERE` з тим самим відступом, а всередині блоку (функція, цикл) ще й `pass`,
  щоб клітинка лишалась синтаксично правильною: студент бачить AssertionError вправи, а не SyntaxError;
- клітинки з тегом `instructor` видаляються повністю;
- клітинки з тегом `system` (Colab form-клітинка з `cellView: form`, напр. системна перевірка
  для студента) лишаються як є — не стрипаються, але так само позначають ноутбук як майстер-ноутбук;
- виводи й лічильники виконання очищаються (у виводах бувають відповіді);
- бейдж Colab і `metadata.lms` одразу виставляються для шляху студентського файлу
  (та сама логіка, що в `tools/sync_notebook_metadata.py`).

    python tools/generate_student.py                     # усі майстер-ноутбуки з рішеннями
    python tools/generate_student.py шлях/до/ноутбука.ipynb [...]
    python tools/generate_student.py --check             # CI: нічого не пише; exit 1, якщо версія застаріла,
                                                         # її немає або клітинка не компілюється

Майстер-ноутбук — будь-який ноутбук у module_*/ з маркерами рішень чи клітинками `instructor`,
крім самих `*_student.ipynb`. Студентські файли руками не редагують — лише цим скриптом.
"""
import argparse
import ast
import copy
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sync_notebook_metadata import (  # noqa: E402  (спільна логіка бейджа й metadata.lms)
    ROOT, build_lms, cell_source, dump_notebook, notebooks, sync_badge, sync_links,
)

PLACEHOLDER = "# YOUR CODE HERE"
BEGIN, END = "# BEGIN SOLUTION", "# END SOLUTION"
BLOCK = re.compile(r"^([ \t]*)# BEGIN SOLUTION[^\n]*\n(?:.*?\n)??[ \t]*# END SOLUTION[^\n]*(?:\n|\Z)", re.M | re.S)
TAG_INSTRUCTOR = "instructor"
TAG_SYSTEM = "system"          # Colab form-клітинка (cellView: form): лишається для студента, не стрипається,
                                # але все одно рахується як ознака майстер-ноутбука (is_master)
STUDENT_SUFFIX = "_student"


def strip_solutions(source: str, fill_blocks: bool = True) -> str:
    """Прибрати блоки рішень, зберігши відступ; `fill_blocks` — `pass` на місці відступленого блоку."""
    def replace(match: re.Match[str]) -> str:
        indent = match[1]
        before = source[:match.start()].rstrip("\n")
        previous = before.rsplit("\n", 1)[-1].strip() if before else ""
        text = "" if previous == PLACEHOLDER else f"{indent}{PLACEHOLDER}\n"
        if indent and fill_blocks:                   # тіло def / for / if не може бути порожнім
            text += f"{indent}pass\n"
        return text

    result = BLOCK.sub(replace, source)
    if BEGIN in result or END in result:
        raise ValueError(f"непарні маркери {BEGIN!r} / {END!r}")
    return result


def student_source(source: str) -> str:
    """Варіант без рішень, що компілюється: з `pass` (тіло функції) чи без (рішення всередині `{…}`)."""
    variants = [strip_solutions(source), strip_solutions(source, fill_blocks=False)]
    return next((v for v in variants if compiles(v)), variants[0])


def compiles(source: str) -> bool:
    if source.lstrip().startswith("%%"):
        return True
    code = "\n".join("" if line.lstrip().startswith(("%", "!")) else line for line in source.splitlines())
    try:
        compile(code, "cell", "exec", flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)   # Jupyter: await у клітинці
    except SyntaxError:
        return False
    return True


def is_master(nb: dict) -> bool:
    for cell in nb.get("cells", []):
        tags = cell.get("metadata", {}).get("tags", [])
        if TAG_INSTRUCTOR in tags or TAG_SYSTEM in tags:
            return True
        if cell.get("cell_type") == "code" and BEGIN in cell_source(cell):
            return True
    return False


def student_path(master: Path) -> Path:
    return master.with_name(master.stem + STUDENT_SUFFIX + master.suffix)


def make_student(nb: dict, rel: str) -> dict:
    """Студентська версія майстер-ноутбука; `rel` — шлях студентського файлу від кореня репозиторію."""
    student = copy.deepcopy(nb)
    cells = []
    for index, cell in enumerate(student.get("cells", [])):
        if TAG_INSTRUCTOR in cell.get("metadata", {}).get("tags", []):
            continue
        if cell.get("cell_type") == "code":
            try:
                text = student_source(cell_source(cell))
            except ValueError as exc:
                raise ValueError(f"клітинка {index}: {exc}") from None
            cell["source"] = text.splitlines(keepends=True)
            cell["outputs"] = []
            cell["execution_count"] = None
        cells.append(cell)
    student["cells"] = cells

    metadata = student.setdefault("metadata", {})
    metadata["lms"] = build_lms(rel, metadata.get("lms"))
    metadata.setdefault("colab", {}).setdefault("provenance", [])
    metadata["colab"]["include_colab_link"] = True
    sync_badge(student, rel)
    sync_links(student, rel, [])
    return student


def compile_errors(nb: dict) -> list[str]:
    """Клітинки коду, які не компілюються (магії IPython `%`, `!` пропускаємо; `await` у клітинці — дозволено)."""
    errors = []
    for index, cell in enumerate(nb.get("cells", [])):
        if cell.get("cell_type") != "code":
            continue
        text = cell_source(cell)
        if text.lstrip().startswith("%%"):
            continue
        code = "\n".join("" if line.lstrip().startswith(("%", "!")) else line for line in text.splitlines())
        try:
            compile(code, f"cell {index}", "exec", flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)   # Jupyter: await у клітинці
        except SyntaxError as exc:
            errors.append(f"клітинка {index}, рядок {exc.lineno}: {exc.msg}")
    return errors


def masters() -> list[Path]:
    found = []
    for path in notebooks():
        if path.stem.endswith(STUDENT_SUFFIX):
            continue
        if is_master(json.loads(path.read_text(encoding="utf-8"))):
            found.append(path)
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("notebooks", nargs="*", type=Path, help="майстер-ноутбуки (за замовчуванням — усі)")
    parser.add_argument("--check", action="store_true", help="не писати; exit 1, якщо щось застаріло чи зламане")
    args = parser.parse_args()

    paths = [p.resolve() for p in args.notebooks] or masters()
    problems, written = [], 0
    for master in paths:
        rel_master = master.relative_to(ROOT).as_posix()
        target = student_path(master)
        rel = target.relative_to(ROOT).as_posix()
        text = master.read_text(encoding="utf-8")
        try:
            student = make_student(json.loads(text), rel)
        except ValueError as exc:
            problems.append(f"{rel_master}: {exc}")
            continue
        problems += [f"{rel}: {e}" for e in compile_errors(student)]
        new_text = dump_notebook(student, text)
        current = target.read_text(encoding="utf-8") if target.exists() else None
        if current == new_text:
            continue
        if args.check:
            problems.append(f"{rel}: {'немає' if current is None else 'застарів'} — запусти tools/generate_student.py")
        else:
            target.write_text(new_text, encoding="utf-8")
            written += 1
            print(f"✅ {rel}")

    for problem in problems:
        print(f"❌ {problem}")
    if not args.check:
        print(f"майстер-ноутбуків: {len(paths)}, оновлено студентських: {written}")
    elif not problems:
        print(f"ok: {len(paths)} студентських ноутбуків актуальні")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())

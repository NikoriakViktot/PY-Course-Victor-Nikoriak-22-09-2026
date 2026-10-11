"""Тести tools/generate_student.py: python -m pytest tools -q"""
import pytest

from generate_student import compile_errors, is_master, make_student, strip_solutions, student_source

REL = "module_6/lessons/lesson_52_final_project/note_lesson_52_final_project_student.ipynb"


def code(source: str, **metadata: object) -> dict:
    return {"cell_type": "code", "metadata": dict(metadata), "source": source.splitlines(keepends=True),
            "outputs": [{"output_type": "stream", "name": "stdout", "text": ["42\n"]}], "execution_count": 3}


def markdown(source: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": source.splitlines(keepends=True)}


def test_function_body_keeps_indent_and_compiles() -> None:
    src = ("def fan_in(graph):\n"
           "    # YOUR CODE HERE\n"
           "    # BEGIN SOLUTION\n"
           "    return {n: 0 for n in graph}\n"
           "    # END SOLUTION\n"
           "\n"
           "assert fan_in({}) == {}\n")
    out = strip_solutions(src)
    assert out == "def fan_in(graph):\n    # YOUR CODE HERE\n    pass\n\nassert fan_in({}) == {}\n"
    compile(out, "cell", "exec")


def test_top_level_block_without_placeholder_gets_one() -> None:
    src = "x = 1\n# BEGIN SOLUTION\nfoundation = {x}\n# END SOLUTION\nprint(foundation)\n"
    assert strip_solutions(src) == "x = 1\n# YOUR CODE HERE\nprint(foundation)\n"


def test_several_blocks_and_block_at_end_of_cell() -> None:
    src = ("for x in xs:\n    # BEGIN SOLUTION\n    total += x\n    # END SOLUTION\n"
           "# YOUR CODE HERE\n# BEGIN SOLUTION\ny = 2\n# END SOLUTION")
    assert strip_solutions(src) == "for x in xs:\n    # YOUR CODE HERE\n    pass\n# YOUR CODE HERE\n"


def test_unbalanced_markers_are_an_error() -> None:
    with pytest.raises(ValueError, match="непарні"):
        strip_solutions("# BEGIN SOLUTION\nx = 1\n")


def test_make_student_strips_untagged_cells_drops_instructor_and_outputs() -> None:
    nb = {"metadata": {"lms": {"notebook_type": "notes"}},
          "cells": [markdown("# Урок"),
                    code("SECRET = 'відповідь'\n", tags=["instructor"]),
                    code("def f():\n    # BEGIN SOLUTION\n    return 1\n    # END SOLUTION\n"),
                    code("print(f())\n")]}
    assert is_master(nb)
    student = make_student(nb, REL)
    sources = ["".join(c["source"]) for c in student["cells"]]
    assert not any("SECRET" in s or "return 1" in s or "BEGIN SOLUTION" in s for s in sources)
    assert sources[0].startswith('<a href="https://colab.research.google.com/github/') and REL in sources[0]
    assert all(c["outputs"] == [] and c["execution_count"] is None for c in student["cells"] if c["cell_type"] == "code")
    assert student["metadata"]["lms"]["notebook_path"] == REL and student["metadata"]["lms"]["lesson_number"] == 52
    assert compile_errors(student) == []
    assert "SECRET" in "".join(nb["cells"][1]["source"])          # майстер не змінився


def test_compile_errors_skip_magics_and_report_real_ones() -> None:
    nb = {"cells": [code("!pip install x\n%timeit 1\nprint(1)\n"), code("%%bash\necho hi\n"),
                    code("r = await client.get('/')\n"), code("def f(:\n")]}
    assert compile_errors(nb) == ["клітинка 3, рядок 1: invalid syntax"]


def test_solution_inside_a_literal_gets_no_pass() -> None:
    src = "kinds = {\n    # YOUR CODE HERE\n    # BEGIN SOLUTION\n    'a': 1,\n    # END SOLUTION\n}\nassert kinds['a'] == 1\n"
    assert student_source(src) == "kinds = {\n    # YOUR CODE HERE\n}\nassert kinds['a'] == 1\n"
    body = "def f():\n    # BEGIN SOLUTION\n    return 1\n    # END SOLUTION\n"
    assert student_source(body) == "def f():\n    # YOUR CODE HERE\n    pass\n"

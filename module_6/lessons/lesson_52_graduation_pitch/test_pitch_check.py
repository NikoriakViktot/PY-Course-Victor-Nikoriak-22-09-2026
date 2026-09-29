"""Тести pitch_check.py: python -m pytest test_pitch_check.py"""
from pathlib import Path

from pitch_check import check, split_slides

HERE = Path(__file__).parent
SPEECH = " ".join(["слово"] * 60)                       # 60 слів ≈ 28 с виступу


def deck(*slides: str, front: str = "---\nmarp: true\n---\n") -> str:
    return front + "\n---\n".join(slides)


def slide(title: str, body: str = "текст", notes: str = SPEECH) -> str:
    return f"# {title}\n\n{body}\n\n<!-- {notes} -->\n"


GOOD = [slide(t) for t in ("Продукт", "Проблема", "Рішення", "Демо", "Чому зараз", "Ринок",
                           "Модель доходу", "Як це працює", "Що далі", "Прохання")]


def test_front_matter_notes_and_directives() -> None:
    slides = split_slides(deck("<!-- _paginate: false -->\n# Назва\n\n<!-- що скажу -->", "# Друга"))
    assert [s.title for s in slides] == ["Назва", "Друга"]
    assert slides[0].notes == "що скажу"                 # директива Marp — не нотатка
    assert slides[1].notes == ""


def test_good_deck_passes() -> None:
    assert check(deck(*GOOD)) == []


def test_example_deck_passes_and_template_does_not() -> None:
    assert check((HERE / "example_news_digest_deck.md").read_text(encoding="utf-8")) == []
    problems = check((HERE / "pitch_deck_template.md").read_text(encoding="utf-8"))
    assert any("заготовка" in p for p in problems)


def test_too_many_words_on_slide() -> None:
    wall = slide("Проблема", body=" ".join(["довгий"] * 60))
    problems = check(deck(GOOD[0], wall, *GOOD[2:]))
    assert problems == ["слайд 2 «Проблема»: 61 слів на слайді — перенеси в нотатки"]   # 60 + заголовок


def test_timing_slides_and_required_sections() -> None:
    short = [slide(t, notes="коротко") for t in ("Проблема", "Рішення", "Демо")]
    problems = check(deck(*short))
    assert "слайдів 3, треба 8–12" in problems
    assert any(p.startswith("виступ ≈ 0.0 хв") for p in problems)
    assert {"немає слайда «як це працює»", "немає слайда «далі»"} <= set(problems)


def test_placeholder_but_not_markdown_link() -> None:
    linked = slide("Прохання", body="[код](https://github.com/)")
    todo = slide("Прохання", body="TODO контакт")
    assert check(deck(*GOOD[:-1], linked)) == []
    assert check(deck(*GOOD[:-1], todo)) == ["слайд 10 «Прохання»: лишилась заготовка [..] чи TODO"]


def test_link_targets_are_not_words_on_slide() -> None:
    body = " ".join(["слово"] * 43) + " [Джерело](https://example.com/a/very/long/descriptive/source/path)"
    body += " ![](img/architecture-diagram-final-version.png) <https://github.com/some/long/repository/path>"
    assert check(deck(slide("Проблема", body=body), *GOOD[1:])) == []     # 43 + «Проблема» + «Джерело» = 45

"""Перевірка питч-деку в Markdown для Marp перед уроком 52.

    python pitch_check.py мій_дек.md

Слайди розділяє рядок `---`; текст у коментарях `<!-- … -->` — нотатки доповідача (те, що кажеш уголос),
крім директив Marp (`<!-- _paginate: false -->`). Скрипт перевіряє те, що легко виміряти:
кількість слайдів, обсяг тексту на слайді, час виступу за нотатками, обов'язкові розділи, забуті заготовки.
Чи переконливий дек — вирішують люди на уроці.
"""
import re
import sys
from dataclasses import dataclass
from pathlib import Path

WORDS_PER_MINUTE = 130            # темп виступу: спокійна мова, 120–150 слів за хвилину
MAX_MINUTES = 7.0                 # регламент уроку 52: 5–7 хвилин
MIN_MINUTES = 4.0
MIN_SLIDES, MAX_SLIDES = 8, 12    # правило 10/20/30 Гая Кавасакі: близько десяти слайдів
MAX_WORDS_ON_SLIDE = 45           # слайд читають за секунди; решта — у нотатках
REQUIRED = ("проблема", "рішення", "демо", "як це працює", "далі")

COMMENT = re.compile(r"<!--(.*?)-->", re.S)
DIRECTIVE = re.compile(r"^\s*_?[a-zA-Z]+\s*:")          # <!-- _class: lead -->, <!-- paginate: false -->
PLACEHOLDER = re.compile(r"\[[^\]]*\]\s*(?!\()|\bTODO\b")   # [текст] без посилання (…)
LINK = re.compile(r"!?\[([^\]]*)\]\([^)]*\)")             # [підпис](адреса), ![опис](картинка.png)
AUTOLINK = re.compile(r"<(?:https?|mailto):[^>]*>")


@dataclass
class Slide:
    title: str
    text: str
    notes: str


def split_slides(markdown: str) -> list[Slide]:
    """Markdown для Marp → слайди. Перший блок `--- … ---` — налаштування (front matter), не слайд."""
    body = re.sub(r"\A---\n.*?\n---\n", "", markdown, count=1, flags=re.S)
    slides = []
    for chunk in re.split(r"^---\s*$", body, flags=re.M):
        notes = " ".join(c.strip() for c in COMMENT.findall(chunk) if not DIRECTIVE.match(c))
        text = COMMENT.sub("", chunk).strip()
        if not text and not notes:
            continue
        title = next((line.lstrip("# ").strip() for line in text.splitlines() if line.startswith("#")), "")
        slides.append(Slide(title, text, notes))
    return slides


def words(text: str) -> int:
    return len(re.findall(r"[\w'’]+", text))


def check(markdown: str) -> list[str]:
    slides = split_slides(markdown)
    problems = []
    if not MIN_SLIDES <= len(slides) <= MAX_SLIDES:
        problems.append(f"слайдів {len(slides)}, треба {MIN_SLIDES}–{MAX_SLIDES}")
    for number, slide in enumerate(slides, 1):
        visible = AUTOLINK.sub(" ", LINK.sub(r"\1", slide.text))   # на слайді видно підпис, а не адресу
        visible = re.sub(r"[|`*>#-]", " ", visible)
        if words(visible) > MAX_WORDS_ON_SLIDE:
            problems.append(f"слайд {number} «{slide.title}»: {words(visible)} слів на слайді — перенеси в нотатки")
        if PLACEHOLDER.search(slide.text + " " + slide.notes):
            problems.append(f"слайд {number} «{slide.title}»: лишилась заготовка [..] чи TODO")
        if not slide.notes:
            problems.append(f"слайд {number} «{slide.title}»: немає нотаток — що ти скажеш?")
    minutes = sum(words(s.notes) for s in slides) / WORDS_PER_MINUTE
    if not MIN_MINUTES <= minutes <= MAX_MINUTES:
        problems.append(f"виступ ≈ {minutes:.1f} хв за нотатками, треба {MIN_MINUTES:.0f}–{MAX_MINUTES:.0f}")
    titles = " | ".join(s.title.lower() for s in slides)
    for section in REQUIRED:
        if section not in titles:
            problems.append(f"немає слайда «{section}»")
    return problems


def main() -> int:
    path = Path(sys.argv[1])
    markdown = path.read_text(encoding="utf-8")
    slides = split_slides(markdown)
    minutes = sum(words(s.notes) for s in slides) / WORDS_PER_MINUTE
    print(f"{path.name}: {len(slides)} слайдів, виступ ≈ {minutes:.1f} хв")
    problems = check(markdown)
    for problem in problems:
        print("  ✗", problem)
    print("  ✓ готово до репетиції" if not problems else f"  {len(problems)} зауважень")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())

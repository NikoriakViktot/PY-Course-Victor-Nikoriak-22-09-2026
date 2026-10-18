"""MkDocs-хук: український стемер для пошуку Material for MkDocs.

`search.lang: uk` у mkdocs.yml не спрацює: lunr.js не має української, і mkdocs
тихо підміняє її на `ru`. Тому в mkdocs.yml стоїть `lang: en`, а цей хук після збірки:

1. кладе `lunr.uk.js` туди, звідки воркер пошуку підвантажує мовні модулі
   (`assets/javascripts/lunr/min/lunr.<мова>.min.js`);
2. дописує `uk` у `config.lang` пошукового індексу — воркер вмикає
   `lunr.multiLanguage("en", "uk")`: українські слова стемить `lunr.uk`,
   англійські терміни (FileNotFoundError, json.load) — англійський стемер.

Індекс будується в браузері, тож той самий стемер обробляє і текст сторінок, і запит.
Стемер працює, лише якщо в `search.pipeline` є `stemmer` (див. mkdocs.yml).
"""
import json
import shutil
from pathlib import Path

from mkdocs.plugins import event_priority

SOURCE = Path(__file__).with_name("lunr.uk.js")
LANG = "uk"


@event_priority(-100)  # після search-плагіна: він пише search_index.json у своєму on_post_build
def on_post_build(config, **kwargs):
    site = Path(config["site_dir"])
    index_path = site / "search" / "search_index.json"
    if not index_path.exists():
        return

    target = site / "assets" / "javascripts" / "lunr" / "min" / f"lunr.{LANG}.min.js"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SOURCE, target)

    index = json.loads(index_path.read_text(encoding="utf-8"))
    langs = index["config"]["lang"]
    if LANG not in langs:
        langs.append(LANG)
    index_path.write_text(json.dumps(index, separators=(",", ":")), encoding="utf-8")

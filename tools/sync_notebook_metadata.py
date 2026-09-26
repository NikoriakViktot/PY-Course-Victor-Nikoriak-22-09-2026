#!/usr/bin/env python3
"""Keep course notebooks' metadata in sync with where they live in the repo.

Why: the "Open in Colab" badge and metadata.lms store the notebook's path.
When a notebook is moved (or copied from another repo) they keep pointing
at the old place, and Colab fails with "Could not find <file>.ipynb".

For every notebook under module_*/ (course materials only, not assignments/):
  * first cell = "Open in Colab" badge for this repo / branch / path
  * metadata.colab.include_colab_link = true
  * metadata.lms rebuilt from the location:
      module_N/lessons/lesson_NN_<slug>/...  -> v5.0 lesson NN of module N
      module_N/bonus/<slug>/...              -> bonus lesson of module N (no number;
                                                title from "bonus" in lessons_v5.json)
      module_N/docs/...                      -> reference notebook of module N
  * relative links in markdown cells -> absolute URLs (they don't resolve in Colab)

For docs/**/*.md:
  * links to files of this repo on GitHub must point at existing files
  * each GitHub link to a notebook gets an "Open in Colab" badge next to it

Sources of truth: course.json (repo, branch, modules), tools/lessons_v5.json
(stream, lesson titles), mkdocs.yml (site_url).

Usage:
  python tools/sync_notebook_metadata.py          # fix files in place
  python tools/sync_notebook_metadata.py --check  # report only, exit 1 on drift (CI)
"""
import argparse
import copy
import json
import posixpath
import re
import sys
from pathlib import Path, PurePosixPath
from urllib.parse import quote, unquote

ROOT = Path(__file__).resolve().parent.parent

COURSE = json.loads((ROOT / "course.json").read_text(encoding="utf-8"))
V5 = json.loads((ROOT / "tools" / "lessons_v5.json").read_text(encoding="utf-8"))
SITE_URL = re.search(r"^site_url:\s*(\S+)", (ROOT / "mkdocs.yml").read_text(encoding="utf-8"), re.M)[1]
SITE_URL = SITE_URL.rstrip("/") + "/"

REPO = COURSE["streams"][0]["repo"]
BRANCH = COURSE["streams"][0]["branch"]
MODULES = {m["number"]: m for m in COURSE["modules"]}

BADGE_IMG = "https://colab.research.google.com/assets/colab-badge.svg"
BADGE_HTML = '<a href="{url}" target="_parent"><img src="' + BADGE_IMG + '" alt="Open In Colab"/></a>'
BADGE_MD = "[![Open In Colab](" + BADGE_IMG + ")]({url})"
BADGE_CELL_ID = "view-in-github"

LESSON_DIR_RE = re.compile(r"^module_(\d+)/lessons/lesson_(\d+)_([a-z0-9_]+)/")
MODULE_DOCS_RE = re.compile(r"^module_(\d+)/docs/")
BONUS_DIR_RE = re.compile(r"^module_(\d+)/bonus/([a-z0-9_]+)/")
MD_LINK_RE = re.compile(r"(!?)\[([^\]]*)\]\(([^)\s]+)\)")
HTML_LINK_RE = re.compile(r'((?:href|src)=")([^"]+)(")')
SCHEME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")
IMAGE_EXT = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp")

REPO_URL_RE = re.escape(REPO)
BRANCH_URL_RE = re.escape(BRANCH)
DOCS_REPO_LINK_RE = re.compile(
    r"https://github\.com/" + REPO_URL_RE + r"/(?:blob|tree)/" + BRANCH_URL_RE + r"/([^)\s\"'#?]+)"
    r"|https://colab\.research\.google\.com/github/" + REPO_URL_RE + r"/blob/" + BRANCH_URL_RE + r"/([^)\s\"'#?]+)",
    re.I,
)
DOCS_NOTEBOOK_LINK_RE = re.compile(
    r"(\[[^\]]*\]\(https://github\.com/" + REPO_URL_RE + r"/blob/" + BRANCH_URL_RE + r"/([^)\s]+\.ipynb)\))"
    r"( \[!\[Open In Colab\]\([^)]*\)\]\([^)]*\))?",
    re.I,
)


def colab_url(path):
    return f"https://colab.research.google.com/github/{REPO}/blob/{BRANCH}/{quote(path)}"


def github_url(path, kind="blob"):
    return f"https://github.com/{REPO}/{kind}/{BRANCH}/{quote(path)}"


def raw_url(path):
    return f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/{quote(path)}"


def site_page_url(docs_path):
    """docs/X/README.md -> <site>/X/, docs/X/Y.md -> <site>/X/Y/ (mkdocs directory URLs)."""
    p = PurePosixPath(docs_path).relative_to("docs")
    if p.name in ("README.md", "index.md"):
        page = "" if str(p.parent) == "." else f"{p.parent}/"
    else:
        page = f"{p.with_suffix('')}/"
    return SITE_URL + quote(page)


def cell_source(cell):
    src = cell.get("source", "")
    return "".join(src) if isinstance(src, list) else src


def set_cell_source(cell, text):
    cell["source"] = text.splitlines(keepends=True) if isinstance(cell.get("source"), list) else text


def build_lms(rel, old):
    old = old if isinstance(old, dict) else {}
    name = PurePosixPath(rel).name
    lesson = LESSON_DIR_RE.match(rel)
    docs = MODULE_DOCS_RE.match(rel)
    bonus = BONUS_DIR_RE.match(rel)
    if lesson:
        module_number, lesson_number, slug = int(lesson[1]), int(lesson[2]), lesson[3]
        info = V5["lessons"].get(str(lesson_number))
        if info is None:
            raise ValueError(f"lesson {lesson_number} is not in tools/lessons_v5.json")
        title = info["title"]
        default_type = "notes" if name.startswith(("note_", "notes_")) else "lesson"
        notebook_type = old.get("notebook_type") or default_type
    elif bonus:
        module_number, lesson_number, slug = int(bonus[1]), None, bonus[2]
        info = V5.get("bonus", {}).get(slug)
        if info is None:
            raise ValueError(f"bonus lesson '{slug}' is not in tools/lessons_v5.json (\"bonus\")")
        if info["module"] != module_number:
            raise ValueError(f"bonus lesson '{slug}' belongs to module {info['module']} (tools/lessons_v5.json)")
        title = info["title"]
        default_type = "notes" if name.startswith(("note_", "notes_")) else "lesson"
        notebook_type = old.get("notebook_type") or default_type
    elif docs:
        module_number, lesson_number = int(docs[1]), None
        stem = PurePosixPath(rel).stem
        slug = old.get("lesson_slug") or stem
        title = old.get("lesson_title") or stem
        notebook_type = "docs"
    else:
        raise ValueError("notebook must live in module_N/lessons/lesson_NN_<slug>/, module_N/bonus/<slug>/ or module_N/docs/")

    module = MODULES.get(module_number)
    if module is None:
        raise ValueError(f"module {module_number} is not in course.json")
    if lesson_number is not None and lesson_number not in module["lessons"]:
        raise ValueError(f"lesson {lesson_number} does not belong to module {module_number} (course.json)")

    return {
        "course": V5["course"],
        "stream": V5["stream"],
        "module_number": module_number,
        "module_slug": module["slug"],
        "module_title": module["title"],
        "lesson_number": lesson_number,
        "lesson_slug": slug,
        "lesson_title": title,
        "notebook_type": notebook_type,
        "notebook_path": rel,
        "version": old.get("version", 1),
    }


def sync_badge(nb, rel):
    cells = nb.setdefault("cells", [])
    badge = BADGE_HTML.format(url=colab_url(rel))
    idx = next(
        (i for i, c in enumerate(cells)
         if c.get("metadata", {}).get("id") == BADGE_CELL_ID or BADGE_IMG in cell_source(c)),
        None,
    )
    if idx is None:
        cell = {"cell_type": "markdown"}
        if any("id" in c for c in cells):
            cell["id"] = BADGE_CELL_ID
        cell["metadata"] = {"id": BADGE_CELL_ID, "colab_type": "text"}
        cell["source"] = [badge]
        cells.insert(0, cell)
        return
    cell = cells.pop(idx)
    cell["cell_type"] = "markdown"
    cell.setdefault("metadata", {}).update({"id": BADGE_CELL_ID, "colab_type": "text"})
    cell["source"] = [badge]
    cells.insert(0, cell)


def absolute_link(url, nb_dir, warnings):
    """Relative link inside a notebook -> absolute URL, or None to keep it as is."""
    if SCHEME_RE.match(url) or url.startswith(("#", "/")):
        return None
    path, sep, anchor = url.partition("#")
    if not path:
        return None
    path = unquote(path)
    candidates = [posixpath.normpath(posixpath.join(nb_dir, path))]
    stripped = re.sub(r"^(\.\./)+", "", path)
    if stripped != path:
        # e.g. "../../00_getting_started/x.md" written with the wrong depth
        candidates += ["docs/" + stripped, stripped]
    target = next((c for c in candidates if not c.startswith("..") and (ROOT / c).exists()), None)
    if target is None:
        warnings.append(f"cannot resolve relative link {url!r}")
        return None
    if target.startswith("docs/") and target.endswith(".md"):
        new = site_page_url(target)
    elif target.endswith(".ipynb"):
        new = colab_url(target)
    elif (ROOT / target).is_dir():
        new = github_url(target, "tree")
    elif target.lower().endswith(IMAGE_EXT):
        new = raw_url(target)
    else:
        new = github_url(target)
    return new + (sep + anchor if anchor else "")


def sync_links(nb, rel, warnings):
    nb_dir = posixpath.dirname(rel)

    def md_sub(m):
        new = absolute_link(m[3], nb_dir, warnings)
        return m[0] if new is None else f"{m[1]}[{m[2]}]({new})"

    def html_sub(m):
        new = absolute_link(m[2], nb_dir, warnings)
        return m[0] if new is None else f"{m[1]}{new}{m[3]}"

    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "markdown":
            continue
        text = cell_source(cell)
        new_text = HTML_LINK_RE.sub(html_sub, MD_LINK_RE.sub(md_sub, text))
        if new_text != text:
            set_cell_source(cell, new_text)


def sync_notebook(path):
    """Return (original_text, original_json, synced_json, warnings)."""
    rel = path.relative_to(ROOT).as_posix()
    text = path.read_bytes().decode("utf-8")
    original = json.loads(text)
    nb = copy.deepcopy(original)
    warnings = []

    metadata = nb.setdefault("metadata", {})
    metadata["lms"] = build_lms(rel, metadata.get("lms"))
    colab = metadata.setdefault("colab", {})
    colab.setdefault("provenance", [])
    colab["include_colab_link"] = True
    sync_badge(nb, rel)
    sync_links(nb, rel, warnings)
    return text, original, nb, warnings


def dump_notebook(nb, like_text):
    text = json.dumps(nb, indent=1, ensure_ascii=False)
    return text + "\n" if like_text.endswith("\n") else text


def sync_doc(path, errors):
    """Return (text, synced_text) of a docs page; record links to missing files in errors."""
    rel = path.relative_to(ROOT).as_posix()
    text = path.read_bytes().decode("utf-8")

    for m in DOCS_REPO_LINK_RE.finditer(text):
        target = unquote((m[1] or m[2]).rstrip("/"))
        if not (ROOT / target).exists():
            errors.append(f"{rel}: link to missing file {target}")

    def badge_sub(m):
        return m[1] + " " + BADGE_MD.format(url=colab_url(unquote(m[2])))

    return text, DOCS_NOTEBOOK_LINK_RE.sub(badge_sub, text)


def notebooks():
    for path in sorted(ROOT.glob("module_*/**/*.ipynb")):
        if ".ipynb_checkpoints" not in path.parts:
            yield path


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="do not write; exit 1 if anything is out of sync")
    args = parser.parse_args()

    drift, errors = [], []

    for path in notebooks():
        rel = path.relative_to(ROOT).as_posix()
        try:
            text, original, nb, warnings = sync_notebook(path)
        except (ValueError, json.JSONDecodeError) as exc:
            errors.append(f"{rel}: {exc}")
            continue
        for w in warnings:
            print(f"warning: {rel}: {w}")
        if nb != original:
            drift.append(rel)
            if not args.check:
                path.write_bytes(dump_notebook(nb, text).encode("utf-8"))

    for path in sorted((ROOT / "docs").glob("**/*.md")):
        text, new_text = sync_doc(path, errors)
        if new_text != text:
            drift.append(path.relative_to(ROOT).as_posix())
            if not args.check:
                path.write_bytes(new_text.encode("utf-8"))

    verb = "out of sync" if args.check else "updated"
    for rel in drift:
        print(f"{verb}: {rel}")
    for err in errors:
        print(f"error: {err}")

    if args.check and drift:
        print(f"\n{len(drift)} file(s) out of sync — run: python tools/sync_notebook_metadata.py")
    if errors or (args.check and drift):
        return 1
    print(f"ok: {len(drift)} file(s) {verb}" if drift else "ok: everything in sync")
    return 0


if __name__ == "__main__":
    sys.exit(main())

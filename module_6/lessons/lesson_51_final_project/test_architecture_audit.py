"""Тести architecture_audit.py на крихітних пакетах у tmp_path: python -m pytest test_architecture_audit.py"""
from pathlib import Path

from architecture_audit import collect, cycles, mermaid


def make_package(root: Path, files: dict[str, str]) -> Path:
    for name, source in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(source, encoding="utf-8")
    return root / next(iter(files)).split("/")[0]


def test_absolute_relative_and_submodule_imports(tmp_path: Path) -> None:
    pkg = make_package(tmp_path, {
        "app/__init__.py": "",
        "app/db.py": "import sqlalchemy\n",                    # чужий пакет — не ребро
        "app/models.py": "from .db import Base\n",
        "app/api.py": "from app import models\nfrom app.db import Base\n",
        "app/sub/__init__.py": "",
        "app/sub/views.py": "from ..models import Note\nimport app.db\n",
    })
    graph, lines = collect([pkg])
    assert graph["app.models"] == {"app.db"}
    assert graph["app.api"] == {"app.models", "app.db"}        # from app import models → модуль models
    assert graph["app.sub.views"] == {"app.models", "app.db"}  # ..models з app/sub/ → app.models
    assert graph["app.db"] == set()
    assert lines["app.api"] == 2
    assert cycles(graph) == []


def test_cycle_is_found(tmp_path: Path) -> None:
    pkg = make_package(tmp_path, {
        "shop/__init__.py": "",
        "shop/orders.py": "from shop.users import User\n",
        "shop/users.py": "from shop.payments import pay\n",
        "shop/payments.py": "from shop.orders import Order\n",
        "shop/utils.py": "from shop.orders import Order\n",   # залежить від циклу, але не в ньому
    })
    graph, _ = collect([pkg])
    assert cycles(graph) == [["shop.orders", "shop.payments", "shop.users"]]


def test_tests_and_migrations_are_skipped(tmp_path: Path) -> None:
    pkg = make_package(tmp_path, {
        "app/__init__.py": "",
        "app/models.py": "",
        "app/tests.py": "from app.models import Note\n",
        "app/migrations/0001_initial.py": "from app.models import Note\n",
    })
    graph, _ = collect([pkg])
    assert set(graph) == {"app", "app.models"}


def test_mermaid_disambiguates_same_short_names(tmp_path: Path) -> None:
    web = make_package(tmp_path, {"web/__init__.py": "", "web/urls.py": "from web import views\n",
                                  "web/views.py": ""})
    project = make_package(tmp_path, {"project/__init__.py": "", "project/urls.py": "import web.urls\n"})
    graph, _ = collect([web, project])
    text = mermaid(graph)
    assert 'project_urls["project/urls"] --> web_urls["web/urls"]' in text
    assert 'web_urls["web/urls"] --> web_views["views"]' in text

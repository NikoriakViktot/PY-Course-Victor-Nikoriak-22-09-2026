"""Урок 44: тести архітектури — шари, правила доступу, CBV, кількість запитів, DATABASE_URL.

    python manage.py test hello_app.tests_architecture
    DATABASE_URL=postgres://notes_user:notes_pass@localhost:5432/notes_db python manage.py test   # на PostgreSQL
"""
import ast
import shutil
import tempfile
from decimal import Decimal
from pathlib import Path

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext

from hello_project.database import database_from_url

from . import selectors, services, views
from .models import Notebook

APP = Path(__file__).resolve().parent


# ─────────────────────────────────────────────────────────────────────────────
# 1. Шари: у views.py і api.py немає власних запитів до бази
# ─────────────────────────────────────────────────────────────────────────────

def orm_in_transport_layer(path: Path) -> list[str]:
    """Порушення правила «view не робить ORM»: Model.objects.… (крім .none()), Q(…),
    get_object_or_404(Модель, …) — правило доступу мало б жити в selectors."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    problems = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr == "objects":
            problems.append(f"{path.name}:{node.lineno} .objects")
        elif isinstance(node, ast.Name) and node.id == "Q":
            problems.append(f"{path.name}:{node.lineno} Q(...)")
        elif (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
              and node.func.id == "get_object_or_404" and isinstance(node.args[0], ast.Name)):
            problems.append(f"{path.name}:{node.lineno} get_object_or_404({node.args[0].id}, ...)")
    # Model.objects.none() — порожній QuerySet без запиту (поле серіалізатора, схема OpenAPI)
    none_calls = {f"{path.name}:{node.lineno} .objects" for node in ast.walk(tree)
                  if isinstance(node, ast.Attribute) and node.attr == "none"
                  and isinstance(node.value, ast.Attribute) and node.value.attr == "objects"}
    return [problem for problem in problems if problem not in none_calls]


class ThinTransportLayerTests(TestCase):
    def test_views_and_api_have_no_orm(self):
        for name in ("views.py", "api.py"):
            with self.subTest(name):
                self.assertEqual(orm_in_transport_layer(APP / name), [])

    def test_checker_finds_violations(self):
        """Перевірка перевірки: на коді уроку 40 правило знайшло б порушення."""
        sample = Path(tempfile.mkdtemp()) / "tests_architecture_sample.py"
        sample.write_text("def v(request, pk):\n"
                          "    get_object_or_404(Note, pk=pk)\n"
                          "    Tag.objects.get(id=1)\n"
                          "    Note.objects.filter(Q(user=request.user))\n"
                          "    Note.objects.none()\n", encoding="utf-8")
        try:
            self.assertEqual(orm_in_transport_layer(sample), [
                "tests_architecture_sample.py:2 get_object_or_404(Note, ...)",
                "tests_architecture_sample.py:3 .objects",
                "tests_architecture_sample.py:4 .objects",
                "tests_architecture_sample.py:4 Q(...)",
            ])
        finally:
            shutil.rmtree(sample.parent)


# ─────────────────────────────────────────────────────────────────────────────
# 2. Правила доступу — selectors, без HTTP
# ─────────────────────────────────────────────────────────────────────────────

class AccessRuleTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user("owner", password="pass-12345")
        self.ann = User.objects.create_user("ann", password="pass-12345")
        self.bob = User.objects.create_user("bob", password="pass-12345")
        self.stranger = User.objects.create_user("stranger", password="pass-12345")

    def test_list_shared_with_two_users_is_returned_once(self):
        """M2M у фільтрі з OR: без distinct() — рядок на кожного, з ким поділено."""
        todo = services.create_todo_list(user=self.owner, title="Ремонт")
        shop = services.create_shopping_list(user=self.owner, title="Будмагазин")
        for username in ("ann", "bob"):
            services.share_todo_list(todo, username)
            services.share_shopping_list(shop, username)
        self.assertEqual(list(selectors.todo_lists_visible_to(self.owner)), [todo])
        self.assertEqual(selectors.get_todo_list_detail(self.owner, todo.pk), todo)
        self.assertEqual(selectors.get_shopping_list_detail(self.owner, shop.pk), shop)
        self.client.force_login(self.owner)
        for url in (f"/todo/{todo.pk}/", f"/todo/{todo.pk}/edit/", f"/shopping/{shop.pk}/", f"/shopping/{shop.pk}/edit/"):
            with self.subTest(url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_every_listed_shopping_list_opens(self):
        """Що видно в списку, те відкривається: одне правило доступу для списку й сторінки."""
        group = services.create_group(name="Сім'я", creator=self.owner)
        services.add_user_to_group(group, "ann")
        own = services.create_shopping_list(user=self.ann, title="Своє")
        family = services.create_shopping_list(user=self.owner, title="На тиждень", group=group)
        shared = services.create_shopping_list(user=self.bob, title="Від Боба")
        services.share_shopping_list(shared, "ann")
        listed = [*selectors.get_user_shopping_lists(self.ann), *selectors.get_shared_shopping_lists(self.ann)]
        self.assertEqual({sl.title for sl in listed}, {"Своє", "На тиждень", "Від Боба"})
        for sl in listed:
            with self.subTest(sl.title):
                self.assertIsNotNone(selectors.get_shopping_list_detail(self.ann, sl.pk))
        self.assertIsNone(selectors.get_shopping_list_detail(self.stranger, family.pk))
        self.assertIsNone(selectors.get_shopping_list_detail(self.stranger, own.pk))

    def test_group_member_opens_list_but_cannot_edit(self):
        group = services.create_group(name="Сім'я", creator=self.owner)
        services.add_user_to_group(group, "ann")
        family = services.create_shopping_list(user=self.owner, title="На тиждень", group=group)
        self.client.force_login(self.ann)
        self.assertEqual(self.client.get(f"/shopping/{family.pk}/").status_code, 200)
        response = self.client.post(f"/shopping/{family.pk}/edit/", {"title": "Зламано"})
        self.assertRedirects(response, f"/shopping/{family.pk}/")
        family.refresh_from_db()
        self.assertEqual(family.title, "На тиждень")
        self.client.force_login(self.stranger)
        self.assertEqual(self.client.get(f"/shopping/{family.pk}/").status_code, 404)

    def test_items_follow_their_list(self):
        todo = services.create_todo_list(user=self.owner, title="Ремонт")
        services.share_todo_list(todo, "ann")
        item = services.add_todo_item(todo, text="Купити фарбу")
        self.client.force_login(self.stranger)
        self.assertEqual(self.client.post(f"/todo/items/{item.pk}/toggle/").status_code, 404)
        self.client.force_login(self.ann)
        self.client.post(f"/todo/items/{item.pk}/toggle/")
        item.refresh_from_db()
        self.assertTrue(item.is_done)                                   # поділений — відмічає
        self.assertEqual(self.client.post(f"/todo/items/{item.pk}/delete/").status_code, 404)   # видаляє лише автор

    def test_pending_total_is_computed_by_database(self):
        shop = services.create_shopping_list(user=self.owner, title="Базар")
        services.add_shop_item(shop, name="Яблука", quantity=Decimal("2"), estimated_price=Decimal("30"))
        services.add_shop_item(shop, name="Хліб", quantity=Decimal("1"), estimated_price=Decimal("25.50"))
        bought = services.add_shop_item(shop, name="Сир", quantity=Decimal("1"), estimated_price=Decimal("200"))
        services.add_shop_item(shop, name="Сіль")                        # без ціни — не рахується
        services.toggle_shop_item_purchased(bought)
        self.assertEqual(selectors.get_shopping_list_detail(self.owner, shop.pk).pending_total, Decimal("85.50"))

    def test_group_member_list_contains_only_members(self):
        group = services.create_group(name="Сім'я", creator=self.owner)
        self.assertIsNone(selectors.get_group_member(group, self.stranger.pk))
        self.assertIsNone(selectors.get_group_member(group, "не число"))
        self.assertEqual(selectors.get_group_member(group, self.owner.pk), self.owner)


# ─────────────────────────────────────────────────────────────────────────────
# 3. Class-based views
# ─────────────────────────────────────────────────────────────────────────────

class ClassBasedViewTests(TestCase):
    def setUp(self):
        self.olena = User.objects.create_user("olena", password="pass-12345")
        self.ann = User.objects.create_user("ann", password="pass-12345")
        self.client.force_login(self.olena)

    def test_login_check_comes_first_in_mro(self):
        mro = views.NoteUpdateView.__mro__
        self.assertLess(mro.index(LoginRequiredMixin), mro.index(views.OwnerRequiredMixin))

    def test_anonymous_is_redirected_before_any_query(self):
        """setup() виконується до dispatch(): якби фільтри читались там, анонім дійшов би до бази."""
        self.client.logout()
        with self.assertNumQueries(0):
            response = self.client.get("/notes/", {"tag": 1, "notebook": 1, "q": "план"})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response["Location"].startswith("/accounts/login/?next=/notes/"))

    def test_group_member_edit_redirects_with_message(self):
        group = services.create_group(name="Команда", creator=self.olena)
        services.add_user_to_group(group, "ann")
        note = services.create_note(user=self.olena, title="Спільна", group=group)
        self.client.force_login(self.ann)
        response = self.client.post(f"/notes/{note.pk}/edit/", {"title": "Зламано", "priority": "1"}, follow=True)
        self.assertRedirects(response, f"/notes/{note.pk}/")
        self.assertContains(response, "Ти не можеш редагувати нотатку іншого користувача.")
        note.refresh_from_db()
        self.assertEqual(note.title, "Спільна")

    def test_update_keeps_tags_and_pin(self):
        note = services.create_note(user=self.olena, title="Стара назва", is_pinned=True)
        response = self.client.post(f"/notes/{note.pk}/edit/", {"title": "Нова назва", "priority": "3",
                                                                 "is_pinned": "on"})
        self.assertRedirects(response, f"/notes/{note.pk}/")
        note.refresh_from_db()
        self.assertEqual((note.title, note.priority, note.is_pinned), ("Нова назва", 3, True))

    def test_notebook_description_is_saved_by_service(self):
        self.client.post("/notebooks/new/", {"title": "Робота", "description": "Задачі по роботі",
                                             "color": "#4A90E2"})
        self.assertEqual(Notebook.objects.get(title="Робота").description, "Задачі по роботі")

    def test_notebook_delete_counts_archived_notes_too(self):
        notebook = services.create_notebook(user=self.olena, title="Архів")
        services.create_note(user=self.olena, title="Жива", notebook=notebook)
        archived = services.create_note(user=self.olena, title="Стара", notebook=notebook)
        services.archive_note(archived)
        self.assertEqual(self.client.get(f"/notebooks/{notebook.pk}/delete/").context["note_count"], 2)

    def test_tag_next_only_to_this_site(self):
        for next_url, expected in (("/notebooks/", "/notebooks/"), ("https://evil.example/phish", "/notes/new/"),
                                   ("//evil.example", "/notes/new/")):
            with self.subTest(next_url):
                response = self.client.post(f"/tags/new/?next={next_url}", {"name": "робота", "color": "#808080"})
                self.assertRedirects(response, expected, fetch_redirect_response=False)

    def test_foreign_objects_are_404(self):
        other = User.objects.create_user("other", password="pass-12345")
        note = services.create_note(user=other, title="Чужа")
        notebook = services.create_notebook(user=other, title="Чужий")
        for url in (f"/notes/{note.pk}/", f"/notes/{note.pk}/edit/", f"/notes/{note.pk}/delete/",
                    f"/notebooks/{notebook.pk}/edit/", f"/notebooks/{notebook.pk}/delete/"):
            with self.subTest(url):
                self.assertEqual(self.client.get(url).status_code, 404)


# ─────────────────────────────────────────────────────────────────────────────
# 4. Кількість запитів не росте разом з даними (N+1 не з'являється)
# ─────────────────────────────────────────────────────────────────────────────

class QueryCountTests(TestCase):
    def queries_for(self, url_for, amount):
        user = User.objects.create_user(f"user{User.objects.count()}", password="pass-12345")
        notebook = services.create_notebook(user=user, title="Робота")
        tag_a, _ = services.create_or_get_tag(user=user, name="a")
        tag_b, _ = services.create_or_get_tag(user=user, name="b")
        shop = services.create_shopping_list(user=user, title="Базар")
        for i in range(amount):
            services.create_note(user=user, title=f"Нотатка {i}", notebook=notebook, tag_ids=[tag_a.id, tag_b.id])
            services.add_shop_item(shop, name=f"Товар {i}", estimated_price=Decimal("10"))
        self.client.force_login(user)
        url = url_for(shop)
        with CaptureQueriesContext(connection) as queries:
            self.assertEqual(self.client.get(url).status_code, 200)
        return len(queries)

    def test_pages_do_not_grow_with_data(self):
        for name, url_for in (("notes", lambda shop: "/notes/"), ("notebooks", lambda shop: "/notebooks/"),
                              ("shopping", lambda shop: f"/shopping/{shop.pk}/")):
            with self.subTest(name):
                self.assertEqual(self.queries_for(url_for, 3), self.queries_for(url_for, 30))


# ─────────────────────────────────────────────────────────────────────────────
# 5. DATABASE_URL
# ─────────────────────────────────────────────────────────────────────────────

class DatabaseUrlTests(TestCase):
    base = Path("/project")

    def test_no_url_is_sqlite(self):
        self.assertEqual(database_from_url(None, base_dir=self.base),
                         {"ENGINE": "django.db.backends.sqlite3", "NAME": self.base / "db.sqlite3"})

    def test_postgres_url(self):
        config = database_from_url("postgres://notes_user:p%40ss%3Aword@db.local:5433/notes_db?sslmode=require",
                                   base_dir=self.base)
        self.assertEqual(config["ENGINE"], "django.db.backends.postgresql")
        self.assertEqual((config["NAME"], config["USER"], config["PASSWORD"], config["HOST"], config["PORT"]),
                         ("notes_db", "notes_user", "p@ss:word", "db.local", "5433"))
        self.assertEqual(config["OPTIONS"], {"sslmode": "require"})

    def test_unknown_scheme_is_an_error(self):
        with self.assertRaisesMessage(ValueError, "mysql"):
            database_from_url("mysql://u:p@h/db", base_dir=self.base)

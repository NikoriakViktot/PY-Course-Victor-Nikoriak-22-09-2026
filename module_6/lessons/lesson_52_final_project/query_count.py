"""Скільки SQL-запитів робить кожна сторінка проєкту нотаток при 10 і 40 записах. Урок 51.

N+1 видно одразу: якщо запитів стає більше разом із записами — десь у циклі є запит до бази.
Запуск з папки crispy_notes_project (тестова база створюється й видаляється сама):

    cd module_5/lessons/lesson_50_ci_cd/crispy_notes_project
    python manage.py shell < ../../../../module_6/lessons/lesson_51_final_project/query_count.py
"""
from django.contrib.auth.models import Group, User
from django.db import connection
from django.test import Client
from django.test.utils import CaptureQueriesContext, setup_test_environment
from django.test.runner import DiscoverRunner

from hello_app.models import Note, Notebook, ShoppingList, Tag, TodoList

setup_test_environment()
runner = DiscoverRunner(verbosity=0)
old = runner.setup_databases()


def fill(user: User, group: Group, n: int) -> None:
    nb = Notebook.objects.create(user=user, title=f"NB{n}")
    tags = [Tag.objects.create(user=user, name=f"t{n}-{i}") for i in range(3)]
    for i in range(n):
        note = Note.objects.create(user=user, title=f"note {n}-{i}", content="x", notebook=nb, group=group if i % 2 else None)
        note.tags.set(tags)
        ShoppingList.objects.create(user=user, title=f"shop {n}-{i}", group=group if i % 2 else None)
        TodoList.objects.create(user=user, title=f"todo {n}-{i}")


pages = ["/notes/", "/notebooks/", "/shopping/", "/todo/", "/api/notes/"]
results = {}
for n in (10, 40):
    Note.objects.all().delete(); ShoppingList.objects.all().delete(); TodoList.objects.all().delete()
    Tag.objects.all().delete(); Notebook.objects.all().delete(); User.objects.all().delete(); Group.objects.all().delete()
    user = User.objects.create_user("olena", password="pass-olena-123")
    group = Group.objects.create(name="family")
    user.groups.add(group)
    fill(user, group, n)
    client = Client()
    client.force_login(user)
    for page in pages:
        with CaptureQueriesContext(connection) as ctx:
            status = client.get(page).status_code
        results.setdefault(page, []).append((n, status, len(ctx.captured_queries)))
for page, rows in results.items():
    print(f"{page:<14} " + "  ".join(f"N={n}: {q} SQL (HTTP {s})" for n, s, q in rows))
runner.teardown_databases(old)

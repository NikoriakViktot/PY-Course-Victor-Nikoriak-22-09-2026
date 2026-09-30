"""Тести шару форм і шаблонів: login, crispy-форма, context processor, закріплення.

Повне тестування проєкту (сервіси, selectors, Selenium) — урок 41.

    python manage.py test
"""
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .forms import NoteForm
from .models import Note, Notebook


class NotesTestCase(TestCase):
    def setUp(self):
        self.olena = User.objects.create_user("olena", password="pass-12345")
        self.bob = User.objects.create_user("bob", password="pass-12345")
        self.client.login(username="olena", password="pass-12345")


class LoginRequiredTests(TestCase):
    def test_anonymous_is_redirected_to_login(self):
        response = self.client.get(reverse("hello_app:note_list"))
        self.assertRedirects(response, "/accounts/login/?next=/notes/", fetch_redirect_response=False)


class CrispyFormTests(NotesTestCase):
    def test_form_page_renders_layout(self):
        html = self.client.get(reverse("hello_app:note_create")).content.decode()
        self.assertIn('id="note-form"', html)
        self.assertEqual(html.count("<fieldset"), 3)
        self.assertIn("Зберегти нотатку", html)

    def test_notebook_choices_are_filtered_by_user(self):
        Notebook.objects.create(user=self.olena, title="Робота")
        Notebook.objects.create(user=self.bob, title="Чуже")
        form = NoteForm(user=self.olena)
        self.assertEqual([nb.title for nb in form.fields["notebook"].queryset], ["Робота"])


class NoteCreateTests(NotesTestCase):
    def test_create_redirects_to_detail(self):
        response = self.client.post(reverse("hello_app:note_create"), {"title": "План", "priority": "2"})
        note = Note.objects.get(title="План")
        self.assertRedirects(response, reverse("hello_app:note_detail", args=[note.pk]))
        self.assertEqual(note.user, self.olena)

    def test_is_pinned_is_saved_on_create(self):
        self.client.post(reverse("hello_app:note_create"), {"title": "Важливе", "priority": "2", "is_pinned": "on"})
        self.assertTrue(Note.objects.get(title="Важливе").is_pinned)


class SidebarContextTests(NotesTestCase):
    def test_sidebar_is_in_every_page(self):
        Notebook.objects.create(user=self.olena, title="Робота")
        response = self.client.get(reverse("hello_app:note_list"))
        self.assertEqual([nb.title for nb in response.context["sidebar_notebooks"]], ["Робота"])

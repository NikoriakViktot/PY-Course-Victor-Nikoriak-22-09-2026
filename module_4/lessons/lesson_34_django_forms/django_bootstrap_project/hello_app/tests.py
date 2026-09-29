"""Тести CRUD на формах: PRG, повідомлення, видалення лише через POST, CSRF.

    python manage.py test
"""
from django.test import Client, TestCase
from django.urls import reverse

from .forms import NoteForm
from .models import Note


class NoteFormTests(TestCase):
    def test_title_is_required(self):
        form = NoteForm(data={"title": "", "content": "текст"})
        self.assertFalse(form.is_valid())
        self.assertEqual(list(form.errors), ["title"])

    def test_title_max_length(self):
        self.assertFalse(NoteForm(data={"title": "x" * 201}).is_valid())
        self.assertTrue(NoteForm(data={"title": "x" * 200}).is_valid())


class NoteCrudTests(TestCase):
    def test_create_redirects_to_list_with_message(self):
        # follow=True — пройти за перенаправленням, як браузер; повідомлення — на тій сторінці
        response = self.client.post(reverse("hello_app:note_create"), {"title": "Нова нотатка"}, follow=True)
        self.assertEqual(response.redirect_chain, [(reverse("hello_app:note_list"), 302)])
        self.assertContains(response, "Нотатку &quot;Нова нотатка&quot; успішно створено!")
        self.assertEqual(Note.objects.count(), 1)

    def test_invalid_data_rerenders_form(self):
        response = self.client.post(reverse("hello_app:note_create"), {"title": ""})
        self.assertEqual(response.status_code, 200)
        self.assertIn("title", response.context["form"].errors)
        self.assertEqual(Note.objects.count(), 0)

    def test_edit_uses_instance(self):
        note = Note.objects.create(title="Стара назва")
        url = reverse("hello_app:note_edit", args=[note.pk])
        self.assertEqual(self.client.get(url).context["form"].initial["title"], "Стара назва")
        self.assertRedirects(self.client.post(url, {"title": "Нова назва"}),
                             reverse("hello_app:note_detail", args=[note.pk]))
        note.refresh_from_db()
        self.assertEqual(note.title, "Нова назва")

    def test_delete_only_on_post(self):
        note = Note.objects.create(title="Видали мене")
        url = reverse("hello_app:note_delete", args=[note.pk])
        self.assertEqual(self.client.get(url).status_code, 200)
        self.assertTrue(Note.objects.filter(pk=note.pk).exists())
        self.assertRedirects(self.client.post(url), reverse("hello_app:note_list"))
        self.assertFalse(Note.objects.filter(pk=note.pk).exists())

    def test_missing_note_is_404(self):
        self.assertEqual(self.client.get(reverse("hello_app:note_detail", args=[99])).status_code, 404)

    def test_csrf_is_enforced(self):
        client = Client(enforce_csrf_checks=True)
        response = client.post(reverse("hello_app:note_create"), {"title": "Без токена"})
        self.assertEqual(response.status_code, 403)

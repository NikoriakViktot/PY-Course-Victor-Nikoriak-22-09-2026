"""Тести REST API (урок 35). Тести HTML-частини з уроку 34 — у tests.py — теж мають проходити:
рефакторинг додав API, не змінивши сторінок.

    python manage.py test
"""
import time

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from . import services
from .models import Note, Notebook


class NoteApiTests(APITestCase):
    def setUp(self):
        self.olena = User.objects.create_user("olena", password="pass-12345")
        self.bob = User.objects.create_user("bob", password="pass-12345")
        self.note = services.create_note(user=self.olena, title="Вивчити DRF", priority=3)
        self.bob_note = services.create_note(user=self.bob, title="Нотатка Боба")
        self.client.force_authenticate(self.olena)

    def test_anonymous_gets_401(self):
        # Урок 35: 403 (першою була SessionAuthentication). Урок 40: JWT першим → 401 + WWW-Authenticate
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get("/api/notes/").status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_shows_only_own_notes(self):
        response = self.client.get("/api/notes/")
        self.assertEqual([n["title"] for n in response.data], ["Вивчити DRF"])

    def test_foreign_note_is_404(self):
        self.assertEqual(self.client.get(f"/api/notes/{self.bob_note.pk}/").status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.client.delete(f"/api/notes/{self.bob_note.pk}/").status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Note.objects.filter(pk=self.bob_note.pk).exists())

    def test_create_sets_owner_from_request(self):
        response = self.client.post("/api/notes/", {"title": "Нова", "priority": 4, "user": self.bob.pk}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Note.objects.get(pk=response.data["id"]).user, self.olena)
        self.assertNotIn("user", response.data)

    def test_validation_errors(self):
        response = self.client.post("/api/notes/", {"title": "", "priority": 9}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(set(response.data), {"title", "priority"})

    def test_foreign_notebook_is_rejected(self):
        foreign = Notebook.objects.create(user=self.bob, title="Записник Боба")
        response = self.client.post("/api/notes/", {"title": "Чужий записник", "notebook": foreign.pk}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("notebook", response.data)

    def test_patch_changes_only_sent_fields_and_updated_at(self):
        before = self.note.updated_at
        time.sleep(0.01)
        response = self.client.patch(f"/api/notes/{self.note.pk}/", {"title": "Вивчити DRF і FastAPI"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.note.refresh_from_db()
        self.assertEqual((self.note.title, self.note.priority), ("Вивчити DRF і FastAPI", 3))
        self.assertGreater(self.note.updated_at, before)

    def test_delete_and_pin(self):
        pinned = self.client.post(f"/api/notes/{self.note.pk}/pin/")
        self.assertTrue(pinned.data["is_pinned"])
        self.assertEqual(self.client.delete(f"/api/notes/{self.note.pk}/").status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Note.objects.filter(pk=self.note.pk).exists())

    def test_filter_by_notebook(self):
        study = Notebook.objects.create(user=self.olena, title="Навчання")
        services.create_note(user=self.olena, title="Конспект DRF", notebook=study)
        response = self.client.get("/api/notes/", {"notebook": study.pk})
        self.assertEqual([n["title"] for n in response.data], ["Конспект DRF"])
        foreign = Notebook.objects.create(user=self.bob, title="Записник Боба")
        for value in (foreign.pk, "abc"):
            self.assertEqual(self.client.get("/api/notes/", {"notebook": value}).status_code, status.HTTP_404_NOT_FOUND)

    def test_schema_lists_api_paths(self):
        response = self.client.get("/api/schema/")
        self.assertIn(b"/api/notes/{id}/pin/:", response.content)

from django.test import TestCase
from django.urls import reverse

from .models import Note


class NoteTests(TestCase):
    """Тести Django: окрема тестова база, яка створюється й видаляється автоматично (урок 41)."""

    def test_pinned_notes_first(self):
        Note.objects.create(title="Стара закріплена", is_pinned=True)
        Note.objects.create(title="Нова звичайна")
        self.assertEqual([n.title for n in Note.objects.all()], ["Стара закріплена", "Нова звичайна"])

    def test_note_list_page(self):
        Note.objects.create(title="Купити молоко", content="2 л")
        response = self.client.get(reverse("hello_app:note_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Купити молоко")
        self.assertTemplateUsed(response, "hello_app/note_list.html")

    def test_default_priority(self):
        note = Note.objects.create(title="Без пріоритету")
        self.assertEqual(note.get_priority_display(), "Звичайний")

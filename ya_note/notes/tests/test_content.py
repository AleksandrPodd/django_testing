"""Тестирование контента."""
from django.contrib.auth import get_user_model

from notes.forms import NoteForm
from .utils import BaseTestClass, NOTE_ADD_URL, NOTE_EDIT_URL, NOTES_LIST_URL

User = get_user_model()


class TestCreateNotePage(BaseTestClass):
    """Тест контента страницы создания заметки."""

    def test_notes_list_for_author(self):
        """Проверка наличия заметки в списке заметок автора заметки."""
        notes = self.auth_author.get(
            NOTES_LIST_URL).context['object_list']
        self.assertIn(self.note, notes)
        note = notes.get(id=self.note.id)
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.slug, self.note.slug)
        self.assertEqual(note.author, self.note.author)

    def test_notes_list_for_not_author(self):
        """Проверка отсутствия чужой заметки в списке заметок."""
        self.assertNotIn(self.note, self.auth_not_author.get(
            NOTES_LIST_URL).context['object_list'])

    def test_authorized_client_has_form(self):
        """Проверка наличия формы в словаре контекста."""
        for url in (NOTE_EDIT_URL, NOTE_ADD_URL):
            with self.subTest(url=url):
                self.assertIsInstance(
                    self.auth_author.get(url).context.get('form'),
                    NoteForm
                )

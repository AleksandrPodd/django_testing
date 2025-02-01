"""Тестирование контента."""
from django.contrib.auth import get_user_model

from notes.forms import NoteForm
from .utils import BaseTestClass, NOTE_ADD_URL, NOTE_EDIT_URL, NOTES_LIST_URL

User = get_user_model()


class TestCreateNotePage(BaseTestClass):
    """Тест контента страницы создания заметки."""

    def test_notes_list_for_author_users(self):
        """Проверка наличия заметки в списке заметок автора заметки."""
        self.client.force_login(self.author1)
        note = self.client.get(
            NOTES_LIST_URL).context['object_list'].get(id=self.note.id)
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.slug, self.note.slug)

    def test_notes_list_for_not_author_users(self):
        """Проверка отсутствия чужой заметки в списке заметок."""
        self.client.force_login(self.author2)
        self.assertIs((self.note in self.client.get(
            NOTES_LIST_URL).context['object_list']), False)

    def test_authorized_client_has_form(self):
        """Проверка наличия формы в словаре контекста."""
        for url in (NOTE_EDIT_URL, NOTE_ADD_URL):
            with self.subTest(url=url):
                self.client.force_login(self.author1)
                self.assertIsInstance(
                    self.client.get(url).context.get('form'),
                    NoteForm
                )

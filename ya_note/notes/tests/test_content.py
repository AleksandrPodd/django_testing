"""Тестирование контента."""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note


User = get_user_model()


class TestCreateNotePage(TestCase):
    """Тест контента страницы создания заметки."""

    @classmethod
    def setUpTestData(cls):
        """Фикстуры."""
        cls.add_note_url = reverse('notes:add')
        cls.author1 = User.objects.create(username='Пользователь 1')
        cls.author2 = User.objects.create(username='Пользователь 2')
        cls.note = Note.objects.create(
            title='Заголовок', text='Текст', author=cls.author1, slug='post_1'
        )

    def test_notes_list_for_different_users(self):
        """Проверка наличия или отсутствия заметки в списке заметок."""
        sessions = (
            (self.author1, True),
            (self.author2, False)
        )
        for user, note_in_list in sessions:
            with self.subTest(user=user, note_in_list=note_in_list):
                self.client.force_login(user)
                response = self.client.get(reverse('notes:list'))
                object_list = response.context['object_list']
                self.assertIs((self.note in object_list), note_in_list)

    def test_authorized_client_has_form(self):
        """Проверка наличия формы в словаре контекста."""
        for name, arg in (
            ('notes:edit', (self.note.slug,)),
            ('notes:add', None)
        ):
            with self.subTest(name=name, arg=arg):
                self.client.force_login(self.author1)
                response = self.client.get(reverse(name, args=arg))
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)

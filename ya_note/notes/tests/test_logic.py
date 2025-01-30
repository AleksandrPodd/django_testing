"""Тестирование логики."""
from http import HTTPStatus
from pytils.translit import slugify

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note


User = get_user_model()


class TestCommentCreation(TestCase):
    """Проверка создания заметок."""

    @classmethod
    def setUpTestData(cls):
        """Фикстуры."""
        cls.url = reverse('notes:add')
        cls.form_data = {
            'title': 'Заголовок',
            'text': 'Текст',
            'slug': 'post_1'
        }
        cls.author = User.objects.create(username='Пользователь')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)

    def test_anonymous_user_cant_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_can_create_note(self):
        """Пользователь может создать заметку."""
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.title, 'Заголовок')
        self.assertEqual(note.text, 'Текст')
        self.assertEqual(note.slug, 'post_1')
        self.assertEqual(note.author, self.author)

    def test_not_unique_slug(self):
        """Невозможность создать две заметки с одинаковым slug."""
        note = Note.objects.create(
            title='Заголовок', text='Текст', author=self.author, slug='post_1'
        )
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertFormError(
            response, 'form', 'slug', errors=(note.slug + WARNING)
        )
        self.assertEqual(Note.objects.count(), 1)

    def test_empty_slug(self):
        """Автоматическое формирование незаполненного slug-поля."""
        response = self.auth_client.post(
            self.url,
            data={'title': 'Заголовок', 'text': 'Текст'}
        )
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.get().slug, slugify('Заголовок'))


class TestNoteEditDelete(TestCase):
    """Проверка удаления и правки заметки."""

    @classmethod
    def setUpTestData(cls):
        """Фикстуры."""
        cls.author1 = User.objects.create(username='Пользователь 1')
        cls.author2 = User.objects.create(username='Пользователь 2')
        cls.author_client1 = Client()
        cls.author_client1.force_login(cls.author1)
        cls.author_client2 = Client()
        cls.author_client2.force_login(cls.author2)
        cls.note = Note.objects.create(
            title='Заголовок', text='Текст', author=cls.author1, slug='post_1'
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
        }

    def test_author_can_delete_note(self):
        """Автор может удалить свою заметку."""
        response = self.author_client1.delete(self.delete_url)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_cant_delete_note_of_another_user(self):
        """Пользователь не может удалить чужую заметку."""
        response = self.author_client2.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_note(self):
        """Автор может редактировать свою заметку."""
        response = self.author_client1.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, 'Новый текст')

    def test_user_cant_edit_note_of_another_user(self):
        """Пользователь не может править чужую заметку."""
        response = self.author_client2.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, 'Текст')

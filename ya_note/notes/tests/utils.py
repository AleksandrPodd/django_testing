"""Модуль с базовым классом для тестирования."""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test import Client
from django.urls import reverse

from notes.models import Note

User = get_user_model()

SLUG = 'post_1'
LOGIN_URL = reverse('users:login')
LOGOUT_URL = reverse('users:logout')
SIGN_UP_URL = reverse('users:signup')
HOME_URL = reverse('notes:home')
NOTES_LIST_URL = reverse('notes:list')
NOTE_ADD_URL = reverse('notes:add')
SUCCESS_URL = reverse('notes:success')
NOTE_DETAIL_URL = reverse('notes:detail', args=(SLUG,))
NOTE_EDIT_URL = reverse('notes:edit', args=(SLUG,))
NOTE_DELETE_URL = reverse('notes:delete', args=(SLUG,))
REDIRECT_URL = f'{LOGIN_URL}?next='


class BaseTestClass(TestCase):
    """Базовый тестовый класс."""

    @classmethod
    def setUpTestData(cls):
        """Фикстуры."""
        cls.author1 = User.objects.create(username='Пользователь 1')
        cls.author2 = User.objects.create(username='Пользователь 2')
        cls.note = Note.objects.create(
            title='Название', text='Слова', author=cls.author1, slug='post_1'
        )
        cls.auth_author1 = Client()
        cls.auth_author1.force_login(cls.author1)
        cls.auth_author2 = Client()
        cls.auth_author2.force_login(cls.author2)
        cls.guest = Client()
        cls.form_data = {
            'title': 'Заголовок',
            'text': 'Текст',
            'slug': 'post_2'
        }

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
REDIRECT_EXPRESSION = f'{LOGIN_URL}?next='
NOTE_EDIT_REDIRECT_URL = f'{REDIRECT_EXPRESSION}{NOTE_EDIT_URL}'
NOTE_DELETE_REDIRECT_URL = f'{REDIRECT_EXPRESSION}{NOTE_DELETE_URL}'
NOTE_DETAIL_REDIRECT_URL = f'{REDIRECT_EXPRESSION}{NOTE_DETAIL_URL}'
SUCCESS_REDIRECT_URL = f'{REDIRECT_EXPRESSION}{SUCCESS_URL}'
NOTES_LIST_REDIRECT_URL = f'{REDIRECT_EXPRESSION}{NOTES_LIST_URL}'
NOTE_ADD_REDIRECT_URL = f'{REDIRECT_EXPRESSION}{NOTE_ADD_URL}'


class BaseTestClass(TestCase):
    """Базовый тестовый класс."""

    @classmethod
    def setUpTestData(cls):
        """Фикстуры."""
        cls.author = User.objects.create(username='Пользователь Автор')
        cls.not_author = User.objects.create(username='Пользователь Не Автор')
        cls.note = Note.objects.create(
            title='Название', text='Слова', author=cls.author, slug='post_1'
        )
        cls.auth_author = Client()
        cls.auth_author.force_login(cls.author)
        cls.auth_not_author = Client()
        cls.auth_not_author.force_login(cls.not_author)
        cls.form_data = {
            'title': 'Заголовок',
            'text': 'Текст',
            'slug': 'post_2'
        }

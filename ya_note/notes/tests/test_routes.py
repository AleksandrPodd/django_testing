"""Тестирование маршрутизации."""
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    """Класс тестирования маршрутов."""

    @classmethod
    def setUpTestData(cls):
        """Фикстуры."""
        cls.author1 = User.objects.create(username='Пользователь 1')
        cls.author2 = User.objects.create(username='Пользователь 2')
        cls.note = Note.objects.create(
            title='Заголовок', text='Текст', author=cls.author1, slug='post_1'
        )

    def test_pages_availability_unauth(self):
        """Доступность неавторизованному пользователю."""
        urls = (
            ('notes:home'),
            ('users:login'),
            ('users:logout'),
            ('users:signup'),
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_edit_and_delete(self):
        """Редактирование и удаление заметки."""
        users_statuses = (
            (self.author1, HTTPStatus.OK),
            (self.author2, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('notes:edit', 'notes:delete', 'notes:detail'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Редирект анонимных пользователей."""
        login_url = reverse('users:login')
        for name, arg in (
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
            ('notes:detail', (self.note.slug,)),
            ('notes:success', None),
            ('notes:list', None),
            ('notes:add', None)
        ):
            with self.subTest(name=name, arg=arg):
                url = reverse(name, args=arg)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_availability_for_auth_user(self):
        """Доступность страниц залогиненому пользователю."""
        self.client.force_login(self.author1)
        for name in ('notes:success', 'notes:list', 'notes:add'):
            with self.subTest(user=self.author1, name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

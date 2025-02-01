"""Тестирование маршрутизации."""
from http import HTTPStatus

from django.contrib.auth import get_user_model

from .utils import (
    BaseTestClass,
    LOGIN_URL,
    LOGOUT_URL,
    SIGN_UP_URL,
    HOME_URL,
    NOTES_LIST_URL,
    NOTE_ADD_URL,
    SUCCESS_URL,
    NOTE_DETAIL_URL,
    NOTE_EDIT_URL,
    NOTE_DELETE_URL,
    REDIRECT_URL,
)

User = get_user_model()


class TestRoutes(BaseTestClass):
    """Класс тестирования маршрутов."""

    def test_redirect_for_anonymous_client(self):
        """Редирект анонимных пользователей."""
        for url in (
            NOTE_EDIT_URL,
            NOTE_DELETE_URL,
            NOTE_DETAIL_URL,
            SUCCESS_URL,
            NOTES_LIST_URL,
            NOTE_ADD_URL
        ):
            with self.subTest(url=url):
                self.assertRedirects(self.client.get(url), REDIRECT_URL + url)

    def test_availability_for_all_users(self):
        """Проверка всех кодов возврата."""
        sessions = (
            (HOME_URL, self.guest, HTTPStatus.OK),
            (LOGIN_URL, self.guest, HTTPStatus.OK),
            (LOGOUT_URL, self.guest, HTTPStatus.OK),
            (SIGN_UP_URL, self.guest, HTTPStatus.OK),
            (NOTE_EDIT_URL, self.auth_author1, HTTPStatus.OK),
            (NOTE_DELETE_URL, self.auth_author1, HTTPStatus.OK),
            (NOTE_DETAIL_URL, self.auth_author1, HTTPStatus.OK),
            (NOTE_EDIT_URL, self.auth_author2, HTTPStatus.NOT_FOUND),
            (NOTE_DELETE_URL, self.auth_author2, HTTPStatus.NOT_FOUND),
            (NOTE_DETAIL_URL, self.auth_author2, HTTPStatus.NOT_FOUND),
            (SUCCESS_URL, self.auth_author1, HTTPStatus.OK),
            (NOTES_LIST_URL, self.auth_author1, HTTPStatus.OK),
            (NOTE_ADD_URL, self.auth_author1, HTTPStatus.OK),

        )
        for url, user, status in sessions:
            with self.subTest(url=url, user=user, status=status):
                self.assertEqual(user.get(url).status_code, status)

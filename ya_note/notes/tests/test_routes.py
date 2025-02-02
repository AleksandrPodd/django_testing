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
    NOTE_EDIT_REDIRECT_URL,
    NOTE_DELETE_REDIRECT_URL,
    NOTE_DETAIL_REDIRECT_URL,
    SUCCESS_REDIRECT_URL,
    NOTES_LIST_REDIRECT_URL,
    NOTE_ADD_REDIRECT_URL
)

User = get_user_model()


class TestRoutes(BaseTestClass):
    """Класс тестирования маршрутов."""

    def test_redirect_for_anonymous_client(self):
        """Редирект анонимных пользователей."""
        for url, redirect_url in (
            (NOTE_EDIT_URL, NOTE_EDIT_REDIRECT_URL),
            (NOTE_DELETE_URL, NOTE_DELETE_REDIRECT_URL),
            (NOTE_DETAIL_URL, NOTE_DETAIL_REDIRECT_URL),
            (SUCCESS_URL, SUCCESS_REDIRECT_URL),
            (NOTES_LIST_URL, NOTES_LIST_REDIRECT_URL),
            (NOTE_ADD_URL, NOTE_ADD_REDIRECT_URL)
        ):
            with self.subTest(url=url, redirect_url=redirect_url):
                self.assertRedirects(self.client.get(url), redirect_url)

    def test_availability_for_all_users(self):
        """Проверка всех кодов возврата."""
        sessions = (
            (HOME_URL, self.client, HTTPStatus.OK),
            (LOGIN_URL, self.client, HTTPStatus.OK),
            (LOGOUT_URL, self.client, HTTPStatus.OK),
            (SIGN_UP_URL, self.client, HTTPStatus.OK),
            (NOTE_EDIT_URL, self.auth_author, HTTPStatus.OK),
            (NOTE_DELETE_URL, self.auth_author, HTTPStatus.OK),
            (NOTE_DETAIL_URL, self.auth_author, HTTPStatus.OK),
            (NOTE_EDIT_URL, self.auth_not_author, HTTPStatus.NOT_FOUND),
            (NOTE_DELETE_URL, self.auth_not_author, HTTPStatus.NOT_FOUND),
            (NOTE_DETAIL_URL, self.auth_not_author, HTTPStatus.NOT_FOUND),
            (SUCCESS_URL, self.auth_author, HTTPStatus.OK),
            (NOTES_LIST_URL, self.auth_author, HTTPStatus.OK),
            (NOTE_ADD_URL, self.auth_author, HTTPStatus.OK),
            (NOTE_EDIT_URL, self.client, HTTPStatus.FOUND),
            (NOTE_DELETE_URL, self.client, HTTPStatus.FOUND),
            (NOTE_DETAIL_URL, self.client, HTTPStatus.FOUND),
            (SUCCESS_URL, self.client, HTTPStatus.FOUND),
            (NOTES_LIST_URL, self.client, HTTPStatus.FOUND),
            (NOTE_ADD_URL, self.client, HTTPStatus.FOUND)
        )
        for url, user, status in sessions:
            with self.subTest(url=url, user=user, status=status):
                self.assertEqual(user.get(url).status_code, status)

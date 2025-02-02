"""Тестирование маршрутов."""
from http import HTTPStatus

from pytest_django.asserts import assertRedirects
from django.test.client import Client
import pytest

pytestmark = pytest.mark.django_db

LOGIN_PAGE_URL = pytest.lazy_fixture('login')
LOGOUT_PAGE_URL = pytest.lazy_fixture('logout')
SIGNUP_PAGE_URL = pytest.lazy_fixture('signup')
NEWS_HOME_URL = pytest.lazy_fixture('news_home')
NEWS_DETAIL_URL = pytest.lazy_fixture('news_detail')
COMMENT_EDIT_URL = pytest.lazy_fixture('news_comment_edit')
COMMENT_DELETE_URL = pytest.lazy_fixture('news_comment_delete')
REDIRECT_EDIT_URL = pytest.lazy_fixture('redirect_edit_comment')
REDIRECT_DELETE_URL = pytest.lazy_fixture('redirect_delete_comment')
AUTHOR_CLIENT = pytest.lazy_fixture('author_client')
NOT_AUTHOR_CLIENT = pytest.lazy_fixture('not_author_client')
CLIENT = Client()


@pytest.mark.parametrize(
    'url, user, expected_status',
    (
        (NEWS_HOME_URL, CLIENT, HTTPStatus.OK),
        (LOGIN_PAGE_URL, CLIENT, HTTPStatus.OK),
        (LOGOUT_PAGE_URL, CLIENT, HTTPStatus.OK),
        (SIGNUP_PAGE_URL, CLIENT, HTTPStatus.OK),
        (NEWS_DETAIL_URL, CLIENT, HTTPStatus.OK),
        (COMMENT_EDIT_URL, CLIENT, HTTPStatus.FOUND),
        (COMMENT_DELETE_URL, CLIENT, HTTPStatus.FOUND),
        (COMMENT_EDIT_URL, NOT_AUTHOR_CLIENT, HTTPStatus.NOT_FOUND),
        (COMMENT_EDIT_URL, AUTHOR_CLIENT, HTTPStatus.OK),
        (COMMENT_DELETE_URL, NOT_AUTHOR_CLIENT, HTTPStatus.NOT_FOUND),
        (COMMENT_DELETE_URL, AUTHOR_CLIENT, HTTPStatus.OK),
        (NEWS_HOME_URL, AUTHOR_CLIENT, HTTPStatus.OK),
        (LOGIN_PAGE_URL, AUTHOR_CLIENT, HTTPStatus.OK),
        (LOGOUT_PAGE_URL, AUTHOR_CLIENT, HTTPStatus.OK),
        (SIGNUP_PAGE_URL, AUTHOR_CLIENT, HTTPStatus.OK),
        (NEWS_DETAIL_URL, AUTHOR_CLIENT, HTTPStatus.OK)
    )
)
def test_pages_response_status(url, user, expected_status):
    """Проверки кодов возврата."""
    assert user.get(url).status_code == expected_status


@pytest.mark.parametrize(
    'url, expected_url',
    (
        (COMMENT_EDIT_URL, REDIRECT_EDIT_URL),
        (COMMENT_DELETE_URL, REDIRECT_DELETE_URL)
    )
)
def test_edit_pages_for_anonymous_user(client, url, expected_url, comment):
    """Правка комментариев анонимным пользователем."""
    assertRedirects(client.get(url), expected_url)

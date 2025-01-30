"""Тестирование маршрутов."""
import pytest

from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name', (
        ('news:home', False),
        ('users:login', False),
        ('users:logout', False),
        ('users:signup', False),
        ('news:detail', True)
    )
)
def test_pages_availability_for_anonymous_user(client, name, news):
    """Доступ к страницам анонимного пользователя."""
    if name[1]:
        url = reverse(name[0], args=(news.id,))
    else:
        url = reverse(name[0])
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('author2_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author1_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_edit_pages_availability_for_different_users(
        parametrized_client, name, comment, expected_status
):
    """Правка комментариев автором и не автором."""
    url = reverse(name, args=(comment.id,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize('name', ('news:edit', 'news:delete'))
def test_edit_pages_for_anonymous_user(client, name, comment):
    """Правка комментариев анонимным пользователем."""
    login_url = reverse('users:login')
    url = reverse(name, args=(comment.id,))
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)

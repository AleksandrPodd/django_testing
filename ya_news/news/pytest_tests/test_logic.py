"""Тестирование логики."""
import pytest

from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news):
    """Анонимный пользователь не может отправить комментарий."""
    client.post(
        reverse('news:detail', args=(news.id,)), data={'text': 'Комментарий'}
    )
    assert Comment.objects.count() == 0


def test_user_can_create_comment(author1_client, news):
    """Авторизованнй пользователь может отправить комментарий."""
    url = reverse('news:detail', args=(news.id,))
    response = author1_client.post(url, data={'text': 'Комментарий'})
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == 'Комментарий'
    assert comment.news == news


def test_user_cant_use_bad_words(author1_client, news):
    """Проверка блокировки запрещенных слов."""
    response = author1_client.post(
        reverse('news:detail', args=(news.id,)),
        data={'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    )
    assertFormError(response, form='form', field='text', errors=WARNING)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_author_can_delete_comment(news, comment, author1_client):
    """Автор может удалить свой комментарий."""
    url = reverse('news:delete', args=(comment.id,))
    response = author1_client.delete(url)
    assertRedirects(
        response, reverse('news:detail', args=(news.id,)) + '#comments'
    )
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_cant_delete_comment(news, comment, author2_client):
    """Пользователь не может удалить чужой комментарий."""
    url = reverse('news:delete', args=(comment.id,))
    response = author2_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


@pytest.mark.parametrize(
    'parametrized_client, expected_result',
    (
        (pytest.lazy_fixture('author1_client'), 'Измененный комментарий'),
        (pytest.lazy_fixture('author2_client'), 'Комментарий Автора1')
    ),
)
def test_edit_comment(parametrized_client, expected_result, comment):
    """Проверка редактирования комменатрия."""
    parametrized_client.post(
        reverse('news:edit', args=(comment.id,)),
        data={'text': 'Измененный комментарий'}
    )
    comment.refresh_from_db()
    assert comment.text == expected_result

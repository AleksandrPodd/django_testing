"""Тестирование логики."""
from http import HTTPStatus

from pytest_django.asserts import assertFormError, assertRedirects
import pytest

from news.forms import WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db


def test_anonymous_user_cant_create_comment(
        client, news, news_detail, form_data):
    """Анонимный пользователь не может отправить комментарий."""
    client.post(news_detail, data=form_data)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(
        author, author_client, news, news_detail, form_data):
    """Авторизованнй пользователь может отправить комментарий."""
    initial_comments_count = Comment.objects.count()
    response = author_client.post(news_detail, data=form_data)
    assertRedirects(response, f'{news_detail}#comments')
    assert Comment.objects.count() == initial_comments_count + 1
    comment = Comment.objects.get()
    assert comment.text == form_data.get('text')
    assert comment.news == news
    assert comment.author == author


@pytest.mark.parametrize(
        'form_data', (
            pytest.lazy_fixture('form_data_bad_word_one'),
            pytest.lazy_fixture('form_data_bad_word_two')
        )
)
def test_user_cant_use_bad_words(author_client, news, news_detail, form_data):
    """Проверка блокировки запрещенных слов."""
    initial_comments_count = Comment.objects.count()
    response = author_client.post(
        news_detail,
        data=form_data
    )
    assertFormError(response, form='form', field='text', errors=WARNING)
    assert Comment.objects.count() == initial_comments_count


def test_author_can_delete_comment(
        news, comment, author_client, news_comment_delete, news_detail):
    """Автор может удалить свой комментарий."""
    initial_comments_count = Comment.objects.count()
    assertRedirects(
        author_client.delete(news_comment_delete), news_detail + '#comments'
    )
    assert Comment.objects.count() == initial_comments_count - 1


def test_user_cant_delete_comment(
        news, comment, not_author_client, news_comment_delete):
    """Пользователь не может удалить чужой комментарий."""
    initial_comments_count = Comment.objects.count()
    response = not_author_client.delete(news_comment_delete)
    test_comment = Comment.objects.get(id=comment.id)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == initial_comments_count
    assert test_comment.text == comment.text
    assert test_comment.news == comment.news
    assert test_comment.author == comment.author


def test_author_edit_comment(
        author_client, form_data, comment, news_comment_edit):
    """Проверка редактирования комменатрия автором."""
    author_client.post(news_comment_edit, data=form_data)
    test_comment = Comment.objects.get(id=comment.id)
    assert test_comment.text == form_data.get('text')
    assert test_comment.news == comment.news
    assert test_comment.author == comment.author


def test_not_author_edit_comment(
        not_author_client, form_data, comment, news_comment_edit):
    """Проверка редактирования комменатрия не автором."""
    not_author_client.post(news_comment_edit, data=form_data)
    test_comment = Comment.objects.get(id=comment.id)
    assert test_comment.text == comment.text
    assert test_comment.news == comment.news
    assert test_comment.author == comment.author

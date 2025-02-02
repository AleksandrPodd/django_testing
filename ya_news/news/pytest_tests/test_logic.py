"""Тестирование логики."""
from http import HTTPStatus

from pytest_django.asserts import (
    assertFormError, assertRedirects, assertQuerysetEqual
)
import pytest

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db
FORM_DATA = {'text': 'Измененный комментарий'}


def test_anonymous_user_cant_create_comment(
        client, news, news_detail):
    """Анонимный пользователь не может отправить комментарий."""
    client.post(news_detail, data=FORM_DATA)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(
        author, author_client, news, news_detail, news_detail_redirect):
    """Авторизованнй пользователь может отправить комментарий."""
    initial_comments_count = Comment.objects.count()
    response = author_client.post(news_detail, data=FORM_DATA)
    assertRedirects(response, news_detail_redirect)
    assert Comment.objects.count() - initial_comments_count == 1
    comment = Comment.objects.latest('id')
    assert comment.text == FORM_DATA['text']
    assert comment.news == news
    assert comment.author == author


@pytest.mark.parametrize(
    'form_data', ({'text': bad_word} for bad_word in BAD_WORDS)
)
def test_user_cant_use_bad_words(author_client, news, news_detail, form_data):
    """Проверка блокировки запрещенных слов."""
    initial_comments_count = Comment.objects.all()
    response = author_client.post(
        news_detail,
        data=form_data
    )
    assertFormError(response, form='form', field='text', errors=WARNING)
    assertQuerysetEqual(initial_comments_count, Comment.objects.all())


def test_author_can_delete_comment(
        news, comment, author_client, news_comment_delete, news_detail):
    """Автор может удалить свой комментарий."""
    initial_comments_count = Comment.objects.count()
    assertRedirects(
        author_client.delete(news_comment_delete), news_detail + '#comments'
    )
    assert Comment.objects.count() == initial_comments_count - 1
    assert not Comment.objects.filter(id=comment.id).exists()


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


def test_author_edit_comment(author_client, comment, news_comment_edit):
    """Проверка редактирования комменатрия автором."""
    author_client.post(news_comment_edit, data=FORM_DATA)
    test_comment = Comment.objects.get(id=comment.id)
    assert test_comment.text == FORM_DATA['text']
    assert test_comment.news == comment.news
    assert test_comment.author == comment.author


def test_not_author_edit_comment(
        not_author_client, comment, news_comment_edit):
    """Проверка редактирования комменатрия не автором."""
    not_author_client.post(news_comment_edit, data=FORM_DATA)
    test_comment = Comment.objects.get(id=comment.id)
    assert test_comment.text == comment.text
    assert test_comment.news == comment.news
    assert test_comment.author == comment.author

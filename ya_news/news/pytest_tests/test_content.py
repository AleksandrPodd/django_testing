"""Тестирование контента."""
from django.conf import settings
import pytest

from news.forms import CommentForm

pytestmark = pytest.mark.django_db


def test_homepage_news_count(news_set, client, news_home):
    """Количество новостей на главной странице."""
    assert client.get(news_home).context['object_list'].count(
    ) == settings.NEWS_COUNT_ON_HOME_PAGE


def test_homepage_news_sorting_check(news_set, client, news_home):
    """Сортировка на главной странице."""
    homepage_news = client.get(news_home).context['object_list']
    all_dates = [news.date for news in homepage_news]
    assert all_dates == sorted(all_dates, reverse=True)


def test_comments_order(comments_set, news, client, news_detail):
    """Проверка сортировки комментариев."""
    response = client.get(news_detail)
    assert 'news' in response.context
    current_news = response.context['news']
    all_comments = current_news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    assert all_timestamps == sorted(all_timestamps)


def test_anonymous_client_has_no_form(client, news, news_detail):
    """Анонимному пользователю недоступна форма отправки комментария."""
    response = client.get(news_detail)
    assert 'form' not in response.context


def test_authorized_client_has_form(author_client, news, news_detail):
    """Авторизованному пользователю доступна форма отправки комментария."""
    assert isinstance(
        author_client.get(news_detail).context.get('form'), CommentForm
    )

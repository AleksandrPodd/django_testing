"""Тестирование контента."""
import pytest

from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm


@pytest.mark.django_db
def test_homepage_news_count_and_sorting_check(news_set, client):
    """Количество новостей и сортировка на главной странице."""
    response = client.get(reverse('news:home'))
    object_list = response.context['object_list']
    news_count = object_list.count()
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE
    assert all_dates == sorted_dates


def test_comments_order(comments_set, news, client):
    """Проверка сортировки комментариев."""
    response = client.get(reverse('news:detail', args=(news.id,)))
    assert 'news' in response.context
    current_news = response.context['news']
    all_comments = current_news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, news):
    """Анонимному пользователю недоступна форма отправки комментария."""
    response = client.get(reverse('news:detail', args=(news.id,)))
    assert 'form' not in response.context


def test_authorized_client_has_form(author1_client, news):
    """Авторизованному пользователю доступна форма отправки комментария."""
    response = author1_client.get(reverse('news:detail', args=(news.id,)))
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)

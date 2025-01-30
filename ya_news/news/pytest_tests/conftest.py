"""Фикстуры Pytest."""
import pytest

from datetime import datetime, timedelta

from django.conf import settings
from django.test.client import Client
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture
def author1(django_user_model):
    """Объект пользователя 1."""
    return django_user_model.objects.create(username='Автор1')


@pytest.fixture
def author2(django_user_model):
    """Объект пользователя 2."""
    return django_user_model.objects.create(username='Автор2')


@pytest.fixture
def author1_client(author1):
    """Залогиненный пользователь 1."""
    client = Client()
    client.force_login(author1)
    return client


@pytest.fixture
def author2_client(author2):
    """Залогиненный пользователь 2."""
    client = Client()
    client.force_login(author2)
    return client


@pytest.fixture
def news():
    """Объект новости."""
    news = News.objects.create(
        title='Заголовок новости',
        text='Текст новости'
    )
    return news


@pytest.fixture
def news_set():
    """Набор новостей на главную страницу."""
    today = datetime.today()
    all_news = []
    for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        news = News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        all_news.append(news)
    return News.objects.bulk_create(all_news)


@pytest.fixture
def comment(author1, news):
    """Объект комментария."""
    comment = Comment.objects.create(
        news=news,
        author=author1,
        text='Комментарий Автора1'
    )
    return comment


@pytest.fixture
def comments_set(author1, news):
    """Два комментария."""
    now = timezone.now()
    for index in range(2):
        comment = Comment.objects.create(
            news=news, author=author1, text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()

"""Фикстуры Pytest."""
from datetime import datetime, timedelta

from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone
import pytest

from news.forms import BAD_WORDS
from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    """Объект пользователя 1."""
    return django_user_model.objects.create(username='Автор1')


@pytest.fixture
def not_author(django_user_model):
    """Объект пользователя 2."""
    return django_user_model.objects.create(username='Автор2')


@pytest.fixture
def author_client(author):
    """Залогиненный пользователь 1."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    """Залогиненный пользователь 2."""
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    """Объект новости."""
    return News.objects.create(
        title='Заголовок новости',
        text='Текст новости'
    )


@pytest.fixture
def news_set():
    """Набор новостей на главную страницу."""
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    return News.objects.bulk_create(all_news)


@pytest.fixture
def comment(author, news):
    """Объект комментария."""
    return Comment.objects.create(
        news=news,
        author=author,
        text='Комментарий Автора1'
    )


@pytest.fixture
def comments_set(author, news):
    """Два комментария."""
    now = timezone.now()
    for index in range(222):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()


@pytest.fixture
def form_data():
    """Данные для изменения комментария."""
    return {'text': 'Измененный комментарий'}


@pytest.fixture
def form_data_bad_word_one():
    """Данные для изменения комментария."""
    return {'text': BAD_WORDS[0]}


@pytest.fixture
def form_data_bad_word_two():
    """Данные для изменения комментария."""
    return {'text': BAD_WORDS[1]}


@pytest.fixture
def login():
    """Login page."""
    return reverse('users:login')


@pytest.fixture
def logout():
    """Logout page."""
    return reverse('users:login')


@pytest.fixture
def signup():
    """Signup page."""
    return reverse('users:signup')


@pytest.fixture
def news_home():
    """Home page."""
    return reverse('news:home')


@pytest.fixture
def news_detail(news):
    """News detail page."""
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def news_comment_edit(comment):
    """News comment edit page."""
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def news_comment_delete(comment):
    """News comment delete page."""
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def redirect_edit_comment(comment, login):
    """Redirect comment edit page."""
    url = reverse('news:edit', args=(comment.id,))
    return f'{login}?next={url}'


@pytest.fixture
def redirect_delete_comment(comment, login):
    """Redirect comment delete page."""
    url = reverse('news:delete', args=(comment.id,))
    return f'{login}?next={url}'

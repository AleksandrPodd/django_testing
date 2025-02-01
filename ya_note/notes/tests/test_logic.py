"""Тестирование логики."""
from http import HTTPStatus

from django.contrib.auth import get_user_model
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from .utils import (
    BaseTestClass,
    NOTE_ADD_URL,
    SUCCESS_URL,
    NOTE_EDIT_URL,
    NOTE_DELETE_URL,
)


User = get_user_model()


class TestNote(BaseTestClass):
    """Проверка создания, удаления и правки заметок."""

    def test_anonymous_user_cant_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        notes_count_initial = Note.objects.count()
        self.guest.post(NOTE_ADD_URL, data=self.form_data)
        self.assertEqual(Note.objects.count(), notes_count_initial)

    def test_user_can_create_note(self):
        """Пользователь может создать заметку."""
        notes_count_initial = Note.objects.count()
        response = self.auth_author1.post(NOTE_ADD_URL, data=self.form_data)
        self.assertRedirects(response, SUCCESS_URL)
        self.assertEqual(Note.objects.count(), notes_count_initial + 1)
        note = Note.objects.get(slug=self.form_data.get('slug'))
        self.assertEqual(note.title, self.form_data.get('title'))
        self.assertEqual(note.text, self.form_data.get('text'))
        self.assertEqual(note.slug, self.form_data.get('slug'))
        self.assertEqual(note.author, self.author1)

    def test_not_unique_slug(self):
        """Невозможность создать две заметки с одинаковым slug."""
        notes_count_initial = Note.objects.count()
        form = self.form_data
        form['slug'] = self.note.slug
        response = self.auth_author1.post(NOTE_ADD_URL, data=form)
        self.assertFormError(
            response, 'form', 'slug', errors=(self.note.slug + WARNING)
        )
        self.assertEqual(Note.objects.count(), notes_count_initial)

    def test_empty_slug(self):
        """Автоматическое формирование незаполненного slug-поля."""
        form = self.form_data
        form.pop('slug')
        response = self.auth_author1.post(NOTE_ADD_URL, data=form)
        new_slug = slugify(self.form_data.get('title'))
        note = Note.objects.get(slug=new_slug)
        self.assertRedirects(response, SUCCESS_URL)
        self.assertEqual(note.slug, new_slug)
        self.assertEqual(note.title, self.form_data.get('title'))
        self.assertEqual(note.text, self.form_data.get('text'))
        self.assertEqual(note.author, self.author1)

    def test_author_can_delete_note(self):
        """Автор может удалить свою заметку."""
        notes_count_initial = Note.objects.count()
        self.assertRedirects(
            self.auth_author1.delete(NOTE_DELETE_URL), SUCCESS_URL
        )
        self.assertEqual(Note.objects.count(), notes_count_initial - 1)

    def test_user_cant_delete_note_of_another_user(self):
        """Пользователь не может удалить чужую заметку."""
        notes_count_initial = Note.objects.count()
        self.assertEqual(self.auth_author2.delete(NOTE_DELETE_URL).status_code,
                         HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), notes_count_initial)
        self.assertEqual(Note.objects.get(slug=self.note.slug), self.note)

    def test_author_can_edit_note(self):
        """Автор может редактировать свою заметку."""
        response = self.auth_author1.post(NOTE_EDIT_URL, data=self.form_data)
        self.assertRedirects(response, SUCCESS_URL)
        note = Note.objects.get(slug=self.form_data.get('slug'))
        self.assertEqual(note.slug, self.form_data.get('slug'))
        self.assertEqual(note.title, self.form_data.get('title'))
        self.assertEqual(note.text, self.form_data.get('text'))
        self.assertEqual(note.author, self.author1)

    def test_user_cant_edit_note_of_another_user(self):
        """Пользователь не может править чужую заметку."""
        response = self.auth_author2.post(NOTE_EDIT_URL, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note = Note.objects.get(slug=self.note.slug)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.slug, self.note.slug)
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.author, self.author1)

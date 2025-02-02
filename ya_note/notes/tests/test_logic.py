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
        notes_initial = Note.objects.all()
        self.guest.post(NOTE_ADD_URL, data=self.form_data)
        self.assertQuerysetEqual(Note.objects.all(), notes_initial)

    def test_user_can_create_note(self):
        """Пользователь может создать заметку."""
        Note.objects.all().delete()
        response = self.auth_author.post(NOTE_ADD_URL, data=self.form_data)
        self.assertRedirects(response, SUCCESS_URL)
        self.assertEqual(Note.objects.count(), 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.form_data.get('title'))
        self.assertEqual(note.text, self.form_data.get('text'))
        self.assertEqual(note.slug, self.form_data.get('slug'))
        self.assertEqual(note.author, self.author)

    def test_not_unique_slug(self):
        """Невозможность создать две заметки с одинаковым slug."""
        notes_initial = Note.objects.all()
        form = self.form_data
        form['slug'] = self.note.slug
        response = self.auth_author.post(NOTE_ADD_URL, data=form)
        self.assertFormError(
            response, 'form', 'slug', errors=(self.note.slug + WARNING)
        )
        self.assertQuerysetEqual(Note.objects.all(), notes_initial)

    def test_empty_slug(self):
        """Автоматическое формирование незаполненного slug-поля."""
        form = self.form_data
        form.pop('slug')
        Note.objects.all().delete()
        response = self.auth_author.post(NOTE_ADD_URL, data=form)
        new_slug = slugify(self.form_data.get('title'))
        note = Note.objects.get()
        self.assertRedirects(response, SUCCESS_URL)
        self.assertEqual(note.slug, new_slug)
        self.assertEqual(note.title, self.form_data.get('title'))
        self.assertEqual(note.text, self.form_data.get('text'))
        self.assertEqual(note.author, self.author)

    def test_author_can_delete_note(self):
        """Автор может удалить свою заметку."""
        notes_count_initial = Note.objects.count()
        self.assertRedirects(
            self.auth_author.delete(NOTE_DELETE_URL), SUCCESS_URL
        )
        self.assertEqual(Note.objects.count(), notes_count_initial - 1)
        self.assertNotIn(self.note, Note.objects.all())

    def test_user_cant_delete_note_of_another_user(self):
        """Пользователь не может удалить чужую заметку."""
        notes_count_initial = Note.objects.count()
        self.assertEqual(self.auth_not_author.delete(
            NOTE_DELETE_URL).status_code, HTTPStatus.NOT_FOUND)
        note = Note.objects.get(id=self.note.id)
        self.assertEqual(Note.objects.count(), notes_count_initial)
        self.assertEqual(note.slug, self.note.slug)
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.author, self.note.author)

    def test_author_can_edit_note(self):
        """Автор может редактировать свою заметку."""
        initial_note = self.note
        response = self.auth_author.post(NOTE_EDIT_URL, data=self.form_data)
        self.assertRedirects(response, SUCCESS_URL)
        note = Note.objects.get(id=self.note.id)
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.author, initial_note.author)

    def test_user_cant_edit_note_of_another_user(self):
        """Пользователь не может править чужую заметку."""
        initial_note = self.note
        response = self.auth_not_author.post(
            NOTE_EDIT_URL, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note = Note.objects.get(id=self.note.id)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.slug, self.note.slug)
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.author, initial_note.author)

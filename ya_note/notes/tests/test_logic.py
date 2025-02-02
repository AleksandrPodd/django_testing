"""Тестирование логики."""
from http import HTTPStatus

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


class TestNote(BaseTestClass):
    """Проверка создания, удаления и правки заметок."""

    def test_anonymous_user_cant_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        notes_initial = Note.objects.all()
        self.client.post(NOTE_ADD_URL, data=self.form_data)
        self.assertQuerysetEqual(
            Note.objects.all(), notes_initial, transform=lambda x: x)

    def test_user_can_create_note(self):
        """Пользователь может создать заметку."""
        forms = (self.form_data, self.form_data_without_slug)
        for form_data in forms:
            with self.subTest(form_data=form_data):
                Note.objects.all().delete()
                response = self.auth_author.post(NOTE_ADD_URL, data=form_data)
                self.assertRedirects(response, SUCCESS_URL)
                self.assertEqual(Note.objects.count(), 1)
                if 'slug' not in form_data.keys():
                    form_data['slug'] = slugify(form_data['title'])
                note = Note.objects.get()
                self.assertEqual(note.title, form_data['title'])
                self.assertEqual(note.text, form_data['text'])
                self.assertEqual(note.slug, form_data['slug'])
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
        self.assertQuerysetEqual(
            Note.objects.all(), notes_initial, transform=lambda x: x)

    def test_author_can_delete_note(self):
        """Автор может удалить свою заметку."""
        notes_count_initial = Note.objects.count()
        self.assertRedirects(
            self.auth_author.delete(NOTE_DELETE_URL), SUCCESS_URL
        )
        self.assertEqual(Note.objects.count(), notes_count_initial - 1)
        self.assertFalse(Note.objects.filter(id=self.note.id).exists())

    def test_user_cant_delete_note_of_another_user(self):
        """Пользователь не может удалить чужую заметку."""
        notes_count_initial = Note.objects.count()
        self.assertEqual(self.auth_not_author.delete(
            NOTE_DELETE_URL).status_code, HTTPStatus.NOT_FOUND)
        self.assertIn(self.note, Note.objects.all())
        note = Note.objects.get(id=self.note.id)
        self.assertEqual(Note.objects.count(), notes_count_initial)
        self.assertEqual(note.slug, self.note.slug)
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.author, self.note.author)

    def test_author_can_edit_note(self):
        """Автор может редактировать свою заметку."""
        response = self.auth_author.post(NOTE_EDIT_URL, data=self.form_data)
        self.assertRedirects(response, SUCCESS_URL)
        note = Note.objects.get(id=self.note.id)
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.author, self.note.author)

    def test_user_cant_edit_note_of_another_user(self):
        """Пользователь не может править чужую заметку."""
        response = self.auth_not_author.post(
            NOTE_EDIT_URL, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note = Note.objects.get(id=self.note.id)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.slug, self.note.slug)
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.author, self.note.author)

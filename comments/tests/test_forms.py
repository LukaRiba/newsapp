from django.test import TestCase

from comments.forms import CommentForm, ReplyForm, EditForm

class CommentFormTests(TestCase):
    
    def test_no_data(self):
        form = CommentForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {'text': ['This field is required.']})

    def test_valid_data(self):
        form = CommentForm(data={'text': 'some text'})
        self.assertTrue(form.is_valid())

class ReplyFormTests(TestCase):
    
    def test_no_data(self):
        form = ReplyForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {'text': ['This field is required.']})
    
    def test_valid_data(self):
        form = CommentForm(data={'text': 'some text'})
        self.assertTrue(form.is_valid())

class EditFormTests(TestCase):
    
    def test_no_data(self):
        form = EditForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {'text': ['This field is required.']})
    
    def test_valid_data(self):
        form = CommentForm(data={'text': 'some text'})
        self.assertTrue(form.is_valid())

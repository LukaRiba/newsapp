import tempfile

from django.test import TestCase, override_settings

from my_newsapp.tests.factories import ArticleFactory
from comments.tests.factories import CommentFactory, ReplyFactory
from comments.models import Comment
from comments.templatetags import comments_tags

@override_settings(MEDIA_ROOT=tempfile.gettempdir() + '/')
class CommentsTagsTests(TestCase):

    def setUp(self):
        self.comments_owner = ArticleFactory()

    def test_for_comment_template_filter(self):
        first = CommentFactory(text='First comment', object_id=self.comments_owner.id)
        second = CommentFactory(text='Second comment', object_id=self.comments_owner.id)
        for comment in [first, second]:
            ReplyFactory.create_batch(size=2, parent=comment)
        replies = Comment.objects.filter(parent_id__isnull=False) # if parent_id is not None, it is reply
        filtered = comments_tags.for_comment(replies, first.id)
        self.assertEqual(list(filtered), list(first.replies.all()))

    def test_first_five_template_filter(self):
        CommentFactory.create_batch(size=6, object_id=self.comments_owner.id)
        comments = Comment.objects.all() # get queryset as create_batch returns list
        first_five = comments_tags.first_five(comments)
        self.assertEqual(list(first_five), list(comments[:5]))

    def test_substract_template_filter(self):
        CommentFactory.create_batch(size=3, object_id=self.comments_owner.id)
        comments = Comment.objects.all() # get queryset as create_batch returns list
        self.assertEqual(comments_tags.substract(comments, 1), 2)
        self.assertEqual(comments_tags.substract(comments, 3), 0)
        
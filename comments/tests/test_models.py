import tempfile

from django.test import TestCase, override_settings

from my_newsapp.tests.factories import ArticleFactory
from comments.models import Comment
from .factories import CommentFactory, ReplyFactory

@override_settings(MEDIA_ROOT=tempfile.gettempdir() + '/')
class CommentTests(TestCase):

    def setUp(self):
        self.comment_owner = ArticleFactory()

    def test_is_reply_method(self):
        comment = CommentFactory(object_id=self.comment_owner.id)
        reply = ReplyFactory(parent=comment)
        self.assertTrue(reply.is_reply())

    def test__str__method(self):
        comment = CommentFactory(object_id=self.comment_owner.id)
        self.assertEqual(comment.__str__(), comment.text)

    def test_ordering(self):
        CommentFactory.create_batch(size=5, object_id=self.comment_owner.id)
        comments = Comment.objects.all() # for ordering to take place, we have to query db
        for i in range( 0, comments.count() - 1):
            self.assertTrue(comments[i].pub_date > comments[i+1].pub_date)
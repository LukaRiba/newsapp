from django.test import TestCase, override_settings
from django.urls import reverse

from my_newsapp.tests.factories import ArticleFactory
from .factories import CommentFactory, ReplyFactory

@override_settings(ROOT_URLCONF = 'comments.tests.urls')
class CommentsOwnerViewTestsWithAnonymousUser(TestCase):
    '''
    Tests for how comments/base.html rendering for anonymous user
    '''
    
    def setUp(self):
        self.comments_owner = ArticleFactory(title='Comment Owner')
        self.url = reverse('comments-test', kwargs={'id': self.comments_owner.id})
        
    def test_response_status_code_is_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Comments')

    def test_login_link_is_displayed(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'Login')

    def test_no_comments(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'No comments yet.')

    def test_one_comment_without_replies(self):
        comment = CommentFactory(object_id=self.comments_owner.id)
        response = self.client.get(self.url)

        self.assertTrue(self.comments_owner.comments.count() == 1 )
        self.assertContains(response, '<strong>1 comment</strong>')
        for i in [comment.author, comment.pub_date.date().strftime('%b %d, %Y'), comment.text, 'No replies yet']:
            self.assertContains(response, i) 

    def test_one_comment_with_one_reply(self):
        comment = CommentFactory(object_id=self.comments_owner.id)
        reply = ReplyFactory(parent=comment)
        
        response = self.client.get(self.url)

        self.assertEqual(comment.object_id, reply.object_id)

        self.assertTrue(self.comments_owner.comments.count() == 1 )
        self.assertContains(response, '<strong>1 comments</strong>') # Ovo treba proci!! -> riješeno , vidi komentar iznad CommentsComtextMixin-a
        # self.assertContains(response, '<strong>2 comments</strong>') # Ovo nesmije proci a prolazi - i reply je shvaćen kao comment!!
        self.assertNotContains(response, 'No replies yet.')
        for i in ['Show 1 reply', reply.author, reply.pub_date.date().strftime('%b %d, %Y'), reply.text]:
            self.assertContains(response, i)

    # !!!!
    def test_one_comment_with_2_replies(self):
        comment = CommentFactory(object_id=self.comments_owner.id)
        ReplyFactory.create_batch(size=2, parent=comment)
        response = self.client.get(self.url)
        print(self.comments_owner.comments.all())
        
        self.assertTrue(self.comments_owner.comments.count() == 1 )
        self.assertContains(response, '<strong>1 comments</strong>')
        self.assertContains(response, 'Show 2 replies')

    def test_five_comments(self):
        pass

    def test_more_than_five_comments(self):
        pass

    

@override_settings(ROOT_URLCONF = 'comments.tests.urls')
class CommentsOwnerViewTestsWithLoggedUser(TestCase):
    pass
    

@override_settings(ROOT_URLCONF = 'comments.tests.urls')
class CreateCommentTests(TestCase):
    pass

@override_settings(ROOT_URLCONF = 'comments.tests.urls')
class CreateReplyTests(TestCase):
    pass

@override_settings(ROOT_URLCONF = 'comments.tests.urls')
class EditCommentOrReplyTests(TestCase):
    pass

@override_settings(ROOT_URLCONF = 'comments.tests.urls')
class DeleteCommentOrReplyTests(TestCase):
    pass

@override_settings(ROOT_URLCONF = 'comments.tests.urls')
class LoadMoreCommentsTests(TestCase):
    pass                



# from comments.tests.factories import CommentFactory, ReplyFactory
# from my_newsapp.tests.factories import ArticleFactory, CategoryFactory

# category = CategoryFactory(title='ajhf')
# comments_owner = ArticleFactory(title='Commedxnt Owner', category=category)
# comment = CommentFactory(object_id=comments_owner.id)
# reply = ReplyFactory(parent=comment)
# reply2 = ReplyFactory(parent=comment)
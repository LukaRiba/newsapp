import tempfile
from urllib.parse import quote_plus

from django.test import TestCase, TransactionTestCase, override_settings
from django.views.generic import TemplateView
from django.db.models.query import QuerySet
from django.contrib.auth.models import User
from django.urls import reverse
from django.conf import settings

from comments.views import CommentsContextMixin
from comments.models import Comment
from my_newsapp.models import Article
from my_newsapp.tests.factories import ArticleFactory
from .factories import CommentFactory, ReplyFactory
from comments.forms import CommentForm, ReplyForm, EditForm

@override_settings(MEDIA_ROOT=tempfile.gettempdir() + '/')
class CommentsContextMixinTests(TestCase):

    class TestView(CommentsContextMixin, TemplateView):
        model = Article

        #region comment
            # We must set kwargs like this, as if not AttributeError: 'TestView' object has no attribute 'kwargs' is
            # thrown. Kwargs are used in get_context_data to get comments_owner_id
        def __init__(self, **kwargs):
            self.kwargs = {'id': kwargs['id']}

    def setUp(self):
        self.comments_owner = ArticleFactory() # it must be the same as in mocked request session
        self.test_view = self.TestView(id=self.comments_owner.id)
        CommentFactory.create_batch(size=5, object_id=self.comments_owner.id)

    def test_get_context_data(self):
        
        context = self.test_view.get_context_data()

        for key in ['comments', 'owner_id', 'owner_model', 'comment_form', 'reply_form', 'edit_form', 'login_url']:
            self.assertTrue(key in context)
        self.assertIsInstance(context['comments'], QuerySet)
        self.assertIsInstance(context['comments'][0], Comment)
        self.assertEqual(context['comments'].count(), 5)
        self.assertEqual(context['owner_id'], self.comments_owner.id)
        self.assertEqual(context['owner_model'], 'Article')
        self.assertIsInstance(context['comment_form'], CommentForm)
        self.assertIsInstance(context['reply_form'], ReplyForm)
        self.assertIsInstance(context['edit_form'], EditForm)
        self.assertEqual(context['login_url'], settings.LOGIN_URL)
        
@override_settings(ROOT_URLCONF = 'comments.tests.urls', MEDIA_ROOT=tempfile.gettempdir() + '/')
class CommentsOwnerViewAnonymousUserTests(TestCase):
    '''
    Tests comments/base.html rendering for anonymous User
    '''
    
    def setUp(self):
        self.comments_owner = ArticleFactory(title='Comment Owner')
        self.url = reverse('comments-test', kwargs={'id': self.comments_owner.id})
        
    def test_response_status_code_is_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Comments')

    def test_login_link_is_displayed_and_comment_form_not(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'Login')
        self.assertNotContains(response, 'comment-form')

    def test_no_comments(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'No comments yet.')

    def test_one_comment_without_replies(self):
        comment = CommentFactory(object_id=self.comments_owner.id)
        response = self.client.get(self.url)

        self.assertEqual(self.comments_owner.comments.count(), 1)
        self.assertContains(response, '<strong>1 comment</strong>')
        for content in [comment.author, comment.pub_date.date().strftime('%b %d, %Y'), comment.text, 'No replies yet']:
            self.assertContains(response, content) 
        for content in ['reply-button', 'reply-form', 'edit-button', 'edit-form', 'delete-button']:
            self.assertNotContains(response, content) 

    def test_one_comment_with_one_reply(self):
        comment = CommentFactory(object_id=self.comments_owner.id)
        reply = ReplyFactory(parent=comment)
        response = self.client.get(self.url)

        self.assertContains(response, '<strong>1 comment</strong>') 
        self.assertNotContains(response, 'No replies yet.')
        self.assertEqual(comment.replies.count(), 1)
        for content in ['Show 1 reply', reply.author, reply.pub_date.date().strftime('%b %d, %Y'), reply.text]:
            self.assertContains(response, content)
        for content in ['reply-button', 'reply-form', 'edit-button', 'edit-form' 'delete-button']:
            self.assertNotContains(response, content) 

    def test_one_comment_with_2_replies(self):
        comment = CommentFactory(object_id=self.comments_owner.id)
        ReplyFactory.create_batch(size=2, parent=comment)
        response = self.client.get(self.url)
        
        self.assertContains(response, '<strong>1 comment</strong>')
        self.assertEqual(comment.replies.count(), 2)
        self.assertContains(response, 'Show 2 replies')

    # Next tests are not affected by user authenticification; outcome is the same 
    # for anonymous or logged user. So they are runned only in this TestCase.
    def test_no_load_more_button_if_less_than_6_comments(self):
        CommentFactory.create_batch(size=5, object_id=self.comments_owner.id)
        response = self.client.get(self.url)
        self.assertEqual(self.comments_owner.comments.count(), 5)
        self.assertContains(response, '<strong>5 comments</strong>')
        self.assertNotContains(response, '<button class="load-more-comments"')

    def test_load_more_button_6_comments(self):
        CommentFactory.create_batch(size=6, object_id=self.comments_owner.id)
        response = self.client.get(self.url)
        self.assertEqual(self.comments_owner.comments.count(), 6)
        self.assertContains(response, 'Load 1 more Comment')

    def test_load_more_button_7_comments(self):
        CommentFactory.create_batch(size=7, object_id=self.comments_owner.id)
        response = self.client.get(self.url)
        self.assertEqual(self.comments_owner.comments.count(), 7)
        self.assertContains(response, 'Load 2 more Comments')

    def test_load_more_button_10_comments(self):
        CommentFactory.create_batch(size=10, object_id=self.comments_owner.id)
        response = self.client.get(self.url)
        self.assertEqual(self.comments_owner.comments.count(), 10)
        self.assertContains(response, 'Load 5 more Comments')

    def test_load_more_button_15_comments(self):
        CommentFactory.create_batch(size=15, object_id=self.comments_owner.id)
        response = self.client.get(self.url)
        self.assertEqual(self.comments_owner.comments.count(), 15)
        self.assertContains(response, 'Load 10 more Comments')

    def test_load_more_button_16_comments(self):
        CommentFactory.create_batch(size=16, object_id=self.comments_owner.id)
        response = self.client.get(self.url)
        self.assertEqual(self.comments_owner.comments.count(), 16)
        self.assertContains(response, 'Load 10 more Comments')

@override_settings(ROOT_URLCONF = 'comments.tests.urls', MEDIA_ROOT=tempfile.gettempdir() + '/')
class CommentsOwnerViewLoggedUserTests(TestCase):
    '''
    Tests comments/base.html rendering for logged User
    '''
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')      
        self.comments_owner = ArticleFactory(title='Comment Owner')
        self.url = reverse('comments-test', kwargs={'id': self.comments_owner.id})
        self.client.login(username='testuser', password='testpass123')
        
    def test_response_status_code_is_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Comments')

    def test_comment_form_is_displayed(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        self.assertContains(response, '<form action="" method="POST" id="comment-form">')

    def test_no_comments(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'No comments yet.')

    def test_one_comment_without_replies_user_is_comment_author(self):
        comment = CommentFactory(object_id=self.comments_owner.id, author=self.user)
        response = self.client.get(self.url)

        self.assertEqual(self.user.comments.count(), 1) # self.user is author of comment
        self.assertContains(response, '<strong>1 comment</strong>')
        for content in [
            comment.author, comment.pub_date.date().strftime('%b %d, %Y'), comment.text, 'No replies yet',
            f'reply-button-{comment.id}', f'reply-form-{comment.id}', f'edit-button-{comment.id}',
            f'edit-form-{comment.id}', f'delete-button-{comment.id}'
        ]:
            self.assertContains(response, content) 

    def test_one_comment_without_replies_user_is_not_comment_author(self):
        comment = CommentFactory(object_id=self.comments_owner.id)
        response = self.client.get(self.url)

        self.assertContains(response, '<strong>1 comment</strong>')
        for content in [comment.author, comment.pub_date.date().strftime('%b %d, %Y'), comment.text, 'No replies yet',
            f'reply-button-{comment.id}', f'reply-form-{comment.id}']:
            self.assertContains(response, content)
        for content in [f'edit-button-{comment.id}', f'edit-form-{comment.id}', f'delete-button-{comment.id}']:
            self.assertNotContains(response, content)

    def test_one_comment_with_one_reply_user_is_reply_author(self):
        comment = CommentFactory(object_id=self.comments_owner.id)
        reply = ReplyFactory(parent=comment, author=self.user)
        response = self.client.get(self.url)

        self.assertContains(response, '<strong>1 comment</strong>') 
        self.assertNotContains(response, 'No replies yet.')
        self.assertEqual(comment.replies.count(), 1)
        for content in ['Show 1 reply', reply.author, reply.pub_date.date().strftime('%b %d, %Y'), reply.text,
            f'edit-button-{reply.id}', f'edit-form-{reply.id}', f'delete-button-{reply.id}']:
            self.assertContains(response, content)

    def test_one_comment_with_one_reply_user_is_not_reply_author(self):
        comment = CommentFactory(object_id=self.comments_owner.id)
        reply = ReplyFactory(parent=comment)
        response = self.client.get(self.url)

        self.assertContains(response, '<strong>1 comment</strong>') 
        self.assertNotContains(response, 'No replies yet.')
        self.assertEqual(comment.replies.count(), 1)
        for content in ['Show 1 reply', reply.author, reply.pub_date.date().strftime('%b %d, %Y'), reply.text]:
            self.assertContains(response, content)
        for content in [f'edit-button-{reply.id}', f'edit-form-{reply.id}', f'delete-button-{reply.id}']:
            self.assertNotContains(response, content)

@override_settings(
    ROOT_URLCONF = 'comments.tests.urls',
    LOGIN_URL = '/admin/login',
    MEDIA_ROOT=tempfile.gettempdir() + '/')
class CreateCommentTests(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')     
        self.url = reverse('comments:create-comment')
        self.comment_owner = ArticleFactory()
        self.data = {
            'text': 'comment text.',
            'owner_model': self.comment_owner.__class__.__name__, # == 'Article'
            'owner_id': self.comment_owner.id
        }

    def test_redirects_amonymous_user_to_login_url(self):
        self.client.logout()
        responses = [
            self.client.get(self.url, follow=True),
            self.client.post(self.url, data=self.data, follow=True),
            self.client.post(self.url, data=self.data, follow=True, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        ]
        for response in responses:
            # quote_plus replaces special characters in string using the %xx escape. It also does not have safe 
            # default to '/', so '/' character ia also replaced.
            self.assertRedirects(response, f'{settings.LOGIN_URL}/?next={quote_plus(self.url)}')
        self.assertEqual(Comment.objects.count(), 0)
            
    def test_error_405_if_request_method_not_POST(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(Comment.objects.count(), 0)

    # region : about client Exceptions 
        # From docs:  
        #     If you point the test client at a view that raises an exception, that exception will be visible in the
        #     test case. You can then use a standard try ... except block or assertRaises() to test for exceptions. The
        #     only exceptions that are not visible to the test client are Http404, PermissionDenied, SystemExit, and
        #     SuspiciousOperation. Django catches these exceptions internally and converts them into the appropriate
        #     HTTP response codes. In these cases, you can check response.status_code in your test. 
        # Thats why test fails if we assert that self.client.post(self.url) raises PermissionDenied. Instead, we have 
        # to check response.status_code which is 403 (Forbidden).
    def test_error_403_if_post_request_not_ajax(self):
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Comment.objects.count(), 0)

    def test_invalid_POST_data_empty_text_field(self):
        self.data.update({'text': ''})
        with self.assertRaises(ValueError) as context:
            self.client.post(self.url, data=self.data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            self.assertEqual(context.exception.msg,
                "The view comments.decorators.create_reply didn't return an HttpResponse object. It returned None instead.")

    def test_comment_created_with_valid_request(self):
        response = self.client.post(self.url, data=self.data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('comments/comments.html')
        self.assertEqual(Comment.objects.count(), 1)

        created_comment = Comment.objects.last()
        self.assertEqual(created_comment.object_id, self.comment_owner.id)
        
        for key in ['comments', 'reply_form', 'edit_form']:
            self.assertTrue(key in response.context)

        self.assertIsInstance(response.context['reply_form'], ReplyForm)
        self.assertIsInstance(response.context['edit_form'], EditForm)        

        for content in [created_comment.author, created_comment.pub_date.date().strftime('%b %d, %Y'), 
            created_comment.text, f'reply-form-{created_comment.id}', f'edit-form-{created_comment.id}',
            f'delete-button-{created_comment.id}']:
            self.assertContains(response, content) 

@override_settings(
    ROOT_URLCONF = 'comments.tests.urls',
    LOGIN_URL = '/admin/login',
    MEDIA_ROOT=tempfile.gettempdir() + '/')
class CreateReplyTests(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')     
        self.url = reverse('comments:create-reply')
        self.comment_owner = ArticleFactory()
        self.reply_owner = CommentFactory(object_id=self.comment_owner.id)
        self.data = {
            'text': 'reply text.',
            'parentId': self.reply_owner.id
        }

    def test_redirects_amonymous_user_to_login_url(self):
        self.client.logout()
        responses = [
            self.client.get(self.url, follow=True),
            self.client.post(self.url, data=self.data, follow=True,),
            self.client.post(self.url, data=self.data, follow=True, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        ]
        for response in responses:
            self.assertRedirects(response, f'{settings.LOGIN_URL}/?next={quote_plus(self.url)}')
        self.assertEqual(Comment.objects.count(), 1) # only reply_owner, no reply created
            
    def test_error_405_if_request_method_not_POST(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(Comment.objects.count(), 1)

    def test_error_403_if_post_request_not_ajax(self):
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Comment.objects.count(), 1)

    def test_invalid_POST_data_empty_text_field(self):
        self.data.update({'text': ''})
        with self.assertRaises(ValueError) as context:
            self.client.post(self.url, data=self.data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            self.assertEqual(context.exception.msg,
                "The view comments.decorators.create_reply didn't return an HttpResponse object. It returned None instead.")

    def test_invalid_POST_data_no_parentId(self):
        self.data.update({'parentId': ''})
        with self.assertRaises(ValueError) as context:
            self.client.post(self.url, data=self.data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            self.assertEqual(context.exception.msg,
                "The view comments.decorators.create_reply didn't return an HttpResponse object. It returned None instead.")

    def test_reply_created_with_valid_request(self):
        response = self.client.post(self.url, data=self.data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('comments/replies.html')
        self.assertEqual(Comment.objects.count(), 2)

        created_reply = Comment.objects.first() # last created, as ordering is -pub_date
        self.assertEqual(created_reply.object_id, self.reply_owner.id)
        
        for key in ['reply', 'edit_form', 'create_reply']:
            self.assertTrue(key in response.context)

        self.assertIsInstance(response.context['edit_form'], EditForm)        

        for content in [created_reply.author, created_reply.pub_date.date().strftime('%b %d, %Y'), 
            created_reply.text, f'edit-form-{created_reply.id}', f'delete-button-{created_reply.id}']:
            self.assertContains(response, content)

@override_settings(
    ROOT_URLCONF = 'comments.tests.urls',
    LOGIN_URL = '/admin/login',
    MEDIA_ROOT=tempfile.gettempdir() + '/')
class EditTests(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')     
        self.comment_owner = ArticleFactory()
        self.comment = CommentFactory(
            object_id=self.comment_owner.id, text='Initial text.')
        self.url = reverse('comments:edit', kwargs={'pk': self.comment.id})

    def test_redirects_amonymous_user_to_login_url(self):
        self.client.logout()
        responses = [
            self.client.get(self.url, follow=True),
            self.client.post(self.url, follow=True,),
            self.client.post(self.url, follow=True, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        ]
        for response in responses:
            self.assertRedirects(response, f'{settings.LOGIN_URL}/?next={quote_plus(self.url)}')
            
    def test_error_405_if_request_method_not_POST(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_error_403_if_post_request_not_ajax(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)

    def test_invalid_POST_data_empty_text_field(self):
        with self.assertRaises(ValueError) as context:
            self.client.post(self.url, data={'text': ''}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            self.assertEqual(context.exception.msg,
                "The view comments.decorators.create_reply didn't return an HttpResponse object. It returned None instead.")

    def test_successfully_edited_with_valid_request(self):
        response = self.client.post(self.url, data={'text': 'Updated text.'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        comment = Comment.objects.get(id=self.comment.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(comment.text, 'Updated text.')

@override_settings(
    ROOT_URLCONF = 'comments.tests.urls',
    LOGIN_URL = '/admin/login',
    MEDIA_ROOT=tempfile.gettempdir() + '/')
class DeleteTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')     
        self.comment_owner = ArticleFactory()
        self.comment = CommentFactory(
            object_id=self.comment_owner.id)
        self.url = reverse('comments:delete', kwargs={'pk': self.comment.id})

    def test_redirects_amonymous_user_to_login_url(self):
        self.client.logout()
        responses = [
            self.client.get(self.url, follow=True),
            self.client.post(self.url, follow=True,),
            self.client.post(self.url, follow=True, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        ]
        for response in responses:
            self.assertRedirects(response, f'{settings.LOGIN_URL}/?next={quote_plus(self.url)}')
            
    def test_error_405_if_request_method_not_POST(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_error_403_if_post_request_not_ajax(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)

    def test_successfully_deleted_with_valid_request(self):
        response = self.client.post(self.url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 204)
        with self.assertRaises(Comment.DoesNotExist) as context:
            Comment.objects.get(id=self.comment.id)
            self.assertEqual(context.exception.msg, 'Comment matching query does not exist.')

@override_settings(ROOT_URLCONF = 'comments.tests.urls', MEDIA_ROOT=tempfile.gettempdir() + '/')
class LoadMoreCommentsTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.comments_owner = ArticleFactory()
        CommentFactory.create_batch(size=6, object_id=self.comments_owner.id)
        # region : comments ordering
            # For right order (-pub_date), we must get comment objects from db after creating them with CommentFactory! 
            # If we say self.comments = CommentFactory.create_batch(size=6, object_id=self.comments_owner.id), 
            # and then use self.comments in tests, the order will be normal (first created first), so tests will fail.
            # So, first create, and then get from databasse. Also, as id sequences are reseted, when we run only this
            # TestCase, order will look like this in database:
            #                           id      
            #   self.comments[0]        6
            #   self.comments[1]        5
            #   self.comments[2]        4
            #   self.comments[3]        3
            #   self.comments[4]        2
            #   self.comments[5]        1
            # Because sequences are reseted only in this TestCase (in every test inside this TestCase ids of comments
            # created in setUp method will be the same), but not in others, if we run only this TestCase, tests will
            # pass and comments ids will be 1-6, but when we run all TestCases at once, ids will not be 1-6, because
            # this TestCase will continue sequence where other TestCases have stopped. Because of that ids are not
            # hardcoded - the ordering is important, not actual values. Order is reversed because -pub_date ordering
            # defined in Comment model. So, comment which is last created is the first one in table.
        self.comments = Comment.objects.all()
        self.url = reverse('comments:load-more-comments')

    def test_error_403_if_post_request_not_ajax(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)

    def test_2_visible_2_to_load(self):
        data = {
            'lastVisibleCommentId': self.comments[1].id,
            'numOfCommentsToLoad': 2,
            'owner_id': self.comments_owner.id
        }
        response = self.client.get(self.url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        for key in ['next_comments', 'reply_form', 'edit_form']:
            self.assertTrue(key in response.context)

        next_comments = response.context['next_comments']  
        self.assertEqual([comment.id for comment in next_comments], [comment.id for comment in self.comments[2:4]])

    def test_2_visible_6_to_load(self):
        # It is requested for 6 to load, but there are only 4 left to load
        data = {
            'lastVisibleCommentId': self.comments[1].id,
            'numOfCommentsToLoad': 6,
            'owner_id': self.comments_owner.id
        }
        response = self.client.get(self.url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        for key in ['next_comments', 'reply_form', 'edit_form']:
            self.assertTrue(key in response.context)

        next_comments = response.context['next_comments']
        self.assertEqual(
            [comment.id for comment in next_comments], [comment.id for comment in self.comments[2:6]])

    def test_no_comments_in_db(self):
        data = {
            'lastVisibleCommentId': self.comments[5].id,
            'numOfCommentsToLoad': 4,
            'owner_id': self.comments_owner.id
        }
        self.comments.delete()
        response = self.client.get(self.url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 400)

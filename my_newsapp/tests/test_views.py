import tempfile

from django.test import TestCase, RequestFactory, TransactionTestCase, override_settings
from django.urls import reverse
from django.views.generic import TemplateView
from django.db.models.query import QuerySet
from django.core.paginator import InvalidPage
from django.contrib.auth.models import User
from django.contrib.sessions.middleware import SessionMiddleware

from my_newsapp.views import NavigationContextMixin, HomeViewMixin
from my_newsapp.tests.factories import CategoryFactory, ArticleFactory, ImageFactory, FileFactory
from my_newsapp.models import Category, Article
from my_newsapp.utils import get_status_none_categories_random_ids, get_test_file, field_values
from my_newsapp.views import CategoryView, ArticleDetailView
from my_newsapp.forms import ArticleForm, ImageInlineFormSet, FileInlineFormSet

# from https://tech.people-doc.com/django-unit-test-your-views.html
def setup_view(view, request, *args, **kwargs):
    """Mimic as_view() returned callable, but returns view instance.
    args and kwargs are the same you would pass to ``reverse()``
    """
    view.request = request
    view.args = args
    view.kwargs = kwargs
    return view

def delete_article_test_files(article):
    for image in article.images.all():
        image.image.delete() 
    for file in article.files.all():
        file.file.delete() 

@override_settings(MEDIA_ROOT=tempfile.gettempdir() + '/')    
class NavigationContextMixinTests(TestCase):

    class TestView(NavigationContextMixin, TemplateView):
        pass

    def setUp(self):
        self.test_view = self.TestView()

    def test_no_category_objects(self):
        context = self.test_view.get_context_data()
        #comment
            # The queryset objects will not be identical if they are the result of different queries even if they 
            # have the same values in their result. If you convert the query set to a list first, you should be able 
            # to do a normal comparison (assuming they have the same sort order of course).
        self.assertEqual(list(context['categories']), list(Category.objects.all()))
        self.assertEqual(list(context['categories']), [])

    def test_with_category_objects(self):
        CategoryFactory.create_batch(size=3)
        context = self.test_view.get_context_data()
        self.assertEqual(list(context['categories']), list(Category.objects.all()))

@override_settings(MEDIA_ROOT=tempfile.gettempdir() + '/')       
class HomeViewMixinTests(TestCase):

    class TestView(HomeViewMixin, TemplateView):
        pass

    def setUp(self):
        CategoryFactory.create_batch(size=3)
        self.test_view = self.TestView()

    def rand_ids(self):
        return get_status_none_categories_random_ids()

    def test_get_primary_category_method__primary_category_exists(self):
        CategoryFactory(status='P')
        returned_category = self.test_view.get_primary_category(self.rand_ids())
        self.assertEqual(returned_category.status, 'P')

    def test_get_primary_category_method__primary_category_doesnt_exist(self):
        returned_category = self.test_view.get_primary_category(self.rand_ids())
        self.assertEqual(returned_category.status, None)
        self.assertTrue(returned_category in Category.objects.all())

    def test_get_primary_category_method__no_category_exists(self):
        Category.objects.all().delete()  # now rand_ids will be empty
        returned_category = self.test_view.get_primary_category(self.rand_ids())
        self.assertTrue(returned_category == None)

    def test_get_secondary_category_method__secondary_category_exists(self):
        CategoryFactory(status='S')
        returned_category = self.test_view.get_secondary_category(self.rand_ids())
        self.assertEqual(returned_category.status, 'S')

    def test_get_secondary_category_method__secondary_category_doesnt_exist(self):
        returned_category = self.test_view.get_secondary_category(self.rand_ids())
        self.assertEqual(returned_category.status, None)
        self.assertTrue(returned_category in Category.objects.all())

    def test_get_secondary_category_method__no_category_exists(self):
        Category.objects.all().delete() # now rand_ids will be empty
        returned_category = self.test_view.get_secondary_category(self.rand_ids())
        self.assertTrue(returned_category == None)

    def test_get_other_articles_method__only_status_none_categories(self):
        # create one article for each category
        for category in Category.objects.all():
            ArticleFactory(category=category)

        # test for 5 or less articles
        articles = self.test_view.get_other_articles(self.rand_ids())
        self.assertTrue(articles.count() == 3)

        # create 2 more articles for each category
        for category in Category.objects.all():
            ArticleFactory.create_batch(size=2, category=category)

        # test for more than 5 articles
        articles = self.test_view.get_other_articles(self.rand_ids())
        self.assertTrue(Article.objects.count() == 9) # now there are 9 articles whose category has status=None
        self.assertTrue(articles.count() == 6) # but method returns maximum 6 articles

        for article in articles:
            self.assertTrue(article.category.status == None)

    def test_get_other_articles_method__primary_and_secondary_category_exist(self):
        CategoryFactory(status='P')
        CategoryFactory(status='S')

        # creates 10 articles, 2 for each of 5 categories
        for category in Category.objects.all():
            ArticleFactory.create_batch(size=2, category=category)

        articles = self.test_view.get_other_articles(self.rand_ids())
        self.assertTrue(articles.count() == 6) # only 6 articles belong to categories with status=None
        for article in articles:
            self.assertTrue(article.category.status == None)

    def test_get_other_articles_method__no_articles_exists(self):
        articles = self.test_view.get_other_articles(self.rand_ids())

        self.assertEqual(articles.count(), 0)

    def test_get_other_articles_method__no_category_exist(self):
        Category.objects.all().delete() # now rand_ids will be empty
        articles = self.test_view.get_other_articles(self.rand_ids())

        self.assertEqual(articles.count(), 0)
        

    def test_context_primary_and_secondary_category_objects_exist(self):
        CategoryFactory(status='P')
        CategoryFactory(status='S')

        # creates 10 articles, 2 for each of 5 categories
        for category in Category.objects.all():
            ArticleFactory.create_batch(size=2, category=category)

        context = self.test_view.get_context_data()
        other_articles = context['other_articles']
        primary_category = context['primary_category']
        secondary_category = context['secondary_category']

        self.assertIsInstance(primary_category, Category)
        self.assertEqual(primary_category.status, 'P')

        self.assertIsInstance(secondary_category, Category)
        self.assertEqual(secondary_category.status, 'S')

        self.assertIsInstance(other_articles, QuerySet)
        for article in other_articles:
            self.assertIsInstance(article, Article)
            self.assertEqual(article.category.status, None)
        self.assertEqual(other_articles.count(), 6)

    def test_context_only_category_objects_with_status_none_exist(self):
        # creates 6 articles, 2 for each of 3 categories
        for category in Category.objects.all():
            ArticleFactory.create_batch(size=2, category=category)

        context = self.test_view.get_context_data()
        other_articles = context['other_articles']
        primary_category = context['primary_category']
        secondary_category = context['secondary_category']

        self.assertIsInstance(primary_category, Category)
        self.assertEqual(primary_category.status, None)

        self.assertIsInstance(secondary_category, Category)
        self.assertEqual(secondary_category.status, None)

        self.assertNotEqual(primary_category, secondary_category)

        self.assertIsInstance(other_articles, QuerySet)
        for article in other_articles:
            self.assertIsInstance(article, Article)
            self.assertEqual(article.category.status, None)
            self.assertNotEqual(article.category, primary_category)
            self.assertNotEqual(article.category, secondary_category)
        self.assertEqual(other_articles.count(), 2) 

@override_settings(MEDIA_ROOT=tempfile.gettempdir() + '/')
class HomeViewTests(TestCase):

    def setUp(self):  
        # creates a new user with a correctly hashed password.
        User.objects.create_user(username='testuser', password='testpass123')      
        CategoryFactory.create_batch(size=3)
        CategoryFactory(status='P')
        CategoryFactory(status='S')

        for category in Category.objects.all():
            ArticleFactory.create_batch(size=4, category=category)
       
        self.response = self.client.get('/news/home/')

    def test_context_is_in_response(self):
        self.assertTrue('categories' in self.response.context)
        self.assertTrue('primary_category' in self.response.context)
        self.assertTrue('secondary_category' in self.response.context)
        self.assertTrue('other_articles' in self.response.context)

    def test_home_view_loads_user(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed('my_newsapp/home.html')
        self.assertTemplateUsed('my_newsapp/navigation.html')

    # as navbar is shared throughout views via NavigationContextMixin, this is tested for this view only
    def test_navbar_has_login_link_for_anonymous_user(self):
        self.assertContains(self.response, '<a class="nav-link" href="/news/login/?next=/news/home/">Login</a>')

    # as navbar is shared throughout views via NavigationContextMixin, this is tested for this view only
    def test_navbar_has_logout_link_for_logged_user(self):
        self.client.login(username='testuser', password='testpass123') # login client as created user
        response = self.client.get('/news/home/') # self.response in setUp is made with unlogged client
        self.assertContains(response, '<a class="nav-link" href="/news/logout/">Logout</a>')

    def test_contains_primary_category_articles(self):
        self.assertContains(self.response, self.response.context['primary_category'].title)
        for article in self.response.context['primary_category'].articles.all()[:3]:
            self.assertContains(self.response, article.title)
            self.assertContains(self.response, article.short_description)
            # strftime() stringifies date to format rendered in templates, which is the same as in settings.DATE_FORMAT
            self.assertContains(self.response, article.pub_date.date().strftime('%b %d, %Y'))

    def test_contains_secondary_category_articles(self):
        self.assertContains(self.response, self.response.context['secondary_category'].title)
        for article in self.response.context['secondary_category'].articles.all()[:2]:
            self.assertContains(self.response, article.title)
            self.assertContains(self.response, article.short_description)
            self.assertContains(self.response, article.pub_date.strftime('%b %d, %Y'))

    def test_contains_other_articles(self):
        for article in self.response.context['other_articles']:
            self.assertContains(self.response, article.title)
            self.assertNotContains(self.response, article.short_description)
            self.assertContains(self.response, article.pub_date.strftime('%b %d, %Y'))

@override_settings(MEDIA_ROOT=tempfile.gettempdir() + '/')
class LatestArticlesViewTests(TestCase):

    def setUp(self):
        ArticleFactory.create_batch(size=8)
        
    def test_response_contents_are_equal(self):
        response = self.client.get('/news/latest-articles/')
        response_page_one_querystring = self.client.get('/news/latest-articles/?page=1')
        self.assertEqual(response.content, response_page_one_querystring.content)

    def test_paginator_page_1(self):
        page_1 = self.client.get('/news/latest-articles/?page=1')
        self.assertEqual(page_1.status_code, 200)
        self.assertTemplateUsed('my_newsapp/latest_articles.html')
        self.assertTemplateUsed('my_newsapp/navigation.html')
        self.assertContains(page_1, 'Latest Articles')
        self.assertTrue('articles' in page_1.context)
        self.assertEqual(len(page_1.context['articles']), 5)

    def test_paginator_page_2(self):
        page_2 = self.client.get('/news/latest-articles/?page=2')
        self.assertEqual(page_2.status_code, 200)
        self.assertTemplateUsed('my_newsapp/latest_articles.html')
        self.assertTemplateUsed('my_newsapp/navigation.html')
        self.assertContains(page_2, 'Latest Articles')
        self.assertTrue('articles' in page_2.context)
        self.assertEqual(len(page_2.context['articles']), 3) # as paginate_by = 5, 3 articles are left for 3rd page.
    
    def test_paginator_non_existing_page(self):
        page_3 = self.client.get('/news/latest-articles/?page=3')
        self.assertTemplateNotUsed('my_newsapp/latest_articles.html')
        self.assertTemplateUsed('my_newsapp/navigation.html')
        self.assertEqual(page_3.status_code, 404)
        self.assertRaises(InvalidPage)

@override_settings(MEDIA_ROOT=tempfile.gettempdir() + '/')
class CategoryViewTests(TestCase):

    def setUp(self):
        self.test_category = CategoryFactory(title='Test Category', slug='test-category')
        ArticleFactory.create_batch(size=8, category=self.test_category)
        self.url = reverse('my_newsapp:category', kwargs={'slug': self.test_category.slug})

    def test_response_contents_are_equal(self):
        response = self.client.get(self.url)
        response_page_one_querystring = self.client.get(self.url + '?page=1')
        self.assertEqual(response.content, response_page_one_querystring.content)

    def test_paginator_page_1(self):
        page_1 = self.client.get(self.url + '?page=1')
        self.assertEqual(page_1.status_code, 200)
        self.assertTemplateUsed('my_newsapp/category.html')
        self.assertTemplateUsed('my_newsapp/navigation.html')
        self.assertContains(page_1, self.test_category.title)
        self.assertTrue('articles' in page_1.context)
        self.assertEqual(len(page_1.context['articles']), 5)

    def test_paginator_page_2(self):
        page_2 = self.client.get(self.url + '?page=2')
        self.assertEqual(page_2.status_code, 200)
        self.assertTemplateUsed('my_newsapp/category.html')
        self.assertTemplateUsed('my_newsapp/navigation.html')
        self.assertContains(page_2, self.test_category.title)
        self.assertTrue('articles' in page_2.context)
        self.assertEqual(len(page_2.context['articles']), 3) # as paginate_by = 5, 3 articles are left for 3rd page.
    
    def test_paginator_non_existing_page(self):
        page_3 = self.client.get(self.url + '?page=3')
        self.assertTemplateNotUsed('my_newsapp/category.html')
        self.assertTemplateUsed('my_newsapp/navigation.html')
        self.assertEqual(page_3.status_code, 404)
        self.assertRaises(InvalidPage)

    def test_get_category_method(self):
        # as get_category() doesn't use request object, we create one with empty path, just to pass it to setup_view().
        request = RequestFactory().get('/')
        slug = self.test_category.slug
        view = setup_view(CategoryView(), request, slug=slug)
        
        self.assertEqual(view.get_category(), Category.objects.get(title=self.test_category.title))

    def test_get_queryset_method(self):
        ArticleFactory.create_batch(size=3, category=self.test_category)

        request = RequestFactory().get('/')
        slug = self.test_category.slug
        view = setup_view(CategoryView(), request, slug=slug)

        self.assertEqual(list(view.get_queryset()), list(Article.objects.filter(category=view.get_category())))

@override_settings(MEDIA_ROOT=tempfile.gettempdir() + '/')
class ArticleDetailViewTests(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')      
        self.article = ArticleFactory(title='Test Article')
        ImageFactory(article=self.article)
        self.url = reverse('my_newsapp:article-detail', kwargs={'category': self.article.category.slug, 
            'id': self.article.id, 'slug': self.article.slug})
        self.response = self.client.get(self.url)

    def article_detail_view_loads(self):
        self.assertTrue('article' in self.response.context)
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateNotUsed('my_newsapp/detail.html')
        self.assertTemplateUsed('my_newsapp/navigation.html')
        self.assertTemplateUsed('comments/base.html')

    def article_fields_are_in_response(self):
        self.assertContains(self.response, self.article.title)
        self.assertNotContains(self.response, self.article.short_description)
        # replace('\n', '<br />') because linebreaks is applied in template
        self.assertContains(self.response, self.article.text.replace('\n', '<br />'))
        self.assertContains(self.response, self.article.pub_date.strftime('%b %d, %Y'))
        self.assertContains(self.response, self.article.author)
        self.assertContains(self.response, self.article.category)

    def article_category_image_is_in_response(self):
        self.assertContains(self.response, self.article.category.image)
        
    def article_image_is_in_response(self):
        self.assertEqual(len(self.article.images.all()), 1)
        for image in self.article.images.all():
            self.assertContains(self.response, image.image)

    def test_no_carousel_gallery_for_one_image(self):
        self.assertTemplateUsed('my_newsapp/snippets/image_carousel.html')

    def test_carousel_gallery_when_article_has_more_than_one_images(self):
        ImageFactory(article=self.article)
        response = self.client.get(self.url) # get new response object which now has newly created image in it
        
        self.assertEqual(len(self.article.images.all()), 2)
        self.assertTemplateUsed(response, 'my_newsapp/snippets/image_carousel.html')
        self.assertContains(response, '<div id="gallery" class="carousel slide" data-ride="carousel">')

    def test_article_has_no_attached_files(self):
        self.assertNotContains(self.response, 'Attachments')

    def test_article_has_attached_files(self):
        FileFactory(article=self.article)
        FileFactory(article=self.article)
        response = self.client.get(self.url) # get new response object which now has newly created files in it

        self.assertContains(response, 'Attachments')
        for file in self.article.files.all():
            self.assertContains(response, file.name())

    def test_EditArticle_and_Delete_buttons_shown_when_user_is_author_of_the_article_and_loggend_in(self):
        self.article.author = self.user
        self.article.save()
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)

        self.assertContains(response, '<a href="/news/edit-article/{}/">Edit Article</a>'.format(self.article.id))
        self.assertContains(response, 'article-delete-button')
        self.assertTemplateUsed('my_newsapp/snippets/article_delete_modal.html')

    def test_EditArticle_and_Delete_buttons_not_shown_when_user_not_author_of_the_article(self):
        # not logged in
        self.assertNotContains(self.response, '<a href="/news/edit-article/{}/">Edit Article</a>'.format(self.article.id))
        self.assertNotContains(self.response, 'article-delete-button')
        self.assertTemplateNotUsed('my_newsapp/snippets/article_delete_modal.html')

        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        
        # logged in
        self.assertNotContains(response, '<a href="/news/edit-article/{}/">Edit Article</a>'.format(self.article.id))
        self.assertNotContains(response, 'article-delete-button')
        self.assertTemplateNotUsed('my_newsapp/snippets/article_delete_modal.html')

    # if session isn't addedv-> AttributeError: 'WSGIRequest' object has no attribute 'session'
    def test_get_method(self):
        request = RequestFactory().get('/')
        
        # adding session
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()

        # setup view
        view = setup_view(ArticleDetailView(), request, category=self.article.category.slug, 
            id=self.article.id, slug=self.article.slug)

        # run method
        view.get(request)

        # check
        self.assertTrue('comments_owner_model_name' in request.session)
        self.assertTrue('comments_owner_id' in request.session)

    def test_request_session_variables(self):
        session = self.client.session
        
        self.assertEqual(session['comments_owner_model_name'], 'Article')
        self.assertEqual(session['comments_owner_id'], str(self.article.id))

@override_settings(MEDIA_ROOT=tempfile.gettempdir() + '/')
class CreateArticleViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.url = reverse('my_newsapp:create-article')

        # initial empty form and formset fields when page loads
        self.initial_data = {
            # ArticleForm
            'title': '', 
            'short_description': '', 
            'text': '', 
            'category': '', 
            
            # ImageFormSet
            'images-TOTAL_FORMS': '1', 
            'images-INITIAL_FORMS': '0', 
            'images-MIN_NUM_FORMS': '0', 
            'images-MAX_NUM_FORMS': '20', 
            'images-0-image': '', 
            'images-0-description': '', 
            
            # FileFormSet
            'files-TOTAL_FORMS': '1', 
            'files-INITIAL_FORMS': '0', 
            'files-MIN_NUM_FORMS': '0', 
            'files-MAX_NUM_FORMS': '20', 
            'files-0-file': '', 
        } 

        self.category = CategoryFactory(slug='testing')

    def test_redirects_anonymous_user_to_login_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('my_newsapp:login') + '?next=' + self.url)

        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('my_newsapp:login') + '?next=' + self.url)

    def test_loads_for_logged_in_user(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('my_newsapp/create_article.html')
        self.assertTemplateUsed('my_newsapp/snippets/navigation.html')

    def test_form_and_formsets_are_in_context(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        self.assertTrue('form' in response.context)
        self.assertIsInstance(response.context['form'], ArticleForm)
        self.assertTrue('image_formset' in response.context)
        self.assertIsInstance(response.context['image_formset'], ImageInlineFormSet)
        self.assertTrue('file_formset' in response.context)
        self.assertIsInstance(response.context['file_formset'], FileInlineFormSet)

    def test_post_with_no_form_and_formset_data(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(self.url, self.initial_data)
        self.assertEqual(response.status_code, 200)

        #check ArticleForm
        article_form = response.context['form'] 
        self.assertFalse(article_form.is_valid())
        for field in article_form.fields:
            self.assertFormError(response, 'form', field, 'This field is required.')
        self.assertContains(response, 'This field is required.', count=4)

        # check ImageFormSet
        image_formset = response.context['image_formset']
        self.assertFalse(image_formset.is_valid())
        self.assertContains(response, 'You have to upload at least one image.')

        # check FileFormSet - is invalid only when duplicate files are updated
        file_formset = response.context['file_formset']
        self.assertTrue(file_formset.is_valid())

        # check article not created
        self.assertEqual(Article.objects.count(), 0)

    def test_post_with_valid_form_but_no_image_uploaded_and_duplicate_files(self):
        self.client.login(username='testuser', password='testpass123')
        # becase dict's update() doesn't return anything, we must assign initial_data to data first
        data = self.initial_data
        data.update({
            'title': 'test article', 
            'short_description': 'this is a test article data', 
            'text': 'some text', 
            'category': self.category.id,

            # upload 2 identical files for file_formset to be invalid
            'files-TOTAL_FORMS': '2', 
            'files-0-file': get_test_file('test_doc_file.doc'),
            'files-1-file': get_test_file('test_doc_file.doc'),   
        })

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)

        self.assertTrue(response.context['form'].is_valid())
        self.assertFalse(response.context['image_formset'].is_valid())
        self.assertContains(response, 'You have to upload at least one image.')
        self.assertFalse(response.context['file_formset'].is_valid())
        self.assertContains(response, 'You have uploaded duplicate files. Files have to be unique.')

        # check article not created
        self.assertEqual(Article.objects.count(), 0)

    def test_post_with_valid_form_with_no_image_uploaded_and_image_formsets_have_only_description(self):
        self.client.login(username='testuser', password='testpass123')
        data = self.initial_data
        data.update({
            'title': 'test article', 
            'short_description': 'this is a test article data', 
            'text': 'some text', 
            'category': self.category.id,

            # upload 2 identical files for file_formset to be invalid
            'images-TOTAL_FORMS': '2', 
            'images-0-image': '', 
            'images-0-description': 'first image',
            'images-1-image': '', 
            'images-1-description': 'second image', 
        })

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)

        self.assertTrue(response.context['form'].is_valid())
        self.assertFalse(response.context['image_formset'].is_valid())
        self.assertContains(response, 'You cannot have description if image is not choosen.', 2)
        self.assertTrue(response.context['file_formset'].is_valid())
        # Even if no image is uploaded, there is no error message 'You have to upload at least one image.' because
        # if there are errors in ImageForms, ImageFormSet is not validated (see ImageInlineFormSet clean()).
        self.assertNotContains(response, 'You have to upload at least one image.')

        # check article not created
        self.assertEqual(Article.objects.count(), 0)
    
    def test_post_with_valid_form_with_image_uploaded_but_other_image_formsets_have_only_description(self):
        self.client.login(username='testuser', password='testpass123')
        # becase dict's update() doesn't return anything, we must assign initial_data to data first
        data = self.initial_data
        data.update({
            'title': 'test article', 
            'short_description': 'this is a test article data', 
            'text': 'some text', 
            'category': self.category.id,

            # upload 2 identical files for file_formset to be invalid
            'images-TOTAL_FORMS': '3', 
            'images-0-image': get_test_file('test_image.png'), 
            'images-0-description': 'first image',
            'images-1-image': '', 
            'images-1-description': 'second image',
            'images-2-image': '', 
            'images-2-description': 'third image',      
        })

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)

        self.assertTrue(response.context['form'].is_valid())
        self.assertFalse(response.context['image_formset'].is_valid())
        self.assertContains(response, 'You cannot have description if image is not choosen.', 2)
        self.assertTrue(response.context['file_formset'].is_valid())

        # check article not created
        self.assertEqual(Article.objects.count(), 0)

    def test_post_with_invalid_form_but_valid_formsets_data(self):
        self.client.login(username='testuser', password='testpass123')
        data = self.initial_data
        data.update({
            'title': 'test article', 
            'short_description': 'this is a test article data', 
            'text': 'some text', 
            'category': 'here should be category id',

            'images-0-image': get_test_file('test_image.png'),
 
            'files-0-file': get_test_file('test_doc_file.doc'),
        })

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)

        self.assertFalse(response.context['form'].is_valid())
        self.assertTrue(response.context['image_formset'].is_valid())
        self.assertTrue(response.context['file_formset'].is_valid())

        # check article not created
        self.assertEqual(Article.objects.count(), 0)

    def test_post_with_article_title_that_already_exists(self):
        ArticleFactory(title='test article')

        self.client.login(username='testuser', password='testpass123')

        data = self.initial_data
        data.update({
            'title': 'test article', 
            'short_description': 'this is a test article', 
            'text': 'some text', 
            'category': self.category.id,

            'images-0-image': get_test_file('test_image.png'),
 
            'files-0-file': get_test_file('test_doc_file.doc'),
        })

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)

        self.assertFormError(response, 'form', 'title', 'Article with this Title already exists.')
        self.assertContains(response, 'Article with this Title already exists.')

         # check article not created through post
        self.assertEqual(Article.objects.count(), 1)

    def test_post_with_valid_data(self):
        self.client.login(username='testuser', password='testpass123')
        data = self.initial_data
        data.update({
            'title': 'test article', 
            'short_description': 'this is a test article data', 
            'text': 'some text', 
            'category': self.category.id,

            'images-0-image': get_test_file('test_image.png'),
 
            'files-0-file': get_test_file('test_doc_file.doc'),
        })

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)

        # check article not created
        try:
            article = Article.objects.get(title='test article')
        except Article.DoesNotExist:
            self.fail('article is not created')

        self.assertEqual(article.images.first().__str__(), 'test_image.png')
        self.assertEqual(article.files.first().name(), 'test_doc_file.doc')

        self.assertRedirects(response, reverse('my_newsapp:article-detail', kwargs={
            'category': article.category.slug, 
            'id': article.id, 
            'slug': article.slug
        }))

        # deletes uploaded files from tempdir
        article.images.first().image.delete()
        article.files.first().file.delete()

@override_settings(MEDIA_ROOT=tempfile.gettempdir() + '/')
class EditArticleViewTests(TransactionTestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.article = ArticleFactory(title='test article')
        ImageFactory.create_batch(size=2, article=self.article)
        FileFactory.create_batch(size=2, article=self.article)
        self.url = reverse('my_newsapp:edit-article', kwargs={'id': self.article.id})
        self.initial_values = field_values(self.article)

        self.initial_data = {
            # ArticleForm
            'title': self.article.title, 
            'short_description': self.article.short_description, 
            'text': self.article.text, 
            'category': self.article.category.id, 
            
            # ImageFormSet
            'images-TOTAL_FORMS': '1', 
            'images-INITIAL_FORMS': '0', 
            'images-MIN_NUM_FORMS': '0', 
            'images-MAX_NUM_FORMS': '20', 
            'images-0-image': '', 
            'images-0-description': '', 
            
            # FileFormSet
            'files-TOTAL_FORMS': '1', 
            'files-INITIAL_FORMS': '0', 
            'files-MIN_NUM_FORMS': '0', 
            'files-MAX_NUM_FORMS': '20', 
            'files-0-file': '', 

            # images and files selected for deletion
            'image-checkbox[]': [],
            'file-checkbox[]': []
        } 

    # comment
        # tearDown() runs after every test method, but tearDownClass only after all test methods have been executed.
        # But for some reason, this class method causes error:
        #       "django.db.transaction.TransactionManagementError: An error occurred in the current transaction. You can't 
        #       execute queries until the end of the 'atomic' block", which gets throwned by other classes from this file,
        # for example HomeViewTests, LatestArticlesViewTests and so on. 
        # @classmethod
        # def tearDownClass(cls):
        #     remove_auto_generated_example_files()
    def tearDown(self):
        delete_article_test_files(self.article)

    def test_redirects_anonymous_user_to_login_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('my_newsapp:login') + '?next=' + self.url)

        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('my_newsapp:login') + '?next=' + self.url)

    def test_loads_for_logged_in_user(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        
        for template in response.templates:
            self.assertTemplateUsed(response, template.name)

        # check ArticleForm initial data
        article_form = response.context['form']
        self.assertEqual(article_form.instance, self.article)

        # compare initial form field values correspond article attribute (field) values.
        for field in article_form:
            # because category field is html select element, whose option elements have values of category.id, not title 
            if field.name == 'category': 
                self.assertEqual(field.value(), self.article.category.id)
            else:
                self.assertEqual(field.value(), getattr(self.article, field.name))

        self.assertContains(response, '<div class="col-md-6 current-images">')
        self.assertContains(response, '<div class="col-md-6 current-files">')

    def test_post_when_nothing_edited(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(self.url, self.initial_data)

        # get field values again now the article is updated
        # comment - important
            # We must use updated_article here (get article again from db after client.post) because than we are sure
            # that we get correct updated values, which we will not with field_values(self.article); we would get 
            # pre-update values (for non relational fields - everyone except images and files -> se comment in
            # test_post_when_article_form_fields_change). Test will still pass here hovever, because we are checking
            # that values are not changed if we don't change them in the view, but we would then comparing old values with
            # old values which is not what is intended, and in next test errors would arise.    
        updated_article = Article.objects.first() 
        updated_values = field_values(updated_article)

        self.assertRedirects(response, reverse('my_newsapp:article-detail', kwargs={
            'category': updated_article.category.slug, 
            'id': updated_article.id, 
            'slug': updated_article.slug
        }))
        
        # check that self.article and updated_article are actually the same instance
        self.assertEqual(self.article, updated_article)

        # check that article field values, including images and files didn't change
        self.assertFalse(any([self.initial_values[field] != updated_values[field] for field in self.initial_values.keys()]))

    def test_post_when_article_form_fields_change(self):
        data = self.initial_data
        data.update({
            'title': 'New Title', 
            'short_description': 'new description',
            'text': 'this is changed text',
            'category': CategoryFactory(title='New Category').id
        })

        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(self.url, data)

        # get field values again now the article is updated
        # comment - important
            # If field_values() called with self.article, old values ar getted even after article is updated. So, we get
            # article again from database (updated_article), and now we get updated values. But images and files fields
            # are updated if within self.article, probably because in field_values() we get them using all() method, which
            # queryes db, and other field values are getted from self.article directly without querying database ???
            # For example, if we don't get updated from db (Article.objects.first() ) article in 
            # test_post_upload_new_article_images_and_files, and use self.article instead updated_article, test will
            # pass and field_values(self.article) would have uploaded image and file in article's images and files
            # fields. ??? 
            # The same is for deleting files and images - we don't have to use updated_article, we can use self.article.
        updated_article = Article.objects.first() 
        updated_values = field_values(updated_article)

        self.assertRedirects(response, reverse('my_newsapp:article-detail', kwargs={
            'category': updated_article.category.slug, 
            'id': updated_article.id, 
            'slug': updated_article.slug
        }))

        # check that article's fields have been updated 
        self.assertNotEqual(self.initial_values['title'], updated_values['title'])
        self.assertEqual(updated_article.title, 'New Title')

        self.assertNotEqual(self.initial_values['short_description'], updated_values['short_description'])
        self.assertEqual(updated_article.short_description, 'new description')

        self.assertNotEqual(self.initial_values['text'], updated_values['text'])
        self.assertEqual(updated_article.text, 'this is changed text')

        self.assertNotEqual(self.initial_values['category'], updated_values['category'])
        self.assertEqual(updated_article.category.title, 'New Category')

    def test_post_upload_new_article_images_and_files(self):
        data = self.initial_data
        data.update({
            'images-0-image': get_test_file('test_image.png'),
            'files-0-file': get_test_file('test_doc_file.doc') # .txt file doesn't upload for some reason. Do not use it!
        })
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(self.url, data)

        # get field values again now the article is updated
        updated_article = Article.objects.first() 
        updated_values = field_values(updated_article)
       
        self.assertRedirects(response, reverse('my_newsapp:article-detail', kwargs={
            'category': updated_article.category.slug, 
            'id': updated_article.id, 
            'slug': updated_article.slug
        }))

        # check that one image and one file have been added
        self.assertNotEqual(self.initial_values['images'], updated_values['images'])
        self.assertEqual(updated_article.images.count(), 3)
        self.assertNotEqual(self.initial_values['files'], updated_values['files'])
        self.assertEqual(updated_article.files.count(), 3)

    def test_post_delete_some_of_article_images_and_files(self):
        data = self.initial_data
        data.update({
            # lists of images/files ids
            'image-checkbox[]': ['1'],
            'file-checkbox[]': ['2']
        })
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(self.url, data)

        self.assertRedirects(response, reverse('my_newsapp:article-detail', kwargs={
            'category': self.article.category.slug, 
            'id': self.article.id, 
            'slug': self.article.slug
        }))

        # check that one image is deleted
        self.assertEqual(self.article.images.count(), 1)
        # check that all files are deleted
        self.assertEqual(self.article.files.count(), 1)
        
    def test_post_delete_all_article_files(self):
        data = self.initial_data
        data.update({
            'file-checkbox[]': ['1' ,'2']
        })
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(self.url, data)

        self.assertRedirects(response, reverse('my_newsapp:article-detail', kwargs={
            'category': self.article.category.slug, 
            'id': self.article.id, 
            'slug': self.article.slug
        }))

        # check that all files are deleted
        self.assertEqual(self.article.files.count(), 0)

    def test_post_delete_all_images_while_not_uploading_new_image(self):
        data = self.initial_data
        data.update({
            'image-checkbox[]': ['1', '2']
        })
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 200)

        image_formset = response.context['image_formset']
        self.assertFalse(image_formset.is_valid())
        # everything passes ok, formset is invalid, but message is not shown ??? fix that!
        self.assertContains(response, 'Article must have at least one image. Upload new one if deleting all existing ones.')

    def test_post_delete_all_images_and_upload_new_image(self):
        data = self.initial_data
        data.update({
            'image-checkbox[]': ['1', '2'], # delete all images
            'images-0-image': get_test_file('test_image.png')
        })
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(self.url, data)

        self.assertRedirects(response, reverse('my_newsapp:article-detail', kwargs={
            'category': self.article.category.slug, 
            'id': self.article.id, 
            'slug': self.article.slug
        }))

        # check that old images are deletet and new one is uploaded 
        self.assertEqual(self.article.images.count(), 1)
        self.assertEqual(self.article.images.first().image, 'test_image.png')

@override_settings(MEDIA_ROOT=tempfile.gettempdir() + '/')
class DeleteArticleViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.article = ArticleFactory(title='test article')
        self.url = reverse('my_newsapp:delete-article', kwargs={'id': self.article.id})

    def test_get_with_anonymous_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_get_with_logged_user(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_article_deletion_with_anonymous_user(self):
        response = self.client.post(self.url)

        # redirect to login page
        self.assertRedirects(response, '{}{}{}{}'.format(
            reverse('my_newsapp:login'), '?next=/news/delete-article/', self.article.id, '/')
        )

    def test_article_deletion_with_logged_user(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(self.url)

        # check that article is deleted
        with self.assertRaises(Article.DoesNotExist) as cm: 
            Article.objects.get(title='test article')
            self.assertEqual(cm.exception.msg, 'Article matching query does not exist.')

        # article is deleted -> redirect to home page
        self.assertRedirects(response, reverse('my_newsapp:home'))
        
class MyNewsappLoginViewTests(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.url = reverse('my_newsapp:login')

    def test_get(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '...please login or continue as guest')

    def test_post_with_empty_fields(self):
        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '...please login or continue as guest')
        # comment
            # two messages, one for every field. Shows up when html required attributes are disabled in fields.
            # If requred attributes are enabled, page doesn't reload and we se pop ups which say 'Please fill out
            # this field'. But, test here passes, because these html5 behaviour is built on top (i believe so):
        self.assertContains(response, 'This field is required.', 2) 

    def test_post_with_invalid_data(self):
        response = self.client.post(self.url, {'username': 'wrong_user', 'password': 'invalidpass333'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '...please login or continue as guest')
        self.assertContains(response, 
            'Please enter a correct username and password. Note that both fields may be case-sensitive.') 

    def test_post_with_valid_data(self):
        # comment
            # Here we are setting follow=True in post method arguments. That's because if not we get error :
            # 'AssertionError: 301 != 200 : Couldn't retrieve redirection page '/news/home': response code was 301
            # (expected 200)'. From django documentation:
            #       If you set follow to True the client will follow any redirects and a redirect_chain 
            #       attribute will be set in the response object containing tuples of the intermediate urls and status
            #       codes.  
        response = self.client.post(self.url, {'username': 'testuser', 'password': 'testpass123'}, follow=True)

        self.assertRedirects(response, reverse('my_newsapp:home'))

class MyNewsappLogoutViewTests(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')
        self.url = reverse('my_newsapp:logout')

    def test_logging_out(self):
        response = self.client.get(self.url)

        self.assertRedirects(response, reverse('my_newsapp:login'))

@override_settings(MEDIA_ROOT=tempfile.gettempdir() + '/')
class DownloadFileTests(TestCase):
    
    def setUp(self):
        self.file = FileFactory(file=get_test_file('test_doc_file.doc'))
        self.url = (reverse('my_newsapp:download-file', kwargs={'id': self.file.id}))

    def tearDown(self):
        delete_article_test_files(self.file.article)
                
    def test_file_doesnt_exist(self):
        response = self.client.get(reverse('my_newsapp:download-file', kwargs={'id': 100}))

        self.assertEqual(response.status_code, 404)

    def test_file_invalid_path(self):
        self.file.file.delete()
        response = self.client.get(reverse('my_newsapp:download-file', kwargs={'id': self.file.id}))

        self.assertEqual(response.status_code, 404)

    def test_file_exists(self):
        response = self.client.get(reverse('my_newsapp:download-file', kwargs={'id': self.file.id}))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], self.file.content_type())
        self.assertIn(self.file.name(), response['Content-Disposition'])

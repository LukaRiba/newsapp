from django.test import TestCase, RequestFactory
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView
from django.db.models.query import QuerySet
from django.core.paginator import InvalidPage
from django.test import Client
from django.contrib.auth.models import User

from my_newsapp.views import NavigationContextMixin, HomeViewMixin, HomeView
from my_newsapp.factories import UserFactory, CategoryFactory, ArticleFactory, ImageFactory, FileFactory
from my_newsapp.models import Category, Article
from my_newsapp.utils import get_status_none_categories_random_ids
from my_newsapp.views import CategoryView

# from https://tech.people-doc.com/django-unit-test-your-views.html
def setup_view(view, request, *args, **kwargs):
    """Mimic as_view() returned callable, but returns view instance.
    args and kwargs are the same you would pass to ``reverse()``
    """
    view.request = request
    view.args = args
    view.kwargs = kwargs
    return view

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

    def test_get_secondary_category_method__secondary_category_exists(self):
        CategoryFactory(status='S')
        returned_category = self.test_view.get_secondary_category(self.rand_ids())
        self.assertEqual(returned_category.status, 'S')

    def test_get_secondary_category_method__secondary_category_doesnt_exist(self):
        returned_category = self.test_view.get_secondary_category(self.rand_ids())
        self.assertEqual(returned_category.status, None)
        self.assertTrue(returned_category in Category.objects.all())

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

    def test_primary_and_secondary_category_objects_exist(self):
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

    def test_home_view_loads_anonymous_user(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed('my_newsapp/home.html')
        self.assertContains(self.response, '<a class="nav-link" href="/news/login/?next=/news/home/">Login</a>')

    def test_home_view_loads_logged_in_user(self):
        self.client.login(username='testuser', password='testpass123') # login client as created user
        response = self.client.get('/news/home/') # self.response in setUp is made with unlogged client
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('my_newsapp/home.html')
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

class LatestArticlesViewTests(TestCase):

    def setUp(self):
        ArticleFactory.create_batch(size=8)
        
    def test_response_contents_are_equal(self):
        response = self.client.get('/news/latest-articles/')
        response_page_one_querystring = self.client.get('/news/latest-articles/?page=1')
        self.assertEqual(response.content, response_page_one_querystring.content)

    def test_latest_articles_view_page_1(self):
        page_1 = self.client.get('/news/latest-articles/?page=1')
        self.assertEqual(page_1.status_code, 200)
        self.assertTemplateUsed('my_newsapp/latest_articles.html')
        self.assertContains(page_1, 'Latest Articles')
        self.assertTrue('articles' in page_1.context)
        self.assertEqual(len(page_1.context['articles']), 5)

    def test_latest_articles_view_page_2(self):
        page_2 = self.client.get('/news/latest-articles/?page=2')
        self.assertEqual(page_2.status_code, 200)
        self.assertTemplateUsed('my_newsapp/latest_articles.html')
        self.assertContains(page_2, 'Latest Articles')
        self.assertTrue('articles' in page_2.context)
        self.assertEqual(len(page_2.context['articles']), 3) # as paginate_by = 5, 3 articles are left for 3rd page.
    
    def test_latest_articles_view_non_existing_page(self):
        page_3 = self.client.get('/news/latest-articles/?page=3')
        self.assertTemplateNotUsed('my_newsapp/latest_articles.html')
        self.assertEqual(page_3.status_code, 404)
        self.assertRaises(InvalidPage)

class CategoryViewTests(TestCase):

    def setUp(self):
        self.test_category = CategoryFactory(title='Test Category', slug='test-category')
        ArticleFactory.create_batch(size=8, category=self.test_category)
        self.url = reverse('my_newsapp:category', kwargs={'slug': self.test_category.slug})

    def test_response_contents_are_equal(self):
        response = self.client.get(self.url)
        response_page_one_querystring = self.client.get(self.url + '?page=1')
        self.assertEqual(response.content, response_page_one_querystring.content)

    def test_category_view_page_1(self):
        page_1 = self.client.get(self.url + '?page=1')
        self.assertEqual(page_1.status_code, 200)
        self.assertTemplateUsed('my_newsapp/category.html')
        self.assertContains(page_1, self.test_category.title)
        self.assertTrue('articles' in page_1.context)
        self.assertEqual(len(page_1.context['articles']), 5)

    def test_category_view_page_2(self):
        page_2 = self.client.get(self.url + '?page=2')
        self.assertEqual(page_2.status_code, 200)
        self.assertTemplateUsed('my_newsapp/category.html')
        self.assertContains(page_2, self.test_category.title)
        self.assertTrue('articles' in page_2.context)
        self.assertEqual(len(page_2.context['articles']), 3) # as paginate_by = 5, 3 articles are left for 3rd page.
    
    def test_category_view_non_existing_page(self):
        page_3 = self.client.get(self.url + '?page=3')
        self.assertTemplateNotUsed('my_newsapp/category.html')
        self.assertEqual(page_3.status_code, 404)
        self.assertRaises(InvalidPage)

    def test_get_category_method(self):
        # as get_category() doesn't use request object, we create one with empty path, just to pass it to setup_view().
        request = RequestFactory().get('')
        slug = self.test_category.slug
        view = setup_view(CategoryView(), request, slug=slug)
        
        self.assertEqual(view.get_category(), Category.objects.get(title=self.test_category.title))

    def test_get_queryset_method(self):
        ArticleFactory.create_batch(size=3, category=self.test_category)

        request = RequestFactory().get('')
        slug = self.test_category.slug
        view = setup_view(CategoryView(), request, slug=slug)

        self.assertEqual(list(view.get_queryset()), list(Article.objects.filter(category=view.get_category())))

class ArticleDetailViewTests(TestCase):
    
    def setUp(self):
        self.test_article = ArticleFactory(title='Test Article')
        ImageFactory.create_batch(size=2, article=self.test_article)
        FileFactory.create_batch(size=2, article=self.test_article)
        self.url = reverse('my_newsapp:article-detail', kwargs={'category': self.test_article.category.slug, 
            'id': self.test_article.id, 'slug': self.test_article.slug})
        self.response = self.client.get(self.url)

    def test_article_detail_view_loads(self):
        self.assertTrue('article' in self.response.context)
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateNotUsed('my_newsapp/detail.html')

    def test_response_content(self):
        self.assertContains(self.response, self.test_article.title)
        self.assertNotContains(self.response, self.test_article.short_description)
        # replace('\n', '<br />') because linebreaks is applied in template
        self.assertContains(self.response, self.test_article.text.replace('\n', '<br />'))
        self.assertContains(self.response, self.test_article.pub_date.strftime('%b %d, %Y'))
        self.assertContains(self.response, self.test_article.author)
        self.assertContains(self.response, self.test_article.category)

        for image in self.test_article.images.all():
            self.assertContains(self.response, image.image)

        for file in self.test_article.files.all():
            self.assertContains(self.response, file.name())
        

        # dalje: test za samo jednu sliku
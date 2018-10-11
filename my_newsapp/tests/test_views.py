from django.test import TestCase
from django.views.generic import TemplateView
from django.db.models.query import QuerySet

from django.test import Client

from my_newsapp.views import NavigationContextMixin, HomeViewMixin, HomeView
from my_newsapp.factories import CategoryFactory, ArticleFactory
from my_newsapp.models import Category, Article
from my_newsapp.utils import get_status_none_categories_random_ids


class NavigationContextMixinTests(TestCase):

    class TestView(NavigationContextMixin, TemplateView):
        pass

    def setUp(self):
        self.test_view = self.TestView()

    def test_navigation_context_mixin_no_category_objects(self):
        context = self.test_view.get_context_data()
        #comment
            # The queryset objects will not be identical if they are the result of different queries even if they 
            # have the same values in their result. If you convert the query set to a list first, you should be able 
            # to do a normal comparison (assuming they have the same sort order of course).
        self.assertEqual(list(context['categories']), list(Category.objects.all()))
        self.assertEqual(list(context['categories']), [])

    def test_navigation_context_mixin_with_category_objects(self):
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

    def test_home_mixin_context(self):
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
        self.assertEqual(other_articles.count(), 6)

class HomeViewTests(TestCase):

    def setUp(self):
        CategoryFactory.create_batch(size=3)
        CategoryFactory(status='P')
        CategoryFactory(status='S')

        for category in Category.objects.all():
            ArticleFactory.create_batch(size=4, category=category)

        self.response = self.client.get('/news/home/')

    def test_home_view_context_variables_are_in_response_context(self):
        self.assertTrue('categories' in self.response.context)
        self.assertTrue('primary_category' in self.response.context)
        self.assertTrue('secondary_category' in self.response.context)
        self.assertTrue('other_articles' in self.response.context)

    def test_home_view_loads(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed('my_newsapp/home.html')
        self.assertContains(self.response, self.response.context['primary_category'].title )

        for article in self.response.context['primary_category'].articles.all()[:3]:
            self.assertContains(self.response, article.title)
            self.assertContains(self.response, article.short_description)
            # strftime() stringifies date to format which is the same as in settings.DATE_FORMAT
            self.assertContains(self.response, article.pub_date.date().strftime('%b %d, %Y'))

        self.assertContains(self.response, self.response.context['secondary_category'].title )
        for article in self.response.context['secondary_category'].articles.all()[:2]:
            self.assertContains(self.response, article.title)
            self.assertContains(self.response, article.short_description)
            self.assertContains(self.response, article.pub_date.date().strftime('%b %d, %Y'))

        for article in self.response.context['other_articles']:
            self.assertContains(self.response, article.title)
            self.assertNotContains(self.response, article.short_description)
            self.assertContains(self.response, article.pub_date.date().strftime('%b %d, %Y'))
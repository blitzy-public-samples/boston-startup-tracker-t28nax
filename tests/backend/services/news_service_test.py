import pytest
from unittest.mock import patch, MagicMock
from src.backend.services import news_service
from src.backend.models.news_article import NewsArticle
from src.backend.utils import db

class TestNewsService:
    @patch('src.backend.utils.db.session.query')
    def test_get_news_articles(self, mock_query):
        # Mock db.session.query to return a list of mock news articles
        mock_articles = [NewsArticle(id=1, title='Test Article 1'), NewsArticle(id=2, title='Test Article 2')]
        mock_query.return_value.all.return_value = mock_articles

        # Call news_service.get_news_articles()
        result = news_service.get_news_articles()

        # Assert the correct number of news articles is returned
        assert len(result) == len(mock_articles)

        # Assert the returned objects are of type NewsArticle
        for article in result:
            assert isinstance(article, NewsArticle)

    @patch('src.backend.utils.db.session.query')
    def test_get_news_article_by_id(self, mock_query):
        # Create a mock news article with a specific ID
        mock_article = NewsArticle(id=1, title='Test Article')
        mock_query.return_value.get.return_value = mock_article

        # Call news_service.get_news_article_by_id() with the specific ID
        result = news_service.get_news_article_by_id(1)

        # Assert the returned news article matches the mock news article
        assert result == mock_article

        # Assert the returned object is an instance of NewsArticle
        assert isinstance(result, NewsArticle)

    @patch('src.backend.utils.db.session.add')
    @patch('src.backend.utils.db.session.commit')
    def test_create_news_article(self, mock_commit, mock_add):
        # Create mock news article data
        mock_data = {'title': 'New Article', 'content': 'Article content'}

        # Call news_service.create_news_article() with mock data
        result = news_service.create_news_article(mock_data)

        # Assert db.session.add was called with a NewsArticle object
        mock_add.assert_called_once()
        assert isinstance(mock_add.call_args[0][0], NewsArticle)

        # Assert db.session.commit was called
        mock_commit.assert_called_once()

        # Assert the returned object is an instance of NewsArticle
        assert isinstance(result, NewsArticle)

    @patch('src.backend.utils.db.session.query')
    @patch('src.backend.utils.db.session.commit')
    def test_update_news_article(self, mock_commit, mock_query):
        # Create a mock news article
        mock_article = NewsArticle(id=1, title='Old Title', content='Old content')
        mock_query.return_value.get.return_value = mock_article

        # Create mock update data
        mock_update_data = {'title': 'Updated Title', 'content': 'Updated content'}

        # Call news_service.update_news_article() with mock data
        result = news_service.update_news_article(1, mock_update_data)

        # Assert the news article's attributes are updated
        assert result.title == 'Updated Title'
        assert result.content == 'Updated content'

        # Assert db.session.commit was called
        mock_commit.assert_called_once()

        # Assert the returned object is an instance of NewsArticle
        assert isinstance(result, NewsArticle)

    @patch('src.backend.utils.db.session.query')
    @patch('src.backend.utils.db.session.delete')
    @patch('src.backend.utils.db.session.commit')
    def test_delete_news_article(self, mock_commit, mock_delete, mock_query):
        # Create a mock news article
        mock_article = NewsArticle(id=1, title='Test Article')
        mock_query.return_value.get.return_value = mock_article

        # Call news_service.delete_news_article() with the news article's ID
        news_service.delete_news_article(1)

        # Assert db.session.delete was called with the mock news article
        mock_delete.assert_called_once_with(mock_article)

        # Assert db.session.commit was called
        mock_commit.assert_called_once()
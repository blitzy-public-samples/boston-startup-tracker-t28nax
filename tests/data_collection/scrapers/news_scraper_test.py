import pytest
from unittest.mock import patch, MagicMock
from src.data_collection.scrapers.news_scraper import NewsScraper
from src.backend.models.news_article import NewsArticle
from src.backend.utils.db import db

class TestNewsScraper:
    @pytest.fixture
    def news_scraper(self):
        return NewsScraper()

    def test_scrape_news(self, news_scraper):
        # Mock the fetch_page method to return sample HTML
        news_scraper.fetch_page = MagicMock(return_value="<html>Sample HTML</html>")
        
        # Mock the parse_news_data method to return sample news data
        sample_news_data = [{"title": "Test News", "content": "Test Content"}]
        news_scraper.parse_news_data = MagicMock(return_value=sample_news_data)
        
        # Mock the save_news_articles method
        news_scraper.save_news_articles = MagicMock()
        
        # Call the scrape_news method
        news_scraper.scrape_news()
        
        # Assert that fetch_page, parse_news_data, and save_news_articles were called
        news_scraper.fetch_page.assert_called_once()
        news_scraper.parse_news_data.assert_called_once_with("<html>Sample HTML</html>")
        news_scraper.save_news_articles.assert_called_once_with(sample_news_data)

    @patch('requests.get')
    def test_fetch_page(self, mock_get, news_scraper):
        # Mock the requests.get method to return a sample response
        mock_response = MagicMock()
        mock_response.content = b"<html>Test Content</html>"
        mock_get.return_value = mock_response
        
        # Call the fetch_page method with a test URL
        test_url = "https://test.com"
        result = news_scraper.fetch_page(test_url)
        
        # Assert that requests.get was called with the correct URL
        mock_get.assert_called_once_with(test_url)
        
        # Assert that the returned content matches the mocked response
        assert result == "<html>Test Content</html>"

    def test_parse_news_data(self, news_scraper):
        # Create a sample HTML content with news article information
        sample_html = """
        <div class="news-article">
            <h2>Test News Title</h2>
            <p>Test News Content</p>
            <span class="date">2023-05-01</span>
        </div>
        """
        
        # Call the parse_news_data method with the sample HTML
        result = news_scraper.parse_news_data(sample_html)
        
        # Assert that the returned data contains the expected news article information
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]['title'] == "Test News Title"
        assert result[0]['content'] == "Test News Content"
        assert result[0]['date'] == "2023-05-01"

    @patch('src.backend.utils.db.session.add')
    @patch('src.backend.utils.db.session.commit')
    def test_save_news_articles(self, mock_commit, mock_add, news_scraper):
        # Create sample news article data
        sample_data = [
            {"title": "News 1", "content": "Content 1", "date": "2023-05-01"},
            {"title": "News 2", "content": "Content 2", "date": "2023-05-02"}
        ]
        
        # Call the save_news_articles method with the sample data
        news_scraper.save_news_articles(sample_data)
        
        # Assert that db.session.add was called for each news article
        assert mock_add.call_count == 2
        
        # Assert that db.session.commit was called
        mock_commit.assert_called_once()

        # Check if the correct NewsArticle objects were created
        calls = mock_add.call_args_list
        assert isinstance(calls[0][0][0], NewsArticle)
        assert calls[0][0][0].title == "News 1"
        assert isinstance(calls[1][0][0], NewsArticle)
        assert calls[1][0][0].title == "News 2"
import pytest
from unittest.mock import patch, MagicMock
from src.data_collection.scrapers.startup_scraper import StartupScraper
from src.backend.models.startup import Startup
from src.backend.utils.db import db

class TestStartupScraper:

    @patch.object(StartupScraper, 'fetch_page')
    @patch.object(StartupScraper, 'parse_startup_data')
    @patch.object(StartupScraper, 'save_startups')
    def test_scrape_startups(self, mock_save_startups, mock_parse_startup_data, mock_fetch_page):
        # Create a mock StartupScraper instance
        scraper = StartupScraper()

        # Mock the fetch_page method to return sample HTML
        sample_html = "<html><body>Sample startup data</body></html>"
        mock_fetch_page.return_value = sample_html

        # Mock the parse_startup_data method to return sample startup data
        sample_startup_data = [{"name": "Startup 1", "description": "Description 1"}]
        mock_parse_startup_data.return_value = sample_startup_data

        # Call the scrape_startups method
        scraper.scrape_startups()

        # Assert that fetch_page, parse_startup_data, and save_startups were called
        mock_fetch_page.assert_called_once()
        mock_parse_startup_data.assert_called_once_with(sample_html)
        mock_save_startups.assert_called_once_with(sample_startup_data)

    @patch('requests.get')
    def test_fetch_page(self, mock_requests_get):
        # Mock the requests.get method to return a sample response
        mock_response = MagicMock()
        mock_response.content = b"<html><body>Test content</body></html>"
        mock_requests_get.return_value = mock_response

        # Create a StartupScraper instance
        scraper = StartupScraper()

        # Call the fetch_page method with a test URL
        test_url = "https://example.com/startups"
        result = scraper.fetch_page(test_url)

        # Assert that requests.get was called with the correct URL
        mock_requests_get.assert_called_once_with(test_url)

        # Assert that the returned content matches the mocked response
        assert result == mock_response.content.decode()

    def test_parse_startup_data(self):
        # Create a sample HTML content with startup information
        sample_html = """
        <html>
            <body>
                <div class="startup">
                    <h2>Startup 1</h2>
                    <p>Description 1</p>
                </div>
                <div class="startup">
                    <h2>Startup 2</h2>
                    <p>Description 2</p>
                </div>
            </body>
        </html>
        """

        # Create a StartupScraper instance
        scraper = StartupScraper()

        # Call the parse_startup_data method with the sample HTML
        result = scraper.parse_startup_data(sample_html)

        # Assert that the returned data contains the expected startup information
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0] == {"name": "Startup 1", "description": "Description 1"}
        assert result[1] == {"name": "Startup 2", "description": "Description 2"}

    @patch.object(db.session, 'add')
    @patch.object(db.session, 'commit')
    def test_save_startups(self, mock_commit, mock_add):
        # Create sample startup data
        sample_data = [
            {"name": "Startup 1", "description": "Description 1"},
            {"name": "Startup 2", "description": "Description 2"}
        ]

        # Create a StartupScraper instance
        scraper = StartupScraper()

        # Call the save_startups method with the sample data
        scraper.save_startups(sample_data)

        # Assert that db.session.add was called for each startup
        assert mock_add.call_count == 2

        # Assert that db.session.commit was called
        mock_commit.assert_called_once()

        # Check if the correct Startup objects were created and added
        calls = mock_add.call_args_list
        assert isinstance(calls[0][0][0], Startup)
        assert calls[0][0][0].name == "Startup 1"
        assert calls[0][0][0].description == "Description 1"
        assert isinstance(calls[1][0][0], Startup)
        assert calls[1][0][0].name == "Startup 2"
        assert calls[1][0][0].description == "Description 2"
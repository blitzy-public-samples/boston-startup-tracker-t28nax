import pytest
from unittest.mock import patch, MagicMock
from src.data_collection.scrapers.investor_scraper import InvestorScraper
from src.backend.models.investor import Investor
from src.backend.utils.db import db

class TestInvestorScraper:

    @patch.object(InvestorScraper, 'fetch_page')
    @patch.object(InvestorScraper, 'parse_investor_data')
    @patch.object(InvestorScraper, 'save_investors')
    def test_scrape_investors(self, mock_save, mock_parse, mock_fetch):
        # Create a mock InvestorScraper instance
        scraper = InvestorScraper()

        # Mock the fetch_page method to return sample HTML
        mock_fetch.return_value = "<html>Sample investor data</html>"

        # Mock the parse_investor_data method to return sample investor data
        sample_data = [{"name": "Investor 1"}, {"name": "Investor 2"}]
        mock_parse.return_value = sample_data

        # Call the scrape_investors method
        scraper.scrape_investors()

        # Assert that fetch_page, parse_investor_data, and save_investors were called
        mock_fetch.assert_called_once()
        mock_parse.assert_called_once_with("<html>Sample investor data</html>")
        mock_save.assert_called_once_with(sample_data)

    @patch('requests.get')
    def test_fetch_page(self, mock_get):
        # Mock the requests.get method to return a sample response
        mock_response = MagicMock()
        mock_response.content = b"<html>Test content</html>"
        mock_get.return_value = mock_response

        # Create an InvestorScraper instance
        scraper = InvestorScraper()

        # Call the fetch_page method with a test URL
        test_url = "https://example.com/investors"
        content = scraper.fetch_page(test_url)

        # Assert that requests.get was called with the correct URL
        mock_get.assert_called_once_with(test_url)

        # Assert that the returned content matches the mocked response
        assert content == "<html>Test content</html>"

    def test_parse_investor_data(self):
        # Create a sample HTML content with investor information
        sample_html = """
        <div class="investor">
            <h2>Investor 1</h2>
            <p>Type: VC</p>
            <p>Location: Boston, MA</p>
        </div>
        <div class="investor">
            <h2>Investor 2</h2>
            <p>Type: Angel</p>
            <p>Location: Cambridge, MA</p>
        </div>
        """

        # Create an InvestorScraper instance
        scraper = InvestorScraper()

        # Call the parse_investor_data method with the sample HTML
        parsed_data = scraper.parse_investor_data(sample_html)

        # Assert that the returned data contains the expected investor information
        assert len(parsed_data) == 2
        assert parsed_data[0] == {"name": "Investor 1", "type": "VC", "location": "Boston, MA"}
        assert parsed_data[1] == {"name": "Investor 2", "type": "Angel", "location": "Cambridge, MA"}

    @patch.object(db.session, 'add')
    @patch.object(db.session, 'commit')
    def test_save_investors(self, mock_commit, mock_add):
        # Create sample investor data
        sample_data = [
            {"name": "Investor 1", "type": "VC", "location": "Boston, MA"},
            {"name": "Investor 2", "type": "Angel", "location": "Cambridge, MA"}
        ]

        # Create an InvestorScraper instance
        scraper = InvestorScraper()

        # Call the save_investors method with the sample data
        scraper.save_investors(sample_data)

        # Assert that db.session.add was called for each investor
        assert mock_add.call_count == 2

        # Assert that db.session.commit was called
        mock_commit.assert_called_once()

        # Check that the correct Investor objects were created
        calls = mock_add.call_args_list
        assert isinstance(calls[0][0][0], Investor)
        assert calls[0][0][0].name == "Investor 1"
        assert calls[0][0][0].type == "VC"
        assert calls[0][0][0].location == "Boston, MA"

        assert isinstance(calls[1][0][0], Investor)
        assert calls[1][0][0].name == "Investor 2"
        assert calls[1][0][0].type == "Angel"
        assert calls[1][0][0].location == "Cambridge, MA"
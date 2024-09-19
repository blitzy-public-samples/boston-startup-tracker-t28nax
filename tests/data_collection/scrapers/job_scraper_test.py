import pytest
from unittest.mock import patch, MagicMock
from src.data_collection.scrapers.job_scraper import JobScraper
from src.backend.models.job_posting import JobPosting
from src.backend.utils.db import db

class TestJobScraper:
    @patch('src.data_collection.scrapers.job_scraper.JobScraper.fetch_page')
    @patch('src.data_collection.scrapers.job_scraper.JobScraper.parse_job_data')
    @patch('src.data_collection.scrapers.job_scraper.JobScraper.save_job_postings')
    def test_scrape_jobs(self, mock_save, mock_parse, mock_fetch):
        # Create a mock JobScraper instance
        scraper = JobScraper()

        # Mock the fetch_page method to return sample HTML
        mock_fetch.return_value = "<html>Sample job data</html>"

        # Mock the parse_job_data method to return sample job data
        sample_job_data = [{"title": "Software Engineer", "company": "TechCo"}]
        mock_parse.return_value = sample_job_data

        # Call the scrape_jobs method
        scraper.scrape_jobs()

        # Assert that fetch_page, parse_job_data, and save_job_postings were called
        mock_fetch.assert_called_once()
        mock_parse.assert_called_once_with("<html>Sample job data</html>")
        mock_save.assert_called_once_with(sample_job_data)

    @patch('requests.get')
    def test_fetch_page(self, mock_get):
        # Mock the requests.get method to return a sample response
        mock_response = MagicMock()
        mock_response.content = b"<html>Test content</html>"
        mock_get.return_value = mock_response

        # Create a JobScraper instance
        scraper = JobScraper()

        # Call the fetch_page method with a test URL
        test_url = "https://example.com/jobs"
        result = scraper.fetch_page(test_url)

        # Assert that requests.get was called with the correct URL
        mock_get.assert_called_once_with(test_url)

        # Assert that the returned content matches the mocked response
        assert result == "<html>Test content</html>"

    def test_parse_job_data(self):
        # Create a sample HTML content with job posting information
        sample_html = """
        <div class="job-posting">
            <h2>Software Engineer</h2>
            <p>Company: TechCo</p>
            <p>Location: Boston, MA</p>
        </div>
        <div class="job-posting">
            <h2>Data Scientist</h2>
            <p>Company: DataCorp</p>
            <p>Location: Cambridge, MA</p>
        </div>
        """

        # Create a JobScraper instance
        scraper = JobScraper()

        # Call the parse_job_data method with the sample HTML
        result = scraper.parse_job_data(sample_html)

        # Assert that the returned data contains the expected job posting information
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0] == {
            "title": "Software Engineer",
            "company": "TechCo",
            "location": "Boston, MA"
        }
        assert result[1] == {
            "title": "Data Scientist",
            "company": "DataCorp",
            "location": "Cambridge, MA"
        }

    @patch('src.backend.utils.db.db.session.add')
    @patch('src.backend.utils.db.db.session.commit')
    def test_save_job_postings(self, mock_commit, mock_add):
        # Create sample job posting data
        sample_data = [
            {"title": "Software Engineer", "company": "TechCo", "location": "Boston, MA"},
            {"title": "Data Scientist", "company": "DataCorp", "location": "Cambridge, MA"}
        ]

        # Create a JobScraper instance
        scraper = JobScraper()

        # Call the save_job_postings method with the sample data
        scraper.save_job_postings(sample_data)

        # Assert that db.session.add was called for each job posting
        assert mock_add.call_count == 2

        # Assert that db.session.commit was called
        mock_commit.assert_called_once()

        # Check if JobPosting objects were created with correct data
        calls = mock_add.call_args_list
        assert isinstance(calls[0][0][0], JobPosting)
        assert calls[0][0][0].title == "Software Engineer"
        assert calls[0][0][0].company == "TechCo"
        assert calls[0][0][0].location == "Boston, MA"

        assert isinstance(calls[1][0][0], JobPosting)
        assert calls[1][0][0].title == "Data Scientist"
        assert calls[1][0][0].company == "DataCorp"
        assert calls[1][0][0].location == "Cambridge, MA"
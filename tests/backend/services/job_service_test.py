import pytest
from unittest.mock import patch, MagicMock
from src.backend.services import job_service
from src.backend.models.job_posting import JobPosting
from src.backend.utils import db

class TestJobService:
    @pytest.fixture
    def mock_db_session(self):
        with patch('src.backend.utils.db.session') as mock_session:
            yield mock_session

    def test_get_job_postings(self, mock_db_session):
        # Mock db.session.query to return a list of mock job postings
        mock_job_postings = [JobPosting(id=1), JobPosting(id=2), JobPosting(id=3)]
        mock_db_session.query.return_value.all.return_value = mock_job_postings

        # Call job_service.get_job_postings()
        result = job_service.get_job_postings()

        # Assert the correct number of job postings is returned
        assert len(result) == len(mock_job_postings)

        # Assert the returned objects are of type JobPosting
        assert all(isinstance(job, JobPosting) for job in result)

    def test_get_job_posting_by_id(self, mock_db_session):
        # Create a mock job posting with a specific ID
        mock_job_posting = JobPosting(id=1, title="Software Engineer")
        mock_db_session.query.return_value.get.return_value = mock_job_posting

        # Call job_service.get_job_posting_by_id() with the specific ID
        result = job_service.get_job_posting_by_id(1)

        # Assert the returned job posting matches the mock job posting
        assert result == mock_job_posting

        # Assert the returned object is an instance of JobPosting
        assert isinstance(result, JobPosting)

    def test_create_job_posting(self, mock_db_session):
        # Create mock job posting data
        mock_data = {
            "title": "Software Engineer",
            "company": "TechCorp",
            "description": "Exciting opportunity for a skilled developer"
        }

        # Call job_service.create_job_posting() with mock data
        result = job_service.create_job_posting(mock_data)

        # Assert db.session.add was called with a JobPosting object
        mock_db_session.add.assert_called_once()
        assert isinstance(mock_db_session.add.call_args[0][0], JobPosting)

        # Assert db.session.commit was called
        mock_db_session.commit.assert_called_once()

        # Assert the returned object is an instance of JobPosting
        assert isinstance(result, JobPosting)

    def test_update_job_posting(self, mock_db_session):
        # Create a mock job posting
        mock_job_posting = JobPosting(id=1, title="Software Engineer", company="TechCorp")
        mock_db_session.query.return_value.get.return_value = mock_job_posting

        # Create mock update data
        mock_update_data = {
            "title": "Senior Software Engineer",
            "description": "Leadership role for an experienced developer"
        }

        # Call job_service.update_job_posting() with mock data
        result = job_service.update_job_posting(1, mock_update_data)

        # Assert the job posting's attributes are updated
        assert result.title == mock_update_data["title"]
        assert result.description == mock_update_data["description"]
        assert result.company == "TechCorp"  # Unchanged attribute

        # Assert db.session.commit was called
        mock_db_session.commit.assert_called_once()

        # Assert the returned object is an instance of JobPosting
        assert isinstance(result, JobPosting)

    def test_delete_job_posting(self, mock_db_session):
        # Create a mock job posting
        mock_job_posting = JobPosting(id=1, title="Software Engineer")
        mock_db_session.query.return_value.get.return_value = mock_job_posting

        # Call job_service.delete_job_posting() with the job posting's ID
        job_service.delete_job_posting(1)

        # Assert db.session.delete was called with the mock job posting
        mock_db_session.delete.assert_called_once_with(mock_job_posting)

        # Assert db.session.commit was called
        mock_db_session.commit.assert_called_once()
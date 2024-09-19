import pytest
from unittest.mock import patch, MagicMock
from src.data_collection.api_integrators.linkedin_integrator import LinkedinIntegrator
from src.backend.models.startup import Startup
from src.backend.models.founder import Founder
from src.backend.models.executive import Executive
from src.backend.models.job_posting import JobPosting
from src.backend.utils.db import db

class TestLinkedinIntegrator:

    @pytest.fixture
    def linkedin_integrator(self):
        return LinkedinIntegrator()

    @patch('requests.get')
    def test_fetch_company_data(self, mock_get, linkedin_integrator):
        # Mock the API response with sample company data
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'name': 'Test Company',
            'description': 'A test company',
            'industry': 'Technology',
            'employeeCount': 100
        }
        mock_get.return_value = mock_response

        # Call the fetch_company_data method with a company name
        result = linkedin_integrator.fetch_company_data('Test Company')

        # Assert that the API was called with correct parameters
        mock_get.assert_called_once_with('https://api.linkedin.com/v2/companies', params={'q': 'Test Company'})

        # Assert that the returned data matches the mocked response
        assert result == mock_response.json.return_value
        assert 'name' in result
        assert 'description' in result
        assert 'industry' in result
        assert 'employeeCount' in result

    @patch('requests.get')
    def test_fetch_employee_data(self, mock_get, linkedin_integrator):
        # Mock the API response with sample employee data
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'employees': [
                {'name': 'John Doe', 'title': 'CEO'},
                {'name': 'Jane Smith', 'title': 'CTO'}
            ]
        }
        mock_get.return_value = mock_response

        # Call the fetch_employee_data method with a company ID
        result = linkedin_integrator.fetch_employee_data('123456')

        # Assert that the API was called with correct parameters
        mock_get.assert_called_once_with('https://api.linkedin.com/v2/employees', params={'company_id': '123456'})

        # Assert that the returned data matches the mocked response
        assert result == mock_response.json.return_value
        assert 'employees' in result
        assert len(result['employees']) == 2
        assert 'name' in result['employees'][0]
        assert 'title' in result['employees'][0]

    @patch('requests.get')
    def test_fetch_job_postings(self, mock_get, linkedin_integrator):
        # Mock the API response with sample job postings data
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'jobs': [
                {'title': 'Software Engineer', 'description': 'Join our team!'},
                {'title': 'Product Manager', 'description': 'Lead our product vision!'}
            ]
        }
        mock_get.return_value = mock_response

        # Call the fetch_job_postings method with a company ID
        result = linkedin_integrator.fetch_job_postings('123456')

        # Assert that the API was called with correct parameters
        mock_get.assert_called_once_with('https://api.linkedin.com/v2/jobs', params={'company_id': '123456'})

        # Assert that the returned data matches the mocked response
        assert result == mock_response.json.return_value
        assert 'jobs' in result
        assert len(result['jobs']) == 2
        assert 'title' in result['jobs'][0]
        assert 'description' in result['jobs'][0]

    @patch('src.data_collection.api_integrators.linkedin_integrator.LinkedinIntegrator.fetch_company_data')
    def test_update_startup_data(self, mock_fetch_company_data, linkedin_integrator):
        # Create a mock startup in the database
        startup = Startup(name='Old Company Name', description='Old description')
        db.session.add(startup)

        # Mock the fetch_company_data method to return updated data
        mock_fetch_company_data.return_value = {
            'name': 'New Company Name',
            'description': 'New description',
            'industry': 'Technology',
            'employeeCount': 200
        }

        # Call the update_startup_data method
        linkedin_integrator.update_startup_data(startup)

        # Assert that the startup in the database was updated
        assert startup.name == 'New Company Name'
        assert startup.description == 'New description'
        assert startup.industry == 'Technology'
        assert startup.employee_count == 200

        # Assert that db.session.commit was called
        db.session.commit.assert_called_once()

    @patch('src.data_collection.api_integrators.linkedin_integrator.LinkedinIntegrator.fetch_employee_data')
    def test_update_employee_data(self, mock_fetch_employee_data, linkedin_integrator):
        # Create mock founder and executive objects in the database
        founder = Founder(name='Old Founder Name', title='Old Title')
        executive = Executive(name='Old Executive Name', title='Old Title')
        db.session.add(founder)
        db.session.add(executive)

        # Mock the fetch_employee_data method to return updated data
        mock_fetch_employee_data.return_value = {
            'employees': [
                {'name': 'New Founder Name', 'title': 'New Founder Title'},
                {'name': 'New Executive Name', 'title': 'New Executive Title'}
            ]
        }

        # Call the update_employee_data method
        linkedin_integrator.update_employee_data('123456')

        # Assert that the founder and executive objects in the database were updated
        assert founder.name == 'New Founder Name'
        assert founder.title == 'New Founder Title'
        assert executive.name == 'New Executive Name'
        assert executive.title == 'New Executive Title'

        # Assert that db.session.commit was called
        db.session.commit.assert_called_once()

    @patch('src.data_collection.api_integrators.linkedin_integrator.LinkedinIntegrator.fetch_job_postings')
    def test_update_job_postings(self, mock_fetch_job_postings, linkedin_integrator):
        # Create mock job posting objects in the database
        existing_job = JobPosting(title='Old Job', description='Old description')
        db.session.add(existing_job)

        # Mock the fetch_job_postings method to return updated data
        mock_fetch_job_postings.return_value = {
            'jobs': [
                {'title': 'Updated Job', 'description': 'Updated description'},
                {'title': 'New Job', 'description': 'New job description'}
            ]
        }

        # Call the update_job_postings method
        linkedin_integrator.update_job_postings('123456')

        # Assert that job posting objects in the database were updated
        assert existing_job.title == 'Updated Job'
        assert existing_job.description == 'Updated description'

        # Assert that new job postings were added
        new_job = JobPosting.query.filter_by(title='New Job').first()
        assert new_job is not None
        assert new_job.description == 'New job description'

        # Assert that outdated job postings were removed
        outdated_job = JobPosting.query.filter_by(title='Old Job').first()
        assert outdated_job is None

        # Assert that db.session.commit was called
        db.session.commit.assert_called_once()
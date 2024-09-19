import pytest
from flask import Flask
from unittest.mock import patch, MagicMock
from app import create_app
from db import db
from models.job_posting import JobPosting

@pytest.fixture
def client():
    # Create a Flask test client
    app = create_app('testing')
    
    # Set up application context
    with app.app_context():
        # Yield the test client
        yield app.test_client()
    
    # Tear down application context after tests

class TestJobPostingRoutes:
    def test_get_job_postings(self, client):
        # Mock db.session.query to return a list of mock job postings
        mock_job_postings = [
            JobPosting(id=1, title="Software Engineer", company="TechCo", description="Job description"),
            JobPosting(id=2, title="Data Scientist", company="DataCorp", description="Another job description")
        ]
        with patch('db.session.query') as mock_query:
            mock_query.return_value.all.return_value = mock_job_postings

            # Send GET request to /jobs
            response = client.get('/jobs')

            # Assert response status code is 200
            assert response.status_code == 200

            # Assert response JSON contains expected job posting data
            data = response.get_json()
            assert len(data) == 2
            assert data[0]['id'] == 1
            assert data[0]['title'] == "Software Engineer"
            assert data[1]['id'] == 2
            assert data[1]['title'] == "Data Scientist"

    def test_get_job_posting(self, client):
        # Mock db.session.query.get to return a mock job posting
        mock_job_posting = JobPosting(id=1, title="Software Engineer", company="TechCo", description="Job description")
        with patch('db.session.query') as mock_query:
            mock_query.return_value.get.return_value = mock_job_posting

            # Send GET request to /jobs/1
            response = client.get('/jobs/1')

            # Assert response status code is 200
            assert response.status_code == 200

            # Assert response JSON contains expected job posting data
            data = response.get_json()
            assert data['id'] == 1
            assert data['title'] == "Software Engineer"
            assert data['company'] == "TechCo"
            assert data['description'] == "Job description"

    def test_create_job_posting(self, client):
        # Mock db.session.add and db.session.commit
        with patch('db.session.add') as mock_add, patch('db.session.commit') as mock_commit:
            # Send POST request to /jobs with job posting data
            response = client.post('/jobs', json={
                'title': "New Job",
                'company': "NewCo",
                'description': "New job description"
            })

            # Assert response status code is 201
            assert response.status_code == 201

            # Assert response JSON contains created job posting data
            data = response.get_json()
            assert data['title'] == "New Job"
            assert data['company'] == "NewCo"
            assert data['description'] == "New job description"

            # Assert db.session.add and db.session.commit were called
            mock_add.assert_called_once()
            mock_commit.assert_called_once()

    def test_update_job_posting(self, client):
        # Mock db.session.query.get to return a mock job posting
        mock_job_posting = MagicMock(spec=JobPosting)
        mock_job_posting.id = 1
        with patch('db.session.query') as mock_query, patch('db.session.commit') as mock_commit:
            mock_query.return_value.get.return_value = mock_job_posting

            # Send PUT request to /jobs/1 with updated data
            response = client.put('/jobs/1', json={
                'title': "Updated Job",
                'company': "UpdatedCo",
                'description': "Updated job description"
            })

            # Assert response status code is 200
            assert response.status_code == 200

            # Assert response JSON contains updated job posting data
            data = response.get_json()
            assert data['title'] == "Updated Job"
            assert data['company'] == "UpdatedCo"
            assert data['description'] == "Updated job description"

            # Assert mock job posting object was updated with new data
            assert mock_job_posting.title == "Updated Job"
            assert mock_job_posting.company == "UpdatedCo"
            assert mock_job_posting.description == "Updated job description"

            # Assert db.session.commit was called
            mock_commit.assert_called_once()

    def test_delete_job_posting(self, client):
        # Mock db.session.query.get to return a mock job posting
        mock_job_posting = MagicMock(spec=JobPosting)
        mock_job_posting.id = 1
        with patch('db.session.query') as mock_query, patch('db.session.delete') as mock_delete, patch('db.session.commit') as mock_commit:
            mock_query.return_value.get.return_value = mock_job_posting

            # Send DELETE request to /jobs/1
            response = client.delete('/jobs/1')

            # Assert response status code is 204
            assert response.status_code == 204

            # Assert db.session.delete was called with the mock job posting
            mock_delete.assert_called_once_with(mock_job_posting)

            # Assert db.session.commit was called
            mock_commit.assert_called_once()
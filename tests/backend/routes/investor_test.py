import pytest
from flask import Flask
from unittest.mock import patch, MagicMock
from app import app
from db import db
from models.investor import Investor

@pytest.fixture
def client():
    # Create a Flask test client
    with app.test_client() as client:
        # Set up application context
        with app.app_context():
            yield client
        # Tear down application context after tests

def test_get_investors(client):
    # Mock db.session.query to return a list of mock investors
    mock_investors = [
        Investor(id=1, name="John Doe", company="ABC Ventures"),
        Investor(id=2, name="Jane Smith", company="XYZ Capital")
    ]
    with patch('db.session.query') as mock_query:
        mock_query.return_value.all.return_value = mock_investors

        # Send GET request to /investors
        response = client.get('/investors')

        # Assert response status code is 200
        assert response.status_code == 200

        # Assert response JSON contains expected investor data
        data = response.get_json()
        assert len(data) == 2
        assert data[0]['id'] == 1
        assert data[0]['name'] == "John Doe"
        assert data[0]['company'] == "ABC Ventures"
        assert data[1]['id'] == 2
        assert data[1]['name'] == "Jane Smith"
        assert data[1]['company'] == "XYZ Capital"

def test_get_investor(client):
    # Mock db.session.query.get to return a mock investor
    mock_investor = Investor(id=1, name="John Doe", company="ABC Ventures")
    with patch('db.session.query') as mock_query:
        mock_query.return_value.get.return_value = mock_investor

        # Send GET request to /investors/1
        response = client.get('/investors/1')

        # Assert response status code is 200
        assert response.status_code == 200

        # Assert response JSON contains expected investor data
        data = response.get_json()
        assert data['id'] == 1
        assert data['name'] == "John Doe"
        assert data['company'] == "ABC Ventures"

def test_create_investor(client):
    # Mock db.session.add and db.session.commit
    with patch('db.session.add') as mock_add, patch('db.session.commit') as mock_commit:
        # Send POST request to /investors with investor data
        response = client.post('/investors', json={
            'name': "New Investor",
            'company': "New Company"
        })

        # Assert response status code is 201
        assert response.status_code == 201

        # Assert response JSON contains created investor data
        data = response.get_json()
        assert data['name'] == "New Investor"
        assert data['company'] == "New Company"

        # Assert db.session.add and db.session.commit were called
        mock_add.assert_called_once()
        mock_commit.assert_called_once()

def test_update_investor(client):
    # Mock db.session.query.get to return a mock investor
    mock_investor = Investor(id=1, name="John Doe", company="ABC Ventures")
    with patch('db.session.query') as mock_query, patch('db.session.commit') as mock_commit:
        mock_query.return_value.get.return_value = mock_investor

        # Send PUT request to /investors/1 with updated data
        response = client.put('/investors/1', json={
            'name': "John Doe Updated",
            'company': "ABC Ventures Updated"
        })

        # Assert response status code is 200
        assert response.status_code == 200

        # Assert response JSON contains updated investor data
        data = response.get_json()
        assert data['id'] == 1
        assert data['name'] == "John Doe Updated"
        assert data['company'] == "ABC Ventures Updated"

        # Assert mock investor object was updated with new data
        assert mock_investor.name == "John Doe Updated"
        assert mock_investor.company == "ABC Ventures Updated"

        # Assert db.session.commit was called
        mock_commit.assert_called_once()

def test_delete_investor(client):
    # Mock db.session.query.get to return a mock investor
    mock_investor = Investor(id=1, name="John Doe", company="ABC Ventures")
    with patch('db.session.query') as mock_query, \
         patch('db.session.delete') as mock_delete, \
         patch('db.session.commit') as mock_commit:
        mock_query.return_value.get.return_value = mock_investor

        # Send DELETE request to /investors/1
        response = client.delete('/investors/1')

        # Assert response status code is 204
        assert response.status_code == 204

        # Assert db.session.delete was called with the mock investor
        mock_delete.assert_called_once_with(mock_investor)

        # Assert db.session.commit was called
        mock_commit.assert_called_once()
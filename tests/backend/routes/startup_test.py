import pytest
from flask import Flask
from unittest.mock import patch, MagicMock
from app import app
from db import db
from Startup import Startup

@pytest.fixture
def client():
    # Create a Flask test client
    with app.test_client() as client:
        # Set up application context
        with app.app_context():
            yield client
        # Tear down application context after tests

def test_get_startups(client):
    # Mock db.session.query to return a list of mock startups
    mock_startups = [
        Startup(id=1, name="Startup 1", description="Description 1"),
        Startup(id=2, name="Startup 2", description="Description 2")
    ]
    with patch('db.session.query') as mock_query:
        mock_query.return_value.all.return_value = mock_startups

        # Send GET request to /startups
        response = client.get('/startups')

        # Assert response status code is 200
        assert response.status_code == 200

        # Assert response JSON contains expected startup data
        data = response.get_json()
        assert len(data) == 2
        assert data[0]['id'] == 1
        assert data[0]['name'] == "Startup 1"
        assert data[1]['id'] == 2
        assert data[1]['name'] == "Startup 2"

def test_get_startup(client):
    # Mock db.session.query.get to return a mock startup
    mock_startup = Startup(id=1, name="Test Startup", description="Test Description")
    with patch('db.session.query') as mock_query:
        mock_query.return_value.get.return_value = mock_startup

        # Send GET request to /startups/1
        response = client.get('/startups/1')

        # Assert response status code is 200
        assert response.status_code == 200

        # Assert response JSON contains expected startup data
        data = response.get_json()
        assert data['id'] == 1
        assert data['name'] == "Test Startup"
        assert data['description'] == "Test Description"

def test_create_startup(client):
    # Mock db.session.add and db.session.commit
    with patch('db.session.add') as mock_add, patch('db.session.commit') as mock_commit:
        # Send POST request to /startups with startup data
        response = client.post('/startups', json={
            'name': 'New Startup',
            'description': 'New Description'
        })

        # Assert response status code is 201
        assert response.status_code == 201

        # Assert response JSON contains created startup data
        data = response.get_json()
        assert data['name'] == 'New Startup'
        assert data['description'] == 'New Description'

        # Assert db.session.add and db.session.commit were called
        mock_add.assert_called_once()
        mock_commit.assert_called_once()

def test_update_startup(client):
    # Mock db.session.query.get to return a mock startup
    mock_startup = Startup(id=1, name="Old Name", description="Old Description")
    with patch('db.session.query') as mock_query, patch('db.session.commit') as mock_commit:
        mock_query.return_value.get.return_value = mock_startup

        # Send PUT request to /startups/1 with updated data
        response = client.put('/startups/1', json={
            'name': 'Updated Name',
            'description': 'Updated Description'
        })

        # Assert response status code is 200
        assert response.status_code == 200

        # Assert response JSON contains updated startup data
        data = response.get_json()
        assert data['id'] == 1
        assert data['name'] == 'Updated Name'
        assert data['description'] == 'Updated Description'

        # Assert mock startup object was updated with new data
        assert mock_startup.name == 'Updated Name'
        assert mock_startup.description == 'Updated Description'

        # Assert db.session.commit was called
        mock_commit.assert_called_once()

def test_delete_startup(client):
    # Mock db.session.query.get to return a mock startup
    mock_startup = Startup(id=1, name="To Delete", description="Will be deleted")
    with patch('db.session.query') as mock_query, \
         patch('db.session.delete') as mock_delete, \
         patch('db.session.commit') as mock_commit:
        mock_query.return_value.get.return_value = mock_startup

        # Send DELETE request to /startups/1
        response = client.delete('/startups/1')

        # Assert response status code is 204
        assert response.status_code == 204

        # Assert db.session.delete was called with the mock startup
        mock_delete.assert_called_once_with(mock_startup)

        # Assert db.session.commit was called
        mock_commit.assert_called_once()
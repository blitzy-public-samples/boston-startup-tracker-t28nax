import pytest
from flask import Flask
from unittest.mock import patch, MagicMock
from app import app
from db import db
from models.user import User
from utils.auth import bcrypt

@pytest.fixture
def client():
    # Create a Flask test client
    with app.test_client() as client:
        # Set up application context
        with app.app_context():
            yield client
        # Tear down application context after tests

def test_get_users(client):
    # Mock db.session.query to return a list of mock users
    mock_users = [
        User(id=1, username='user1', email='user1@example.com'),
        User(id=2, username='user2', email='user2@example.com')
    ]
    with patch('db.session.query') as mock_query:
        mock_query.return_value.all.return_value = mock_users

        # Send GET request to /users
        response = client.get('/users')

        # Assert response status code is 200
        assert response.status_code == 200

        # Assert response JSON contains expected user data
        data = response.get_json()
        assert len(data) == 2
        assert data[0]['id'] == 1
        assert data[0]['username'] == 'user1'
        assert data[0]['email'] == 'user1@example.com'
        assert data[1]['id'] == 2
        assert data[1]['username'] == 'user2'
        assert data[1]['email'] == 'user2@example.com'

def test_get_user(client):
    # Mock db.session.query.get to return a mock user
    mock_user = User(id=1, username='user1', email='user1@example.com')
    with patch('db.session.query') as mock_query:
        mock_query.return_value.get.return_value = mock_user

        # Send GET request to /users/1
        response = client.get('/users/1')

        # Assert response status code is 200
        assert response.status_code == 200

        # Assert response JSON contains expected user data
        data = response.get_json()
        assert data['id'] == 1
        assert data['username'] == 'user1'
        assert data['email'] == 'user1@example.com'

def test_create_user(client):
    # Mock db.session.add and db.session.commit
    with patch('db.session.add') as mock_add, \
         patch('db.session.commit') as mock_commit, \
         patch('bcrypt.generate_password_hash') as mock_hash:

        mock_hash.return_value = b'hashed_password'

        # Send POST request to /users with user data
        response = client.post('/users', json={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123'
        })

        # Assert response status code is 201
        assert response.status_code == 201

        # Assert response JSON contains created user data
        data = response.get_json()
        assert data['username'] == 'newuser'
        assert data['email'] == 'newuser@example.com'

        # Assert db.session.add and db.session.commit were called
        mock_add.assert_called_once()
        mock_commit.assert_called_once()

        # Assert bcrypt.generate_password_hash was called
        mock_hash.assert_called_once_with('password123')

def test_update_user(client):
    # Mock db.session.query.get to return a mock user
    mock_user = User(id=1, username='user1', email='user1@example.com')
    with patch('db.session.query') as mock_query, \
         patch('db.session.commit') as mock_commit:
        mock_query.return_value.get.return_value = mock_user

        # Send PUT request to /users/1 with updated data
        response = client.put('/users/1', json={
            'username': 'updateduser',
            'email': 'updated@example.com'
        })

        # Assert response status code is 200
        assert response.status_code == 200

        # Assert response JSON contains updated user data
        data = response.get_json()
        assert data['username'] == 'updateduser'
        assert data['email'] == 'updated@example.com'

        # Assert mock user object was updated with new data
        assert mock_user.username == 'updateduser'
        assert mock_user.email == 'updated@example.com'

        # Assert db.session.commit was called
        mock_commit.assert_called_once()

def test_delete_user(client):
    # Mock db.session.query.get to return a mock user
    mock_user = User(id=1, username='user1', email='user1@example.com')
    with patch('db.session.query') as mock_query, \
         patch('db.session.delete') as mock_delete, \
         patch('db.session.commit') as mock_commit:
        mock_query.return_value.get.return_value = mock_user

        # Send DELETE request to /users/1
        response = client.delete('/users/1')

        # Assert response status code is 204
        assert response.status_code == 204

        # Assert db.session.delete was called with the mock user
        mock_delete.assert_called_once_with(mock_user)

        # Assert db.session.commit was called
        mock_commit.assert_called_once()
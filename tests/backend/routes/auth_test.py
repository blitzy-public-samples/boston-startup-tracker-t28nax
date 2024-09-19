import pytest
from flask import Flask
from unittest.mock import patch, MagicMock
from app import app
from db import db
from models.user import User
from utils.auth import bcrypt, jwt

@pytest.fixture
def client():
    # Create a Flask test client
    app.config['TESTING'] = True
    with app.test_client() as client:
        # Set up application context
        with app.app_context():
            yield client
        # Tear down application context after tests

def test_login_success(client):
    # Mock db.session.query to return a mock user
    mock_user = MagicMock(spec=User)
    mock_user.id = 1
    mock_user.email = 'test@example.com'
    mock_user.password = 'hashed_password'

    with patch('db.session.query') as mock_query:
        mock_query.return_value.filter_by.return_value.first.return_value = mock_user
        
        # Mock bcrypt.check_password_hash to return True
        with patch('utils.auth.bcrypt.check_password_hash', return_value=True):
            # Mock jwt.encode to return a mock token
            with patch('utils.auth.jwt.encode', return_value='mock_token'):
                # Send POST request to /auth/login with valid credentials
                response = client.post('/auth/login', json={
                    'email': 'test@example.com',
                    'password': 'password123'
                })

                # Assert response status code is 200
                assert response.status_code == 200
                # Assert response JSON contains access token
                assert 'access_token' in response.json
                # Assert bcrypt.check_password_hash was called with correct arguments
                bcrypt.check_password_hash.assert_called_once_with('hashed_password', 'password123')
                # Assert jwt.encode was called to generate token
                jwt.encode.assert_called_once()

def test_login_invalid_credentials(client):
    # Mock db.session.query to return a mock user
    mock_user = MagicMock(spec=User)
    mock_user.password = 'hashed_password'

    with patch('db.session.query') as mock_query:
        mock_query.return_value.filter_by.return_value.first.return_value = mock_user
        
        # Mock bcrypt.check_password_hash to return False
        with patch('utils.auth.bcrypt.check_password_hash', return_value=False):
            # Send POST request to /auth/login with invalid credentials
            response = client.post('/auth/login', json={
                'email': 'test@example.com',
                'password': 'wrong_password'
            })

            # Assert response status code is 401
            assert response.status_code == 401
            # Assert response JSON contains error message
            assert 'error' in response.json

def test_logout(client):
    # Mock jwt.decode to return a valid token payload
    with patch('utils.auth.jwt.decode', return_value={'user_id': 1}):
        # Send POST request to /auth/logout with valid token
        response = client.post('/auth/logout', headers={'Authorization': 'Bearer valid_token'})

        # Assert response status code is 200
        assert response.status_code == 200
        # Assert response JSON confirms successful logout
        assert 'message' in response.json
        assert 'Successfully logged out' in response.json['message']

def test_refresh_token(client):
    # Mock jwt.decode to return a valid token payload
    with patch('utils.auth.jwt.decode', return_value={'user_id': 1}):
        # Mock jwt.encode to return a new mock token
        with patch('utils.auth.jwt.encode', return_value='new_mock_token'):
            # Send POST request to /auth/refresh with valid refresh token
            response = client.post('/auth/refresh', headers={'Authorization': 'Bearer valid_refresh_token'})

            # Assert response status code is 200
            assert response.status_code == 200
            # Assert response JSON contains new access token
            assert 'access_token' in response.json
            assert response.json['access_token'] == 'new_mock_token'
            # Assert jwt.encode was called to generate new token
            jwt.encode.assert_called_once()

def test_protected_route(client):
    # Mock jwt.decode to return a valid token payload
    with patch('utils.auth.jwt.decode', return_value={'user_id': 1}):
        # Send GET request to a protected route with valid token
        response = client.get('/api/protected', headers={'Authorization': 'Bearer valid_token'})

        # Assert response status code is 200
        assert response.status_code == 200
        # Assert response contains protected resource data
        assert 'data' in response.json
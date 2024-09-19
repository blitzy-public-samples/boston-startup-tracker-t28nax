import pytest
from flask import Flask
from unittest.mock import patch, MagicMock
from app import create_app
from db import db
from models.news_article import NewsArticle

@pytest.fixture
def client():
    # Create a Flask test client
    app = create_app('testing')
    
    # Set up application context
    with app.app_context():
        # Yield the test client
        yield app.test_client()
    
    # Tear down application context after tests

class TestNewsArticleRoutes:
    def test_get_news_articles(self, client):
        # Mock db.session.query to return a list of mock news articles
        mock_articles = [
            NewsArticle(id=1, title="Article 1", content="Content 1"),
            NewsArticle(id=2, title="Article 2", content="Content 2")
        ]
        with patch('db.session.query') as mock_query:
            mock_query.return_value.all.return_value = mock_articles

            # Send GET request to /news
            response = client.get('/news')

            # Assert response status code is 200
            assert response.status_code == 200

            # Assert response JSON contains expected news article data
            data = response.get_json()
            assert len(data) == 2
            assert data[0]['id'] == 1
            assert data[0]['title'] == "Article 1"
            assert data[1]['id'] == 2
            assert data[1]['title'] == "Article 2"

    def test_get_news_article(self, client):
        # Mock db.session.query.get to return a mock news article
        mock_article = NewsArticle(id=1, title="Test Article", content="Test Content")
        with patch('db.session.query') as mock_query:
            mock_query.return_value.get.return_value = mock_article

            # Send GET request to /news/1
            response = client.get('/news/1')

            # Assert response status code is 200
            assert response.status_code == 200

            # Assert response JSON contains expected news article data
            data = response.get_json()
            assert data['id'] == 1
            assert data['title'] == "Test Article"
            assert data['content'] == "Test Content"

    def test_create_news_article(self, client):
        # Mock db.session.add and db.session.commit
        with patch('db.session.add') as mock_add, patch('db.session.commit') as mock_commit:
            # Send POST request to /news with news article data
            response = client.post('/news', json={
                'title': 'New Article',
                'content': 'New Content'
            })

            # Assert response status code is 201
            assert response.status_code == 201

            # Assert response JSON contains created news article data
            data = response.get_json()
            assert data['title'] == 'New Article'
            assert data['content'] == 'New Content'

            # Assert db.session.add and db.session.commit were called
            mock_add.assert_called_once()
            mock_commit.assert_called_once()

    def test_update_news_article(self, client):
        # Mock db.session.query.get to return a mock news article
        mock_article = NewsArticle(id=1, title="Old Title", content="Old Content")
        with patch('db.session.query') as mock_query, patch('db.session.commit') as mock_commit:
            mock_query.return_value.get.return_value = mock_article

            # Send PUT request to /news/1 with updated data
            response = client.put('/news/1', json={
                'title': 'Updated Title',
                'content': 'Updated Content'
            })

            # Assert response status code is 200
            assert response.status_code == 200

            # Assert response JSON contains updated news article data
            data = response.get_json()
            assert data['id'] == 1
            assert data['title'] == 'Updated Title'
            assert data['content'] == 'Updated Content'

            # Assert mock news article object was updated with new data
            assert mock_article.title == 'Updated Title'
            assert mock_article.content == 'Updated Content'

            # Assert db.session.commit was called
            mock_commit.assert_called_once()

    def test_delete_news_article(self, client):
        # Mock db.session.query.get to return a mock news article
        mock_article = NewsArticle(id=1, title="Test Article", content="Test Content")
        with patch('db.session.query') as mock_query, \
             patch('db.session.delete') as mock_delete, \
             patch('db.session.commit') as mock_commit:
            mock_query.return_value.get.return_value = mock_article

            # Send DELETE request to /news/1
            response = client.delete('/news/1')

            # Assert response status code is 204
            assert response.status_code == 204

            # Assert db.session.delete was called with the mock news article
            mock_delete.assert_called_once_with(mock_article)

            # Assert db.session.commit was called
            mock_commit.assert_called_once()
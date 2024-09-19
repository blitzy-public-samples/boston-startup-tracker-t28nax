from flask import Blueprint, request, jsonify
from ..utils.db import db
from ..models.news_article import NewsArticle
from ..utils.auth import auth_required

news_routes = Blueprint('news', __name__)

@news_routes.route('/', methods=['GET'])
@auth_required
def get_news_articles():
    # Parse query parameters for filtering and pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    startup_id = request.args.get('startup_id', type=int)

    # Build the database query based on filters
    query = NewsArticle.query
    if startup_id:
        query = query.filter_by(startup_id=startup_id)

    # Execute the query with pagination
    pagination = query.order_by(NewsArticle.date_published.desc()).paginate(page=page, per_page=per_page)

    # Convert news article objects to dictionaries
    articles = [article.to_dict() for article in pagination.items]

    # Return JSON response with news articles and metadata
    return jsonify({
        'articles': articles,
        'total': pagination.total,
        'pages': pagination.pages,
        'page': page,
        'per_page': per_page
    })

@news_routes.route('/<int:article_id>', methods=['GET'])
@auth_required
def get_news_article(article_id):
    # Query the database for the news article with the given ID
    article = NewsArticle.query.get(article_id)

    # If news article not found, return 404 error
    if not article:
        return jsonify({'error': 'News article not found'}), 404

    # Convert news article object to dictionary
    article_data = article.to_dict()

    # Return JSON response with news article details
    return jsonify(article_data)

@news_routes.route('/', methods=['POST'])
@auth_required
def create_news_article():
    # Parse JSON data from request
    data = request.get_json()

    # Validate required fields
    required_fields = ['title', 'url', 'startup_id', 'date_published']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400

    # Create new NewsArticle object
    new_article = NewsArticle(
        title=data['title'],
        url=data['url'],
        startup_id=data['startup_id'],
        date_published=data['date_published'],
        summary=data.get('summary'),
        source=data.get('source')
    )

    # Add to database and commit
    db.session.add(new_article)
    db.session.commit()

    # Return JSON response with created news article details
    return jsonify(new_article.to_dict()), 201

@news_routes.route('/<int:article_id>', methods=['PUT'])
@auth_required
def update_news_article(article_id):
    # Query the database for the news article with the given ID
    article = NewsArticle.query.get(article_id)

    # If news article not found, return 404 error
    if not article:
        return jsonify({'error': 'News article not found'}), 404

    # Parse JSON data from request
    data = request.get_json()

    # Update news article object with new data
    for key, value in data.items():
        if hasattr(article, key):
            setattr(article, key, value)

    # Commit changes to database
    db.session.commit()

    # Return JSON response with updated news article details
    return jsonify(article.to_dict())

@news_routes.route('/<int:article_id>', methods=['DELETE'])
@auth_required
def delete_news_article(article_id):
    # Query the database for the news article with the given ID
    article = NewsArticle.query.get(article_id)

    # If news article not found, return 404 error
    if not article:
        return jsonify({'error': 'News article not found'}), 404

    # Delete news article from database
    db.session.delete(article)
    db.session.commit()

    # Return JSON response confirming deletion
    return jsonify({'message': 'News article deleted successfully'}), 200

# Human tasks:
# - Implement more advanced filtering options (e.g., by date range, source, startup)
# - Add sorting functionality (e.g., by date published, relevance)
# - Optimize query performance for large datasets
# - Add error handling for invalid news article IDs
# - Implement caching for frequently accessed news articles
# - Implement more robust input validation (e.g., check for valid startup_id, URL format)
# - Add support for automatic summarization of article content
# - Implement duplicate detection to avoid creating duplicate articles
# - Implement partial updates (PATCH) functionality
# - Add validation to prevent updates to read-only fields (e.g., creation date, original URL)
# - Implement soft delete functionality to maintain historical data
# - Add authorization check to ensure only admin users can delete news articles
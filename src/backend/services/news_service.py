from sqlalchemy import func
from ..utils import db
from ..models.news_article import NewsArticle
from ..models.startup import Startup

def get_news_articles(filters=None, page=1, per_page=20):
    # Create a base query for NewsArticle model
    query = db.session.query(NewsArticle)

    # Apply filters to the query if provided
    if filters:
        for key, value in filters.items():
            query = query.filter(getattr(NewsArticle, key) == value)

    # Calculate total count of matching news articles
    total_count = query.count()

    # Apply pagination to the query
    query = query.offset((page - 1) * per_page).limit(per_page)

    # Execute the query and return results along with total count
    return query.all(), total_count

def get_news_article_by_id(article_id):
    # Query the database for a NewsArticle with the given ID
    return db.session.query(NewsArticle).get(article_id)

def create_news_article(article_data):
    # Create a new NewsArticle object with the provided data
    new_article = NewsArticle(**article_data)

    # Add the new NewsArticle to the database session
    db.session.add(new_article)

    # Commit the changes to the database
    db.session.commit()

    # Return the created NewsArticle object
    return new_article

def update_news_article(article_id, article_data):
    # Query the database for the NewsArticle with the given ID
    article = db.session.query(NewsArticle).get(article_id)

    # If not found, raise an exception
    if not article:
        raise ValueError(f"News article with id {article_id} not found")

    # Update the NewsArticle object with the provided data
    for key, value in article_data.items():
        setattr(article, key, value)

    # Commit the changes to the database
    db.session.commit()

    # Return the updated NewsArticle object
    return article

def delete_news_article(article_id):
    # Query the database for the NewsArticle with the given ID
    article = db.session.query(NewsArticle).get(article_id)

    # If found, delete the NewsArticle from the database
    if article:
        db.session.delete(article)
        db.session.commit()
        return True
    
    # Return False if not found
    return False

def get_news_articles_by_startup(startup_id, page=1, per_page=20):
    # Create a query for NewsArticle objects associated with the given startup_id
    query = db.session.query(NewsArticle).filter(NewsArticle.startup_id == startup_id)

    # Calculate total count of matching news articles
    total_count = query.count()

    # Apply pagination to the query
    query = query.offset((page - 1) * per_page).limit(per_page)

    # Execute the query and return results along with total count
    return query.all(), total_count

def search_news_articles(query, page=1, per_page=20):
    # Create a base query for NewsArticle model
    base_query = db.session.query(NewsArticle)

    # Apply full-text search filter based on the query
    search_query = base_query.filter(
        NewsArticle.title.ilike(f"%{query}%") |
        NewsArticle.content.ilike(f"%{query}%")
    )

    # Calculate total count of matching news articles
    total_count = search_query.count()

    # Apply pagination to the query
    search_query = search_query.offset((page - 1) * per_page).limit(per_page)

    # Execute the query and return results along with total count
    return search_query.all(), total_count

# Human tasks:
# TODO: Implement more advanced filtering options (e.g., by date range, source, startup)
# TODO: Add sorting functionality (e.g., by date published, relevance)
# TODO: Optimize query performance for large datasets
# TODO: Add caching mechanism for frequently accessed news articles
# TODO: Implement data validation for news article creation
# TODO: Add support for automatic summarization of article content
# TODO: Implement duplicate detection to avoid creating duplicate articles
# TODO: Implement partial update functionality
# TODO: Add validation to prevent updates to read-only fields (e.g., original URL, publication date)
# TODO: Implement soft delete functionality to maintain historical data
# TODO: Add authorization check to ensure only admin users can delete news articles
# TODO: Add sorting options (e.g., by date published, relevance)
# TODO: Implement filtering options (e.g., by source, keywords)
# TODO: Implement full-text search functionality
# TODO: Add support for advanced search operators (e.g., AND, OR, NOT)
# TODO: Implement relevance scoring for search results
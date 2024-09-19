from ..utils import db
from ..models.startup import Startup
from ..models.funding_round import FundingRound
from ..models.job_posting import JobPosting
from ..models.news_article import NewsArticle
import sqlalchemy

def get_startups(filters=None, page=1, per_page=20):
    # Create a base query for Startup model
    query = db.session.query(Startup)

    # Apply filters to the query if provided
    if filters:
        for key, value in filters.items():
            query = query.filter(getattr(Startup, key) == value)

    # Calculate total count of matching startups
    total_count = query.count()

    # Apply pagination to the query
    query = query.offset((page - 1) * per_page).limit(per_page)

    # Execute the query and return results along with total count
    return query.all(), total_count

def get_startup_by_id(startup_id):
    # Query the database for a Startup with the given ID
    return db.session.query(Startup).get(startup_id)

def create_startup(startup_data):
    # Create a new Startup object with the provided data
    new_startup = Startup(**startup_data)

    # Add the new Startup to the database session
    db.session.add(new_startup)

    # Commit the changes to the database
    db.session.commit()

    # Return the created Startup object
    return new_startup

def update_startup(startup_id, startup_data):
    # Query the database for the Startup with the given ID
    startup = db.session.query(Startup).get(startup_id)

    # If not found, raise an exception
    if not startup:
        raise ValueError(f"Startup with id {startup_id} not found")

    # Update the Startup object with the provided data
    for key, value in startup_data.items():
        setattr(startup, key, value)

    # Commit the changes to the database
    db.session.commit()

    # Return the updated Startup object
    return startup

def delete_startup(startup_id):
    # Query the database for the Startup with the given ID
    startup = db.session.query(Startup).get(startup_id)

    # If found, delete the Startup from the database
    if startup:
        db.session.delete(startup)
        db.session.commit()
        return True
    
    return False

def get_startup_funding_rounds(startup_id):
    # Query the database for FundingRound objects associated with the given startup_id
    return db.session.query(FundingRound).filter(FundingRound.startup_id == startup_id).all()

def get_startup_job_postings(startup_id):
    # Query the database for JobPosting objects associated with the given startup_id
    return db.session.query(JobPosting).filter(JobPosting.startup_id == startup_id).all()

def get_startup_news_articles(startup_id):
    # Query the database for NewsArticle objects associated with the given startup_id
    return db.session.query(NewsArticle).filter(NewsArticle.startup_id == startup_id).all()

# Human tasks:
# - Implement more advanced filtering options
# - Add sorting functionality
# - Optimize query performance for large datasets
# - Add caching mechanism for frequently accessed startups
# - Implement data validation for startup creation
# - Add support for creating related entities (e.g., founders) in the same transaction
# - Implement partial update functionality
# - Add validation to prevent updates to read-only fields
# - Implement soft delete functionality
# - Add cascading delete for related entities
# - Add pagination support for startups with many funding rounds
# - Implement sorting options (e.g., by date, amount) for funding rounds
# - Add pagination support for startups with many job postings
# - Implement filtering options (e.g., by department, experience level) for job postings
# - Add pagination support for startups with many news articles
# - Implement sorting options (e.g., by date, relevance) for news articles
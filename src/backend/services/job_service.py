from ..utils import db
from ..models.job_posting import JobPosting
from ..models.startup import Startup
from sqlalchemy import or_

def get_job_postings(filters=None, page=1, per_page=20):
    # Create a base query for JobPosting model
    query = JobPosting.query

    # Apply filters to the query if provided
    if filters:
        if 'startup_id' in filters:
            query = query.filter(JobPosting.startup_id == filters['startup_id'])
        if 'job_type' in filters:
            query = query.filter(JobPosting.job_type == filters['job_type'])
        # Add more filters as needed

    # Calculate total count of matching job postings
    total_count = query.count()

    # Apply pagination to the query
    query = query.offset((page - 1) * per_page).limit(per_page)

    # Execute the query and return results along with total count
    return query.all(), total_count

def get_job_posting_by_id(job_posting_id):
    # Query the database for a JobPosting with the given ID
    return JobPosting.query.get(job_posting_id)

def create_job_posting(job_posting_data):
    # Create a new JobPosting object with the provided data
    new_job_posting = JobPosting(**job_posting_data)

    # Add the new JobPosting to the database session
    db.session.add(new_job_posting)

    # Commit the changes to the database
    db.session.commit()

    # Return the created JobPosting object
    return new_job_posting

def update_job_posting(job_posting_id, job_posting_data):
    # Query the database for the JobPosting with the given ID
    job_posting = JobPosting.query.get(job_posting_id)

    # If not found, raise an exception
    if not job_posting:
        raise ValueError(f"Job posting with id {job_posting_id} not found")

    # Update the JobPosting object with the provided data
    for key, value in job_posting_data.items():
        setattr(job_posting, key, value)

    # Commit the changes to the database
    db.session.commit()

    # Return the updated JobPosting object
    return job_posting

def delete_job_posting(job_posting_id):
    # Query the database for the JobPosting with the given ID
    job_posting = JobPosting.query.get(job_posting_id)

    # If found, delete the JobPosting from the database
    if job_posting:
        db.session.delete(job_posting)
        db.session.commit()
        return True
    
    # Return False if not found
    return False

def get_job_postings_by_startup(startup_id):
    # Query the database for JobPosting objects associated with the given startup_id
    return JobPosting.query.filter_by(startup_id=startup_id).all()

def search_job_postings(query, page=1, per_page=20):
    # Create a base query for JobPosting model
    base_query = JobPosting.query

    # Apply full-text search filter based on the query
    search_filter = or_(
        JobPosting.title.ilike(f"%{query}%"),
        JobPosting.description.ilike(f"%{query}%"),
        JobPosting.requirements.ilike(f"%{query}%")
    )
    filtered_query = base_query.filter(search_filter)

    # Calculate total count of matching job postings
    total_count = filtered_query.count()

    # Apply pagination to the query
    paginated_query = filtered_query.offset((page - 1) * per_page).limit(per_page)

    # Execute the query and return results along with total count
    return paginated_query.all(), total_count

# Human tasks:
# - Implement more advanced filtering options (e.g., by skills, experience level, salary range)
# - Add sorting functionality (e.g., by date posted, relevance)
# - Optimize query performance for large datasets
# - Add caching mechanism for frequently accessed job postings
# - Implement data validation for job posting creation
# - Add support for creating related entities (e.g., required skills) in the same transaction
# - Implement partial update functionality
# - Add validation to prevent updates to read-only fields
# - Implement soft delete functionality
# - Add authorization check to ensure only the posting startup or admin can delete
# - Add pagination support for startups with many job postings
# - Implement sorting options (e.g., by date posted, job title)
# - Implement full-text search functionality
# - Add support for advanced search operators (e.g., AND, OR, NOT)
# - Implement relevance scoring for search results
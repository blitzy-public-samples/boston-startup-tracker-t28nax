from flask import Blueprint, request, jsonify
from ..utils.db import db
from ..models.job_posting import JobPosting
from ..utils.auth import auth_required

job_routes = Blueprint('job', __name__)

@job_routes.route('/', methods=['GET'])
@auth_required
def get_job_postings():
    # Parse query parameters for filtering and pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    startup_id = request.args.get('startup_id', type=int)
    
    # Build the database query based on filters
    query = JobPosting.query
    if startup_id:
        query = query.filter_by(startup_id=startup_id)
    
    # Execute the query with pagination
    paginated_jobs = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Convert job posting objects to dictionaries
    jobs = [job.to_dict() for job in paginated_jobs.items]
    
    # Return JSON response with job postings and metadata
    return jsonify({
        'jobs': jobs,
        'total': paginated_jobs.total,
        'pages': paginated_jobs.pages,
        'page': page,
        'per_page': per_page
    })

@job_routes.route('/<int:job_id>', methods=['GET'])
@auth_required
def get_job_posting(job_id):
    # Query the database for the job posting with the given ID
    job = JobPosting.query.get(job_id)
    
    # If job posting not found, return 404 error
    if not job:
        return jsonify({'error': 'Job posting not found'}), 404
    
    # Convert job posting object to dictionary
    job_dict = job.to_dict()
    
    # Return JSON response with job posting details
    return jsonify(job_dict)

@job_routes.route('/', methods=['POST'])
@auth_required
def create_job_posting():
    # Parse JSON data from request
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['title', 'description', 'startup_id', 'salary_range']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Create new JobPosting object
    new_job = JobPosting(
        title=data['title'],
        description=data['description'],
        startup_id=data['startup_id'],
        salary_range=data['salary_range']
    )
    
    # Add to database and commit
    db.session.add(new_job)
    db.session.commit()
    
    # Return JSON response with created job posting details
    return jsonify(new_job.to_dict()), 201

@job_routes.route('/<int:job_id>', methods=['PUT'])
@auth_required
def update_job_posting(job_id):
    # Query the database for the job posting with the given ID
    job = JobPosting.query.get(job_id)
    
    # If job posting not found, return 404 error
    if not job:
        return jsonify({'error': 'Job posting not found'}), 404
    
    # Parse JSON data from request
    data = request.get_json()
    
    # Update job posting object with new data
    for key, value in data.items():
        if hasattr(job, key):
            setattr(job, key, value)
    
    # Commit changes to database
    db.session.commit()
    
    # Return JSON response with updated job posting details
    return jsonify(job.to_dict())

@job_routes.route('/<int:job_id>', methods=['DELETE'])
@auth_required
def delete_job_posting(job_id):
    # Query the database for the job posting with the given ID
    job = JobPosting.query.get(job_id)
    
    # If job posting not found, return 404 error
    if not job:
        return jsonify({'error': 'Job posting not found'}), 404
    
    # Delete job posting from database
    db.session.delete(job)
    db.session.commit()
    
    # Return JSON response confirming deletion
    return jsonify({'message': 'Job posting deleted successfully'}), 200

# Human tasks:
# - Implement more advanced filtering options (e.g., by skills, experience level)
# - Add sorting functionality (e.g., by date posted, salary range)
# - Optimize query performance for large datasets
# - Add error handling for invalid job posting IDs
# - Implement caching for frequently accessed job postings
# - Implement more robust input validation (e.g., check for valid startup_id)
# - Add support for creating job postings with associated skills or requirements
# - Implement partial updates (PATCH) functionality
# - Add validation to prevent updates to read-only fields (e.g., creation date)
# - Implement soft delete functionality to maintain historical data
# - Add authorization check to ensure only the posting startup or admin can delete
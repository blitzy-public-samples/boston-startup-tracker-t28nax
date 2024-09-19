from flask import Blueprint, request, jsonify
from ..utils.db import db
from ..models.startup import Startup
from ..utils.auth import auth_required

startup_routes = Blueprint('startup', __name__)

@startup_routes.route('/', methods=['GET'])
@auth_required
def get_startups():
    # Parse query parameters for filtering and pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    name = request.args.get('name')
    industry = request.args.get('industry')

    # Build the database query based on filters
    query = Startup.query
    if name:
        query = query.filter(Startup.name.ilike(f'%{name}%'))
    if industry:
        query = query.filter(Startup.industry == industry)

    # Execute the query with pagination
    paginated_startups = query.paginate(page=page, per_page=per_page, error_out=False)

    # Convert startup objects to dictionaries
    startups = [startup.to_dict() for startup in paginated_startups.items]

    # Return JSON response with startups and metadata
    return jsonify({
        'startups': startups,
        'total': paginated_startups.total,
        'pages': paginated_startups.pages,
        'page': page,
        'per_page': per_page
    })

@startup_routes.route('/<int:startup_id>', methods=['GET'])
@auth_required
def get_startup(startup_id):
    # Query the database for the startup with the given ID
    startup = Startup.query.get(startup_id)

    # If startup not found, return 404 error
    if not startup:
        return jsonify({'error': 'Startup not found'}), 404

    # Convert startup object to dictionary
    startup_data = startup.to_dict()

    # Return JSON response with startup details
    return jsonify(startup_data)

@startup_routes.route('/', methods=['POST'])
@auth_required
def create_startup():
    # Parse JSON data from request
    data = request.get_json()

    # Validate required fields
    required_fields = ['name', 'industry', 'description']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400

    # Create new Startup object
    new_startup = Startup(
        name=data['name'],
        industry=data['industry'],
        description=data['description'],
        # Add other fields as necessary
    )

    # Add to database and commit
    db.session.add(new_startup)
    db.session.commit()

    # Return JSON response with created startup details
    return jsonify(new_startup.to_dict()), 201

@startup_routes.route('/<int:startup_id>', methods=['PUT'])
@auth_required
def update_startup(startup_id):
    # Query the database for the startup with the given ID
    startup = Startup.query.get(startup_id)

    # If startup not found, return 404 error
    if not startup:
        return jsonify({'error': 'Startup not found'}), 404

    # Parse JSON data from request
    data = request.get_json()

    # Update startup object with new data
    for key, value in data.items():
        if hasattr(startup, key):
            setattr(startup, key, value)

    # Commit changes to database
    db.session.commit()

    # Return JSON response with updated startup details
    return jsonify(startup.to_dict())

@startup_routes.route('/<int:startup_id>', methods=['DELETE'])
@auth_required
def delete_startup(startup_id):
    # Query the database for the startup with the given ID
    startup = Startup.query.get(startup_id)

    # If startup not found, return 404 error
    if not startup:
        return jsonify({'error': 'Startup not found'}), 404

    # Delete startup from database
    db.session.delete(startup)
    db.session.commit()

    # Return JSON response confirming deletion
    return jsonify({'message': 'Startup deleted successfully'}), 200

# Human tasks:
# - Implement more advanced filtering options
# - Add sorting functionality
# - Optimize query performance for large datasets
# - Add error handling for invalid startup IDs
# - Implement caching for frequently accessed startups
# - Implement more robust input validation
# - Add support for creating related entities (e.g., founders, funding rounds)
# - Implement partial updates (PATCH) functionality
# - Add validation to prevent updates to read-only fields
# - Implement soft delete functionality
# - Add cascading delete for related entities
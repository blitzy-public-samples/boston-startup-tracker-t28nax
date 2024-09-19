from flask import Blueprint, request, jsonify
from ..utils.db import db
from ..models.investor import Investor
from ..utils.auth import auth_required

investor_routes = Blueprint('investor', __name__)

@investor_routes.route('/', methods=['GET'])
@auth_required
def get_investors():
    # Parse query parameters for filtering and pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    name_filter = request.args.get('name', '')

    # Build the database query based on filters
    query = Investor.query
    if name_filter:
        query = query.filter(Investor.name.ilike(f'%{name_filter}%'))

    # Execute the query with pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    investors = pagination.items

    # Convert investor objects to dictionaries
    investor_list = [investor.to_dict() for investor in investors]

    # Return JSON response with investors and metadata
    return jsonify({
        'investors': investor_list,
        'total': pagination.total,
        'pages': pagination.pages,
        'page': page,
        'per_page': per_page
    })

@investor_routes.route('/<int:investor_id>', methods=['GET'])
@auth_required
def get_investor(investor_id):
    # Query the database for the investor with the given ID
    investor = Investor.query.get(investor_id)

    # If investor not found, return 404 error
    if not investor:
        return jsonify({'error': 'Investor not found'}), 404

    # Convert investor object to dictionary
    investor_data = investor.to_dict()

    # Return JSON response with investor details
    return jsonify(investor_data)

@investor_routes.route('/', methods=['POST'])
@auth_required
def create_investor():
    # Parse JSON data from request
    data = request.get_json()

    # Validate required fields
    required_fields = ['name', 'email', 'investment_focus']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400

    # Create new Investor object
    new_investor = Investor(
        name=data['name'],
        email=data['email'],
        investment_focus=data['investment_focus'],
        website=data.get('website'),
        linkedin=data.get('linkedin')
    )

    # Add to database and commit
    db.session.add(new_investor)
    db.session.commit()

    # Return JSON response with created investor details
    return jsonify(new_investor.to_dict()), 201

@investor_routes.route('/<int:investor_id>', methods=['PUT'])
@auth_required
def update_investor(investor_id):
    # Query the database for the investor with the given ID
    investor = Investor.query.get(investor_id)

    # If investor not found, return 404 error
    if not investor:
        return jsonify({'error': 'Investor not found'}), 404

    # Parse JSON data from request
    data = request.get_json()

    # Update investor object with new data
    for key, value in data.items():
        if hasattr(investor, key):
            setattr(investor, key, value)

    # Commit changes to database
    db.session.commit()

    # Return JSON response with updated investor details
    return jsonify(investor.to_dict())

@investor_routes.route('/<int:investor_id>', methods=['DELETE'])
@auth_required
def delete_investor(investor_id):
    # Query the database for the investor with the given ID
    investor = Investor.query.get(investor_id)

    # If investor not found, return 404 error
    if not investor:
        return jsonify({'error': 'Investor not found'}), 404

    # Delete investor from database
    db.session.delete(investor)

    # Commit changes
    db.session.commit()

    # Return JSON response confirming deletion
    return jsonify({'message': 'Investor deleted successfully'}), 200

# Human tasks:
# - Implement more advanced filtering options
# - Add sorting functionality
# - Optimize query performance for large datasets
# - Add error handling for invalid investor IDs
# - Implement caching for frequently accessed investors
# - Implement more robust input validation
# - Add support for creating related entities (e.g., investment history)
# - Implement partial updates (PATCH) functionality
# - Add validation to prevent updates to read-only fields
# - Implement soft delete functionality
# - Add cascading delete for related entities
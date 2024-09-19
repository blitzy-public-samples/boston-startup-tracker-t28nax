from flask import Blueprint, request, jsonify
from ..utils.db import db
from ..models.user import User
from ..utils.auth import auth_required

user_routes = Blueprint('user', __name__)

@user_routes.route('/', methods=['GET'])
@auth_required
def get_users():
    # Parse query parameters for filtering and pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Build the database query based on filters
    query = User.query
    
    # Execute the query with pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Convert user objects to dictionaries
    users = [user.to_dict() for user in pagination.items]
    
    # Return JSON response with users and metadata
    return jsonify({
        'users': users,
        'total': pagination.total,
        'pages': pagination.pages,
        'page': page,
        'per_page': per_page
    })

@user_routes.route('/<int:user_id>', methods=['GET'])
@auth_required
def get_user(user_id):
    # Query the database for the user with the given ID
    user = User.query.get(user_id)
    
    # If user not found, return 404 error
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Convert user object to dictionary
    user_data = user.to_dict()
    
    # Return JSON response with user details
    return jsonify(user_data)

@user_routes.route('/', methods=['POST'])
def create_user():
    # Parse JSON data from request
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['email', 'password', 'name']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Check if email already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    # Create new User object
    new_user = User(
        email=data['email'],
        name=data['name']
    )
    
    # Set password hash
    new_user.set_password(data['password'])
    
    # Add to database and commit
    db.session.add(new_user)
    db.session.commit()
    
    # Return JSON response with created user details
    return jsonify(new_user.to_dict()), 201

@user_routes.route('/<int:user_id>', methods=['PUT'])
@auth_required
def update_user(user_id):
    # Query the database for the user with the given ID
    user = User.query.get(user_id)
    
    # If user not found, return 404 error
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Parse JSON data from request
    data = request.get_json()
    
    # Update user object with new data
    if 'name' in data:
        user.name = data['name']
    if 'email' in data:
        user.email = data['email']
    
    # If password is being updated, set new password hash
    if 'password' in data:
        user.set_password(data['password'])
    
    # Commit changes to database
    db.session.commit()
    
    # Return JSON response with updated user details
    return jsonify(user.to_dict())

@user_routes.route('/<int:user_id>', methods=['DELETE'])
@auth_required
def delete_user(user_id):
    # Query the database for the user with the given ID
    user = User.query.get(user_id)
    
    # If user not found, return 404 error
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Delete user from database
    db.session.delete(user)
    
    # Commit changes
    db.session.commit()
    
    # Return JSON response confirming deletion
    return jsonify({'message': 'User deleted successfully'})

# Human tasks:
# - Implement more advanced filtering options (e.g., by role, registration date)
# - Add sorting functionality
# - Implement access control to restrict this endpoint to admin users only
# - Add error handling for invalid user IDs
# - Implement access control to allow users to view only their own profile or admin access
# - Implement more robust input validation (e.g., password strength, email format)
# - Add email verification process
# - Implement rate limiting to prevent abuse
# - Implement partial updates (PATCH) functionality
# - Add validation to prevent updates to read-only fields (e.g., email)
# - Implement access control to allow users to update only their own profile or admin access
# - Implement soft delete functionality to maintain historical data
# - Add authorization check to ensure only admin users can delete other users
# - Implement a process for users to delete their own accounts
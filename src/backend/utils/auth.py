from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from functools import wraps
from flask import jsonify
from ..models.user import User

def auth_required(func):
    @wraps(func)
    @jwt_required()
    def wrapper(*args, **kwargs):
        try:
            # Execute the original function
            return func(*args, **kwargs)
        except Exception as e:
            # If a JWT exception occurs, return an error response
            return jsonify({"error": "Authentication required"}), 401
    return wrapper

def get_current_user():
    # Get the user ID from the JWT token
    user_id = get_jwt_identity()
    
    # Query the database for the User with the given ID
    user = User.query.get(user_id)
    
    # Return the User object if found, otherwise return None
    return user

def generate_token(user):
    # Create a JWT token with the user's ID as the identity
    token = create_access_token(identity=user.id)
    
    # Return the generated token
    return token

# Human tasks:
# TODO: Implement role-based access control
# TODO: Add logging for authentication failures
# TODO: Implement token refresh mechanism
# TODO: Implement caching for frequent user lookups
# TODO: Add error handling for database query failures
# TODO: Implement token expiration and refresh mechanism
# TODO: Add additional claims to the token (e.g., user role)
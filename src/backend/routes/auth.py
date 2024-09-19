from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from ..utils.db import db
from ..models.user import User
from ..utils.auth import auth_required

# Create a Blueprint for authentication routes
auth_routes = Blueprint('auth', __name__)

@auth_routes.route('/login', methods=['POST'])
def login():
    # Parse JSON data from request
    data = request.get_json()

    # Validate required fields (email and password)
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({"error": "Email and password are required"}), 400

    # Query the database for the user with the given email
    user = User.query.filter_by(email=data['email']).first()

    # If user not found or password is incorrect, return 401 error
    if not user or not user.check_password(data['password']):
        return jsonify({"error": "Invalid email or password"}), 401

    # Create access and refresh tokens
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    # Update user's last_login timestamp
    user.update_last_login()

    # Commit changes to database
    db.session.commit()

    # Return JSON response with tokens and user details
    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": user.to_dict()
    }), 200

@auth_routes.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    # Get the user identity from the refresh token
    current_user = get_jwt_identity()

    # Create a new access token
    new_access_token = create_access_token(identity=current_user)

    # Return JSON response with the new access token
    return jsonify({"access_token": new_access_token}), 200

@auth_routes.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    # Add the current token to a blacklist or revoke it
    # Note: Implementation of token blacklisting is not provided in this code
    # It should be implemented as per the application's requirements

    # Return JSON response confirming logout
    return jsonify({"message": "Successfully logged out"}), 200

@auth_routes.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    # Get the user identity from the access token
    current_user_id = get_jwt_identity()

    # Parse JSON data from request
    data = request.get_json()

    # Validate required fields (current_password and new_password)
    if not data or 'current_password' not in data or 'new_password' not in data:
        return jsonify({"error": "Current password and new password are required"}), 400

    # Query the database for the user
    user = User.query.get(current_user_id)

    # Verify the current password
    if not user.check_password(data['current_password']):
        return jsonify({"error": "Current password is incorrect"}), 400

    # Update the user's password
    user.set_password(data['new_password'])

    # Commit changes to database
    db.session.commit()

    # Return JSON response confirming password change
    return jsonify({"message": "Password successfully changed"}), 200

# Human tasks:
# TODO: Implement rate limiting to prevent brute force attacks
# TODO: Add two-factor authentication option
# TODO: Implement account lockout after multiple failed attempts
# TODO: Implement refresh token rotation for enhanced security
# TODO: Add logging for token refresh events
# TODO: Implement token blacklisting or revocation mechanism
# TODO: Add logging for logout events
# TODO: Implement password strength validation
# TODO: Add option to invalidate all existing tokens on password change
# TODO: Send email notification for password change